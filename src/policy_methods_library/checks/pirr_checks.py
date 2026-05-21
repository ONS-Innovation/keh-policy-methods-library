"This module contains the checks for PIRR"


def check_repo_visibility(repo_details: dict, repo_contents: dict) -> dict:
    """
    Args:
            repo_details (dict): The details of the repository to check.
            repo_contents (dict): The contents of the repository to check.

    Returns:
            dict: A dictionary containing the result of the check (pass/fail), a message, and any relevant details.
    """

    if not repo_details:
        return {
            "result": "fail",
            "message": "Repository details cannot be empty.",
            "details": {"repo_details": repo_details},
        }

    if "private" not in repo_details or "visibility" not in repo_details:
        return {
            "result": "fail",
            "message": "Repository details must include 'private' and 'visibility' keys.",
            "details": {"repo_details": repo_details},
        }

    if not repo_contents:
        return {
            "result": "fail",
            "message": "Repository contents cannot be empty.",
            "details": {"repo_contents": repo_contents},
        }

    if "entries" not in repo_contents:
        return {
            "result": "fail",
            "message": "Repository contents must include 'entries' key.",
            "details": {"repo_contents": repo_contents},
        }

    if repo_details.get("private") is False:
        return {
            "result": "pass",
            "message": "Repository is public.",
            "details": {"repo_details": repo_details},
        }

    entries = repo_contents.get("entries", [])
    pirr_files = [
        entry for entry in entries if entry.get("name", "").lower() == "pirr.md"
    ]
    if pirr_files:
        return {
            "result": "pass",
            "message": "Repository is private but contains a PIRR.md file.",
            "details": {"repo_details": repo_details, "repo_contents": repo_contents},
        }
    else:
        return {
            "result": "fail",
            "message": "Repository is private and does not contain a PIRR.md file.",
            "details": {"repo_details": repo_details, "repo_contents": repo_contents},
        }
