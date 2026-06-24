"""This module contains a check to ensure repositories do not have external pull requests."""

from requests import HTTPError

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.organisation import verify_client_organisation
from policy_methods_library.utils.pagination import get_paginated_list


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

    organisation_check_result = verify_client_organisation(client=client)
    if organisation_check_result is not None:
        return organisation_check_result

    initial_endpoint = (
        f"/repos/{client.owner}/{repository_name}/pulls?state=open&per_page=100"
    )

    pull_requests = get_paginated_list(
        client,
        initial_endpoint=initial_endpoint,
        list_name="pull requests",
    )

    if isinstance(pull_requests, dict) and "error" in pull_requests:
        if "response" in pull_requests:
            return {
                "result": "error",
                "message": pull_requests["error"],
                "details": {"response": pull_requests["response"]},
            }

        return {
            "result": "error",
            "message": f"An error occurred while retrieving pull requests: {pull_requests['error']}",
            "details": {},
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
