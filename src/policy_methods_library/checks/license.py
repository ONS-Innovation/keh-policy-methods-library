"""This module contains a check to see if the repository has a license file."""

from policy_methods_library.github.clients import GitHubRestClient


def check_license(
    client: GitHubRestClient,
    repository_name: str,
) -> dict:
    """Check if a repository has a license file.

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
        is_repo_private = (
            client.make_request("GET", f"/repos/{client.owner}/{repository_name}")
            .json()
            .get("private")
        )
        if is_repo_private:
            return {
                "result": "pass",
                "message": f"Repository '{repository_name}' is not public and does not require a license file.",
                "details": {
                    "repository_name": repository_name,
                    "required_file": "license",
                    "is_public": False,
                },
            }

        response = client.make_request(
            "GET", f"/repos/{client.owner}/{repository_name}/contents/"
        )
        contents = response.json()

        license_file = next(
            (
                item
                for item in contents
                if item.get("name", "").lower() == "license"
                or item.get("name", "").lower() == "license.md"
                or item.get("name", "").lower() == "license.txt"
            ),
            None,
        )

        if license_file is not None:
            return {
                "result": "pass",
                "message": f"Repository '{repository_name}' contains a license file.",
                "details": {
                    "repository_name": repository_name,
                    "required_file": "license",
                },
            }

        return {
            "result": "fail",
            "message": f"Repository '{repository_name}' does not contain a license file.",
            "details": {
                "repository_name": repository_name,
                "required_file": "license",
            },
        }

    except Exception as e:
        return {
            "result": "error",
            "message": f"Error fetching repository data: {str(e)}",
            "details": {},
        }
