"""
Get repository details from GitHub."""

from policy_methods_library.github.clients import GitHubRestClient


def get_repo_details(github_client: GitHubRestClient, repository_name: str) -> dict:
    """
    Args:
            github_client (GitHubRestClient): The GitHub REST client to use for making requests.
            repository_name (str): The name of t"he repository for which to retrieve details.

    Returns:
            dict: A dictionary containing the result of the check (pass/fail), a message, and any relevant details.
    """

    if not github_client:
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
        response = github_client.make_request(
            "GET", f"/repos/{github_client.owner}/{repository_name}"
        )

        return {
            "result": "pass",
            "message": "Repository details retrieved successfully.",
            "details": {
                "repository_name": repository_name,
                "details": response.json(),
            },
        }

    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while fetching repository details: {str(e)}",
            "details": {},
        }
