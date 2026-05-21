from policy_methods_library.github.clients import GitHubRestClient


def get_repo_contents(repository_name: str, github_client: GitHubRestClient) -> dict:
    """
    Args:
            repository_name (str): The name of the repository to check.
            github_client (GitHubRestClient): The GitHub REST client to use for making requests.

    Returns:
            dict: A dictionary containing the result of the check (pass/fail), a message, and any relevant details.
    """

    if not repository_name:
        return {
            "result": "fail",
            "message": "Repository name cannot be empty.",
            "details": {"repository_name": repository_name},
        }

    response = github_client.make_request(
        "GET", f"/repos/{github_client.owner}/{repository_name}/contents"
    )

    if response is None:
        return {
            "result": "fail",
            "message": "Unable to retrieve repository contents.",
            "details": {"repository_name": repository_name},
        }

    return response
