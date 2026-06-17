"""This module contains the checks for PIRR"""

from policy_methods_library.github.clients import GitHubRestClient

from policy_methods_library.utils.get_contents import get_repo_contents
# Backwards-compatible alias: some tests (or callers) reference get_repo_content
get_repo_content = get_repo_contents

from policy_methods_library.utils.get_details import get_repo_details


def check_pirr(client: GitHubRestClient, repository_name: str) -> dict:
    """
    This function checks the visibility and private for a repository.

    Args:
        client (GitHubRestClient): The GitHub REST client.
        repository_name (str): The name of the repository to check.

    Returns:
        dict: A dictionary containing the result of the check (pass/fail/error),
              a message, and any relevant details.
    """

    if not isinstance(repository_name, str) or repository_name.strip() == "":
        return {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    if not isinstance(client, GitHubRestClient):
        return {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    try:
        repo_details = get_repo_details(client, repository_name)

        if (
            not repo_details["details"]['details']['private']
            and repo_details["details"]['details']['visibility'] == "public"
        ):
            return {
                "result": "pass",
                "message": (
                    f"Successfully retrieved the details for "
                    f"repository {repository_name}"
                ),
                "details": {
                    "repository_name": repository_name,
                    "repository_details": repo_details["details"]['details']
                },
            }
        else:
            try:
                repo_contents = get_repo_contents(client, repository_name)
                if any(
                    content.get("name", "").lower() == "pirr.md"
                    for content in repo_contents
                ):
                    return {
                        "result": "pass",
                        "message": "Repository contains PIRR documentation.",
                        "details": {
                            "repository_name": repository_name,
                            "repository_details": repo_details,
                            "repository_contents": repo_contents,
                        },
                    }
                else:
                    return {
                        "result": "faii",
                        "message": "Repository does not contain PIRR documentation",
                        "details": {
                            "repository_name": repository_name,
                            "repository_details": repo_details,
                            "repository_contents": repo_contents,
                        },
                    }
            except Exception as e:
                return {
                    "result": "error",
                    "message": f"Error fetching repository contents: {str(e)}",
                    "details": {},
                }

    except Exception as e:
        return {
            "result": "error",
            "message": f"Error fetching repository details: {str(e)}",
            "details": {},
        }
