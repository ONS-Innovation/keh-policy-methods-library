"""This module contains a check for repository naming conventions."""


def check_naming_convention(
    repository_name: str,
) -> dict:
    """Ensures that the repository name follows GitHub Usage Policy Naming Conventions.
    This check verifies that the repository name is in lowercase and does not contain spaces or special characters.

    Args:
        repository_name (str): The name of the GitHub repository to check.
    Returns:
        dict: A dictionary containing the result of the check (pass/fail), a message, and any relevant details.
    """

    if not repository_name:
        return {
            "result": "fail",
            "message": "Repository name cannot be empty.",
            "details": {"repository_name": repository_name},
        }

    # Note: Although the lowercase and no spaces check are covered by allowed_characters,
    # they are included as separate checks to provide more specific feedback on why a repository name fails the check.
    # Invalid characters can be grouped together but spaces and uppercase letters would be harder to identify if they are just part of a larger invalid character issue.

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

    # Only allow lowercase letters, numbers, hyphens, and underscores in repository names
    allowed_characters = set("abcdefghijklmnopqrstuvwxyz0123456789-_")

    if any(char not in allowed_characters for char in repository_name):
        return {
            "result": "fail",
            "message": "Repository name should only contain letters, numbers, hyphens, and underscores.",
            "details": {"repository_name": repository_name},
        }

    return {
        "result": "pass",
        "message": "Repository name follows GitHub Usage Policy Naming Conventions.",
        "details": {"repository_name": repository_name},
    }
