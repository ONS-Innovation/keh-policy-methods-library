from policy_methods_library.github.clients import GitHubRestClient


def get_repo_details(github_client: GitHubRestClient, repository_name: str) -> dict:
    """
    Args:
            github_client (GitHubRestClient): The GitHub REST client to use for making requests.
            repository_name (str): The name of the repository for which to retrieve details.

    Returns:
            dict: A dictionary containing the result of the check (pass/fail), a message, and any relevant details.
    """

    if not github_client:
        return {
            "result": "error",
            "message": "GitHub client cannot be None.",
            "details": {"github_client": github_client},
        }

    if not repository_name:
        return {
            "result": "error",
            "message": "Repository name cannot be empty.",
            "details": {"repository_name": repository_name},
        }

    try:
        response = github_client.make_request(
            "GET", f"/repos/{github_client.owner}/{repository_name}"
        )

        details = response.json()

        if not isinstance(details, dict):
            return {
                "result": "error",
                "message": "API response is not a valid JSON object.",
                "details": {"response": details},
            }

        return {
            "result": "pass",
            "message": f"Successfully retrieved details for repository '{repository_name}'.",
            "details": details,
        }

    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while fetching repository details: {str(e)}",
            "details": {},
        }
