"""This module contains a check for repository naming conventions."""

from policy_methods_library.github.clients import GitHubRestClient
from typing import Optional


def check_naming_convention(
    client: Optional[GitHubRestClient] = None,
    repository_name: Optional[str] = None,
    data: Optional[dict] = None,
) -> dict:
    """Ensures that the repository name follows GitHub Usage Policy Naming Conventions.
    This check verifies that the repository name is in lowercase and does not contain spaces or special characters.

    Requires a GitHubRestClient, repository_name and owner to fetch the data, or the data to be passed directly.

    Args:
        client (Optional[GitHubRestClient], optional): An instance of the GitHubRestClient. Required if data is not provided. Defaults to None.
        repository_name (Optional[str], optional): The name of the repository to check. Required if client is provided. Defaults to None.
        owner (Optional[str], optional): The owner the repository belongs to (i.e. the organisation or GitHub Account). Required if client is provided. Defaults to None.
        data (Optional[dict], optional): The data to check. Defaults to None.

    Returns:
        dict: A dictionary containing the result of the check, a message, and any additional data.
    """

    if data is None:
        if client is None:
            raise ValueError(
                "A GitHubRestClient instance must be provided if data is not passed directly."
            )
        if repository_name is None:
            raise ValueError(
                "A repository name must be provided if data is not passed directly."
            )

        try:
            response = client.make_request(
                "GET", f"/repos/{client.owner}/{repository_name}"
            )
        except Exception as e:
            return {
                "result": "error",
                "message": f"An error occurred while fetching repository data: {str(e)}",
                "data": None,
            }

        if response.status_code != 200:
            return {
                "result": "error",
                "message": f"Failed to fetch repository data. Status code: {response.status_code}",
                "data": None,
            }

        data = response.json()

    repo_name = data.get("name", "")

    if not repo_name.islower():
        return {
            "result": "fail",
            "message": "Repository name should be in lowercase.",
            "data": {"repository_name": repo_name},
        }

    if " " in repo_name:
        return {
            "result": "fail",
            "message": "Repository name should not contain spaces.",
            "data": {"repository_name": repo_name},
        }

    if any(char in repo_name for char in "!@#$%^&*()+=[]{}|\\;:'\"<>,.?/"):
        return {
            "result": "fail",
            "message": "Repository name should not contain special characters.",
            "data": {"repository_name": repo_name},
        }

    return {
        "result": "pass",
        "message": "Repository name follows GitHub Usage Policy Naming Conventions.",
        "data": {"repository_name": repo_name},
    }
