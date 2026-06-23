"""
Get a list of repository files from GitHub.
"""

from policy_methods_library.github.clients import GitHubRestClient


def get_repo_contents(github_client: GitHubRestClient, repository_name: str) -> dict:
    """
    Args:
            github_client (GitHubRestClient): The GitHub REST client to use for
            making requests.  The name of the repository for which to retrieve
            contents.
    Returns:
            dict: A dictionary containing the result of the
            check (pass/fail),
            a message,
            and any relevant details.

            The details will include :-
                repository name

                conents: A list of dictionaries containing the details of each file
                or directory in the repository.
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
            "GET",
            f"/repos/{github_client.owner}/{repository_name}/contents",
        )

        return {
            "result": "pass",
            "message": "Repository contents retrieved successfully.",
            "details": {
                "repository_name": repository_name,
                "repository_contents": response.json(),
            },
        }

    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while fetching repository "
            f"contents: {str(e)}",
            "details": {},
        }
