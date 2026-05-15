"This module contains the checks for PIRR"

def check_repo_visibility(repository_name: str) -> dict:
    """
    if the repository 
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
            }else:
            return {
                    "result": "pass",
                    "message": "Repository name is not empty.",
                    "details": {"repository_name": repository_name},
            }