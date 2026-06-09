"This module contains the checks for PIRR"

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.get_contents import get_repo_contents
from policy_methods_library.utils.get_details import get_repo_details


def check_repo_visibility(client: GitHubRestClient, repository_name: str) -> dict:
    """
    This function checks if a repository visibility is either private or internal and contains PIRR documentation.

    Args:
        client (GitHubRestClient): The GitHub REST client.
        repository_name (str): The name of the repository to check.

    Returns:
            dict: A dictionary containing the result of the check (pass/fail/error), a message, and any relevant details.
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

    except Exception as e:
        return {
            "result": e["result"] if isinstance(e, dict) and "result" in e else "error",
            "message": e["message"]
            if isinstance(e, dict) and "message" in e
            else f"An error occurred while fetching repository details: {str(e)}",
            "details": {},
        }

    if (
        not repo_details.get("details", {}).get("private")
        and repo_details.get("details", {}).get("visibility") == "public"
    ):
        return {
            "result": "pass",
            "message": "Repository is public.",
            "details": {
                "repository_name": repository_name,
                "repository_details": repo_details.get("details", {}),
            },
        }

    try:
        repo_contents = get_repo_contents(client, repository_name)

    except Exception as e:
        return {
            "result": e["result"] if isinstance(e, dict) and "result" in e else "error",
            "message": e["message"]
            if isinstance(e, dict) and "message" in e
            else f"An error occurred while fetching repository contents: {str(e)}",
            "details": {},
        }

    # Check the repository contents have pirr mkdocumentation

    if any(content.get("name").lower() == "pirr.md" for content in repo_contents):
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
            "result": "fail",
            "message": "Repository does not contain PIRR documentation.",
            "details": {
                "repository_name": repository_name,
                "repository_details": repo_details,
                "repository_contents": repo_contents,
            },
        }
