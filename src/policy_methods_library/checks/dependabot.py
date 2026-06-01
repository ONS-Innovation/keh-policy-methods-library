"""This module contains a check to verify that Dependabot is enabled for repositories."""

from policy_methods_library.github.clients import GitHubRestClient


def check_dependabot(
    client: GitHubRestClient,
    repository_name: str,
) -> dict:
    """Check if Dependabot automated security fixes are enabled for a repository.

    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required.
        repository_name: The name of the repository to check. Required.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error), 'message', and 'details'.
        Details contains the 'enabled' status.
    """

    if client is None:
        return {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    if repository_name is None:
        return {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    try:
        response = client.make_request(
            "GET",
            f"/repos/{client.owner}/{repository_name}/automated-security-fixes",
        )

        response_data = response.json()
        enabled = response_data.get("enabled")

        if enabled is None:
            return {
                "result": "error",
                "message": "API response does not contain 'enabled' field.",
                "details": {"response": response_data},
            }
    except Exception as e:
        return {
            "result": "error",
            "message": f"Error fetching automated security fixes data: {str(e)}",
            "details": {},
        }

    if not isinstance(enabled, bool):
        return {
            "result": "error",
            "message": "Invalid type for 'enabled'. Expected boolean.",
            "details": {"enabled": enabled},
        }

    if enabled:
        return {
            "result": "pass",
            "message": f"Dependabot automated security fixes are enabled for {repository_name} repository.",
            "details": {"enabled": enabled},
        }
    else:
        return {
            "result": "fail",
            "message": f"Dependabot automated security fixes are not enabled for {repository_name} repository.",
            "details": {"enabled": enabled},
        }
