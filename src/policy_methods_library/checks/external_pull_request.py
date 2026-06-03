"""This module contains a check to ensure repositories do not have external pull requests."""

from requests import HTTPError

from policy_methods_library.github.clients import GitHubRestClient


def _is_organisation_member(client: GitHubRestClient, username: str) -> bool:
    """Return whether the user is a member of the configured organisation.

    Args:
        client: An instance of the GitHubRestClient to use for API calls.
        username: The GitHub username to check membership for.

    Returns:
        True if the user is a member of the organisation; otherwise False.

    Raises:
        HTTPError: Raised for unexpected status codes from the membership endpoint.
    """
    try:
        response = client.make_request(
            "GET",
            f"/orgs/{client.owner}/members/{username}",
            allow_redirects=False,
        )
    except HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return False
        raise

    if response.status_code == 204:
        return True

    # Any other status means the membership check did not complete in the
    # expected authenticated context (for example 302 if requester is not an
    # organisation member).
    raise HTTPError(
        f"Unexpected membership response status code: {response.status_code}",
        response=response,
    )


def _verify_client_organisation(client: GitHubRestClient) -> dict | None:
    """Validate that the client owner resolves to an organisation account.

    Args:
        client: An instance of the GitHubRestClient to validate.

    Returns:
        A standard error result dictionary when validation fails, otherwise None.
    """
    try:
        response = client.make_request("GET", f"/orgs/{client.owner}")
        organisation_data = response.json()
    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while verifying organisation authentication: {str(e)}",
            "details": {},
        }

    if not isinstance(organisation_data, dict):
        return {
            "result": "error",
            "message": "API response does not contain organisation data.",
            "details": {"response": organisation_data},
        }

    if organisation_data.get("type") != "Organization":
        return {
            "result": "error",
            "message": "Client is not authenticated as an organisation.",
            "details": {"organisation": organisation_data},
        }

    return None


def check_external_pull_request(
    client: GitHubRestClient,
    repository_name: str,
) -> dict:
    """Check that all open pull requests are authored by organisation members.

    Args:
        client: An instance of the GitHubRestClient to use for API calls.
        repository_name: The name of the repository to check.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error),
        'message', and 'details'.
    """

    if client is None:
        return {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    if not repository_name:
        return {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    organisation_check_result = _verify_client_organisation(client=client)
    if organisation_check_result is not None:
        return organisation_check_result

    pull_requests = []
    next_page_url = (
        f"/repos/{client.owner}/{repository_name}/pulls?state=open&per_page=100"
    )
    has_next_page = True

    try:
        while has_next_page:
            response = client.make_request(
                "GET",
                next_page_url,
            )
            response_pull_requests = response.json()

            if isinstance(response_pull_requests, list):
                pull_requests.extend(response_pull_requests)
            else:
                return {
                    "result": "error",
                    "message": "API response does not contain a list of pull requests.",
                    "details": {"response": response_pull_requests},
                }

            if response.links and "next" in response.links:
                next_page_url = response.links["next"]["url"].replace(
                    "https://api.github.com", ""
                )
            else:
                has_next_page = False

    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while retrieving pull requests: {str(e)}",
            "details": {},
        }

    if not isinstance(pull_requests, list):
        return {
            "result": "error",
            "message": "API response does not contain a list of pull requests.",
            "details": {"response": pull_requests},
        }

    external_pull_requests = []

    try:
        for pull_request in pull_requests:
            user = pull_request.get("user")
            username = user.get("login") if isinstance(user, dict) else None

            if not username:
                return {
                    "result": "error",
                    "message": "Pull request data is missing author username.",
                    "details": {"pull_request": pull_request},
                }

            # Allow dependabot[bot] as an exception since it is commonly used for automated dependency updates.
            if username == "dependabot[bot]":
                continue

            if not _is_organisation_member(client=client, username=username):
                external_pull_requests.append(
                    {
                        "number": pull_request.get("number"),
                        "title": pull_request.get("title"),
                        "author": username,
                    }
                )
    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while checking pull request authors: {str(e)}",
            "details": {},
        }

    if external_pull_requests:
        return {
            "result": "fail",
            "message": f"Repository '{repository_name}' has external pull requests authored by non-organisation members.",
            "details": {
                "repository_name": repository_name,
                "open_pull_request_count": len(pull_requests),
                "external_pull_requests": external_pull_requests,
            },
        }

    return {
        "result": "pass",
        "message": f"Repository '{repository_name}' has no external pull requests.",
        "details": {
            "repository_name": repository_name,
            "open_pull_request_count": len(pull_requests),
            "external_pull_requests": external_pull_requests,
        },
    }
