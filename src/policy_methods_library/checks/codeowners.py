"""This module contains a check to see if the repository has a CODEOWNERS file."""

import base64

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.get_contents import get_repo_contents

CODEOWNERS_PATHS = [
    "CODEOWNERS",
    ".github/CODEOWNERS",
    "docs/CODEOWNERS",
]


def check_codeowners(
    client: GitHubRestClient,
    repository_name: str,
) -> dict:
    """Check if a repository has a CODEOWNERS file.

    Searches for a CODEOWNERS file in the repository root, `.github/`, and `docs/` directories,
    (referenced as CODEOWNERS_PATHS) which are the locations GitHub recognises for CODEOWNERS files.

    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required.
        repository_name: The name of the repository to check. Required.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error), 'message', and 'details'.
        Details contains the 'repository_name', and either 'codeowners_path' (on pass) or 'checked_paths' (on fail).
        A file that exists but contains only whitespace is treated as empty and will fail.
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
        for path in CODEOWNERS_PATHS:
            file_data = get_repo_contents(client, repository_name, path)

            if isinstance(file_data, dict) and "error" in file_data:
                if file_data.get("status_code") == "404":
                    continue

                return {
                    "result": "error",
                    "message": file_data["error"],
                    "details": {},
                }

            if not isinstance(file_data, dict):
                return {
                    "result": "error",
                    "message": "Unexpected CODEOWNERS API response format.",
                    "details": {"response": file_data},
                }

            encoded_content = file_data.get("content", "")
            decoded_content = base64.b64decode(encoded_content).decode("utf-8")

            if not decoded_content.strip():
                return {
                    "result": "fail",
                    "message": f"Repository '{repository_name}' contains a CODEOWNERS file at '{path}' but it is empty.",
                    "details": {
                        "repository_name": repository_name,
                        "codeowners_path": path,
                    },
                }

            return {
                "result": "pass",
                "message": f"Repository '{repository_name}' contains a CODEOWNERS file at '{path}'.",
                "details": {
                    "repository_name": repository_name,
                    "codeowners_path": path,
                },
            }

        return {
            "result": "fail",
            "message": f"Repository '{repository_name}' does not contain a CODEOWNERS file.",
            "details": {
                "repository_name": repository_name,
                "checked_paths": CODEOWNERS_PATHS,
            },
        }

    except Exception as e:
        return {
            "result": "error",
            "message": f"Error fetching repository data: {str(e)}",
            "details": {},
        }
