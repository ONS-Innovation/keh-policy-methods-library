"""Get a list of repository files from GitHub."""

from typing import Any
import requests

from policy_methods_library.github.clients import GitHubRestClient


def get_repo_contents(
    github_client: GitHubRestClient,
    repository_name: str,
    path: str | None = None,
) -> list[dict[str, Any]] | dict[str, str]:
    """Return repository top-level contents data or an error object.

    Args:
        github_client: GitHub REST client used to make API calls.
        repository_name: Name of the repository.
        path: Optional repository path under contents endpoint.

    Returns:
        On success: Raw repository contents as returned by GitHub.
        On error: {"error": "<message>"}
    """

    if not isinstance(github_client, GitHubRestClient):
        return {"error": "GitHubRestClient instance is required."}

    if not isinstance(repository_name, str) or repository_name.strip() == "":
        return {"error": "Repository name is required."}

    if path is not None and not isinstance(path, str):
        return {"error": "Path must be a string when provided."}

    try:
        endpoint = f"/repos/{github_client.owner}/{repository_name}/contents"
        if path:
            endpoint = f"{endpoint}/{path.lstrip('/')}"

        response = github_client.make_request(
            "GET",
            endpoint,
        )

        return response.json()

    except requests.HTTPError as e:
        error = {
            "error": f"An error occurred while fetching repository contents: {str(e)}"
        }

        if e.response is not None and e.response.status_code is not None:
            error["status_code"] = str(e.response.status_code)

        return error

    except Exception as e:
        return {
            "error": f"An error occurred while fetching repository contents: {str(e)}"
        }
