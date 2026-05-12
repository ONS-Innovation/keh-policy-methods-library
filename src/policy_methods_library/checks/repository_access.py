"""This module contains a check for repository access permissions. It is recommended that access is given to a team rather than individual users."""

from policy_methods_library.github.clients import GitHubRestClient

# Note: A data passthrough is not included for this check since it is unlikely that the necessary data (list of collaborators with their types) would be available without making an API call.


def check_repository_access(
    client: GitHubRestClient,
    repository_name: str,
) -> dict:
    """Check if a repository has any individual users with access instead of a team.

    Args:
        client: An instance of the GitHubRestClient to use for API calls.
        repository_name: The name of the repository to check.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error), 'message', and 'details'.
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

    try:
        response = client.make_request(
            "GET",
            f"/repos/{client.owner}/{repository_name}/collaborators?affiliation=direct",
        )

        collaborators = response.json()

        # Verify that the API response contains a list of collaborators
        if not isinstance(collaborators, list):
            return {
                "result": "error",
                "message": "API response does not contain a list of collaborators.",
                "details": {"response": collaborators},
            }

        individual_collaborators = [
            {
                "login": collaborator.get("login"),
                "permissions": collaborator.get("permissions"),
            }
            for collaborator in collaborators
            if collaborator.get("type") == "User"
        ]

        if individual_collaborators:
            return {
                "result": "fail",
                "message": f"Repository '{repository_name}' has individual users with access. It is recommended to use teams for access management.",
                "details": {
                    "repository_name": repository_name,
                    "individual_collaborators": individual_collaborators,
                },
            }
        else:
            return {
                "result": "pass",
                "message": f"Repository '{repository_name}' does not have any individual users with access.",
                "details": {
                    "repository_name": repository_name,
                    "individual_collaborators": individual_collaborators,
                },
            }

    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while checking repository access: {str(e)}",
            "details": {},
        }
