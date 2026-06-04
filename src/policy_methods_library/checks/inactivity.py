"""This module contains a check for repository inactivity (not updated within a year)."""

from policy_methods_library.github.clients import GitHubRestClient
from typing import Optional
from datetime import datetime, timedelta, timezone


def check_inactivity(
    client: Optional[GitHubRestClient] = None,
    repository_name: Optional[str] = None,
    data: Optional[dict] = None,
) -> dict:
    """Check if a repository has been inactive for over a year.

    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required if data is not provided. Defaults to None.
        repository_name: The name of the repository to check. Required if data is not provided. Defaults to None.
        data: A dictionary containing data about the repository. This must contain the 'updated_at' field with the last update timestamp. If provided, client and repository_name are ignored. Defaults to None.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error), 'message', and 'details'.
    """

    if data is not None:
        if "updated_at" not in data:
            return {
                "result": "error",
                "message": "Data must include 'updated_at' field.",
                "details": {"data": data},
            }

        last_updated = data.get("updated_at")

    else:
        if client is None:
            return {
                "result": "error",
                "message": "GitHubRestClient instance is required if data is not provided.",
                "details": {},
            }
        if repository_name is None:
            return {
                "result": "error",
                "message": "Repository name is required if data is not provided.",
                "details": {},
            }

        try:
            response = client.make_request(
                "GET", f"/repos/{client.owner}/{repository_name}"
            )

            repository_info = response.json()
            last_updated = repository_info.get("updated_at")

            if last_updated is None:
                return {
                    "result": "error",
                    "message": "API response does not contain 'updated_at' field.",
                    "details": {"response": repository_info},
                }
        except Exception as e:
            return {
                "result": "error",
                "message": f"Error fetching repository data: {str(e)}",
                "details": {},
            }

    if not isinstance(last_updated, str):
        return {
            "result": "error",
            "message": "Invalid type for 'updated_at'. Expected ISO 8601 string.",
            "details": {"updated_at": last_updated},
        }

    try:
        last_updated_date = datetime.strptime(
            last_updated, "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)
    except ValueError:
        return {
            "result": "error",
            "message": "Invalid date format for 'updated_at'. Expected ISO 8601 format.",
            "details": {"updated_at": last_updated},
        }

    one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)

    if last_updated_date < one_year_ago:
        return {
            "result": "fail",
            "message": f"Repository {repository_name} has been inactive since {last_updated_date.strftime('%Y-%m-%d')}.",
            "details": {"last_updated": last_updated},
        }
    else:
        return {
            "result": "pass",
            "message": f"Repository {repository_name} has been updated within the last year.",
            "details": {"last_updated": last_updated},
        }
