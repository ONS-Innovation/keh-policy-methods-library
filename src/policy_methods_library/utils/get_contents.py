"""Get a list of repository files from GitHub."""

from typing import Any

from policy_methods_library.github.clients import GitHubRestClient


def get_repo_contents(
    github_client: GitHubRestClient, repository_name: str
) -> list[dict[str, Any]] | dict[str, str]:
    """Return repository top-level contents data or an error object.

    Args:
        github_client: GitHub REST client used to make API calls.
        repository_name: Name of the repository.

    Returns:
        On success: Repository contents as returned by GitHub.
        On error: {"error": "<message>"}
    """

    if not isinstance(github_client, GitHubRestClient):
        return {"error": "GitHubRestClient instance is required."}

    if not isinstance(repository_name, str) or repository_name.strip() == "":
        return {"error": "Repository name is required."}

    try:
        response = github_client.make_request(
            "GET",
            f"/repos/{github_client.owner}/{repository_name}/contents",
        )

        return response.json()

    except Exception as e:
        return {
            "error": f"An error occurred while fetching repository contents: {str(e)}"
        }
