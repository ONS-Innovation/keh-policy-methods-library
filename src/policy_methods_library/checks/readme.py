"""This module contains a check to see if the repository has a readme file."""

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.get_contents import get_repo_contents


def check_readme(
    client: GitHubRestClient,
    repository_name: str,
) -> dict:
    """Check if a repository has a readme file.

    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required.
        repository_name: The name of the repository to check. Required.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error), 'message', and 'details'.
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
        contents = get_repo_contents(client, repository_name)
        if isinstance(contents, dict) and "error" in contents:
            return {
                "result": "error",
                "message": contents["error"],
                "details": {},
            }

        if not isinstance(contents, list):
            return {
                "result": "error",
                "message": "Unexpected repository contents format.",
                "details": {"response": contents},
            }

        readme = next(
            (item for item in contents if item.get("name", "").lower() == "readme.md"),
            None,
        )

        if readme is not None:
            return {
                "result": "pass",
                "message": f"Repository '{repository_name}' contains a readme.md file.",
                "details": {
                    "repository_name": repository_name,
                    "required_file": "readme.md",
                },
            }

        return {
            "result": "fail",
            "message": f"Repository '{repository_name}' does not contain a readme.md file.",
            "details": {
                "repository_name": repository_name,
                "required_file": "readme.md",
            },
        }

    except Exception as e:
        return {
            "result": "error",
            "message": f"Error fetching repository data: {str(e)}",
            "details": {},
        }
