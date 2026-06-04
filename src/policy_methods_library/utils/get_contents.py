from policy_methods_library.github.clients import GitHubRestClient


def get_repo_contents(github_client: GitHubRestClient, repository_name: str) -> dict:
    """
    Args:
            github_client (GitHubRestClient): The GitHub REST client to use for making requests.
            repository_name (str): The name of the repository for which to retrieve contents.
    Returns:
            list: A list of dictionaries containing the details of each file or directory in the repository.
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

        contents = response.json()

        if not isinstance(contents, list):
            return {
                "result": "error",
                "message": "API response is not a valid JSON array.",
                "details": {"response": contents},
            }
        return {
            "result": "pass",
            "message": f"Successfully retrieved contents for repository '{repository_name}'.",
            "details": contents,
        }
    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while fetching repository contents: {str(e)}",
            "details": {},
        }
