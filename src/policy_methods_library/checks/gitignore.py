"""This module contains a check to see if the repository has a .gitignore file."""

from policy_methods_library.github.clients import GitHubRestClient


def check_gitignore(
    client: GitHubRestClient,
    repository_name: str,
) -> dict:
    """Check if a repository has a .gitignore file.

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
        response = client.make_request(
            "GET", f"/repos/{client.owner}/{repository_name}/contents/"
        )
        contents = response.json()

        gitignore = next(
            (item for item in contents if item.get("name", "").lower() == ".gitignore"),
            None,
        )

        if gitignore is not None:
            return {
                "result": "pass",
                "message": f"Repository '{repository_name}' contains a .gitignore file.",
                "details": {
                    "repository_name": repository_name,
                    "required_file": ".gitignore",
                },
            }

        return {
            "result": "fail",
            "message": f"Repository '{repository_name}' does not contain a .gitignore file.",
            "details": {
                "repository_name": repository_name,
                "required_file": ".gitignore",
            },
        }

    except Exception as e:
        return {
            "result": "error",
            "message": f"Error fetching repository data: {str(e)}",
            "details": {},
        }
