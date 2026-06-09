"""This module contains a check to verify that branch protection is enabled"""

from policy_methods_library.github.clients import GitHubRestClient


def check_branch_protection(
    client: GitHubRestClient,
    repository_name: str,
) -> dict:
    """Check if a GitHub repository has branch protection enabled.

    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required.
        repository_name: The name of the repository to check. Required if data is not provided. Defaults to None.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error), 'message', and 'details'.
        Details contains the 'team_slug', 'maintainer_count', and 'maintainers' list.
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
            "message": "Repository name is required if data is not provided.",
            "details": {},
        }

    try:
        response = client.make_request(
            "GET",
            f"/repos/{client.owner}/{repository_name}/branches/main/protection",
        )

        protection = response.json()

        if protection.get("status") == 404:
            return {
                "result": "fail",
                "message": f"Branch protection is not enabled for the 'main' branch of repository '{repository_name}'.",
                "details": {},
            }
        else:
            return {
                "result": "pass",
                "message": f"Branch protection is enabled for the 'main' branch of repository '{repository_name}'.",
                "details": {
                    "required_status_checks": protection.get("required_status_checks"),
                    "enforce_admins": protection.get("enforce_admins", {}).get(
                        "enabled", False
                    ),
                    "required_pull_request_reviews": protection.get(
                        "required_pull_request_reviews"
                    ),
                    "restrictions": protection.get("restrictions"),
                },
            }

    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while checking repository access: {str(e)}",
            "details": {},
        }
