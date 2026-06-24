"""This module contains a check to validate PIRR requirements."""

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.get_contents import get_repo_contents
from policy_methods_library.utils.get_details import get_repo_details


def check_pirr(client: GitHubRestClient, repository_name: str) -> dict:
    """Check PIRR requirements based on repository visibility.
    Passes if the repository is public or if it is private/internal and contains a `pirr.md` file.
    Fails if the repository is private/internal and does not contain a `pirr.md` file.

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
        repository_details = repo_details["details"]["repository_details"]

        is_private = repository_details["private"]
        visibility = repository_details["visibility"].lower()

        if not is_private and visibility == "public":
            return {
                "result": "pass",
                "message": (
                    f"Successfully retrieved the details for "
                    f"repository {repository_name}"
                ),
                "details": {
                    "repository_name": repository_name,
                    "repository_details": repository_details,
                },
            }

        if is_private and visibility in ["private", "internal"]:
            try:
                repo_contents = get_repo_contents(client, repository_name)
                repository_contents = repo_contents["details"]["repository_contents"]

                if any(
                    content.get("name", "").lower() == "pirr.md"
                    for content in repository_contents
                ):
                    return {
                        "result": "pass",
                        "message": "Repository contains PIRR documentation.",
                        "details": {
                            "repository_name": repository_name,
                            "repository_details": repository_details,
                            "repository_contents": repository_contents,
                        },
                    }

                return {
                    "result": "fail",
                    "message": "Repository missing PIRR documentation.",
                    "details": {
                        "repository_name": repository_name,
                        "repository_details": repository_details,
                        "repository_contents": repository_contents,
                    },
                }
            except Exception as e:
                return {
                    "result": "error",
                    "message": (f"Error fetching repository content: {str(e)}."),
                    "details": {
                        "repository_name": repository_name,
                        "repository_details": repository_details,
                        "repository_contents": {},
                    },
                }

        return {
            "result": "error",
            "message": (
                "Repository visibility or privacy settings are unexpected for "
                f"{repository_name}."
            ),
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
            },
        }

    except Exception as e:
        return {
            "result": "error",
            "message": (f"Error fetching repository details: {str(e)}"),
            "details": {},
        }
