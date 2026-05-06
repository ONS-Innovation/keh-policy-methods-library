"""This module contains a check for repository naming conventions."""


def check_naming_convention(
    repository_name: str,
) -> dict:
    """Ensures that the repository name follows GitHub Usage Policy Naming Conventions.
    This check verifies that the repository name is in lowercase and does not contain spaces or special characters.

    Args:
        repository_name (str): The name of the GitHub repository to check.
    Returns:
        dict: A dictionary containing the result of the check, a message, and any relevant details.
    """

    if not repository_name:
        return {
            "result": "fail",
            "message": "Repository name cannot be empty.",
            "details": {"repository_name": repository_name},
        }

    if not repository_name.islower():
        return {
            "result": "fail",
            "message": "Repository name should be in lowercase.",
            "details": {"repository_name": repository_name},
        }

    if " " in repository_name:
        return {
            "result": "fail",
            "message": "Repository name should not contain spaces.",
            "details": {"repository_name": repository_name},
        }

    if any(char in repository_name for char in "!@#$%^&*()+=[]{}|\\;:'\"<>,.?/"):
        return {
            "result": "fail",
            "message": "Repository name should not contain special characters.",
            "details": {"repository_name": repository_name},
        }

    return {
        "result": "pass",
        "message": "Repository name follows GitHub Usage Policy Naming Conventions.",
        "details": {"repository_name": repository_name},
    }
