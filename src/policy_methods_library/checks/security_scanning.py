"""This module contains a check for ensuring Push Protection and Secret Scanning are enabled."""

from policy_methods_library.github.clients import GitHubRestClient
from typing import Optional


def check_security_scanning(
    client: Optional[GitHubRestClient] = None,
    repository_name: Optional[str] = None,
    data: Optional[dict] = None,
) -> dict:
    """Check if Push Protection and Secret Scanning are enabled for a repository.

    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required if data is not provided. Defaults to None.
        repository_name: The name of the repository to check. Required if data is not provided. Defaults to None.
        data: A dictionary containing data about the repository. This must contain the 'security_and_analysis' field with the security settings. If provided, client and repository_name are ignored. Defaults to None.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error), 'message', and 'details'.
    """

    if data is not None:
        if "security_and_analysis" not in data:
            return {
                "result": "error",
                "message": "Data must include 'security_and_analysis' field.",
                "details": {"data": data},
            }

        security_analysis = data.get("security_and_analysis")

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
            security_analysis = repository_info.get("security_and_analysis")

            if security_analysis is None:
                return {
                    "result": "error",
                    "message": "API response does not contain 'security_and_analysis' field.",
                    "details": {"response": repository_info},
                }
        except Exception as e:
            return {
                "result": "error",
                "message": f"Error fetching repository data: {str(e)}",
                "details": {},
            }

    if not isinstance(security_analysis, dict):
        return {
            "result": "error",
            "message": "Invalid type for 'security_and_analysis'. Expected dictionary.",
            "details": {"security_and_analysis": security_analysis},
        }

    # Extract the status of Push Protection and Secret Scanning
    push_protection_status = security_analysis.get("secret_scanning_push_protection", {})
    secret_scanning_status = security_analysis.get("secret_scanning", {})

    # Check if both are enabled
    push_protection_enabled = push_protection_status.get("status") == "enabled"
    secret_scanning_enabled = secret_scanning_status.get("status") == "enabled"

    details = {
        "push_protection_enabled": push_protection_enabled,
        "secret_scanning_enabled": secret_scanning_enabled,
        "security_and_analysis": security_analysis,
    }

    if push_protection_enabled and secret_scanning_enabled:
        return {
            "result": "pass",
            "message": "Both Push Protection and Secret Scanning are enabled.",
            "details": details,
        }
    else:
        disabled_features = []
        if not push_protection_enabled:
            disabled_features.append("Push Protection")
        if not secret_scanning_enabled:
            disabled_features.append("Secret Scanning")

        return {
            "result": "fail",
            "message": f"The following security features are not enabled: {', '.join(disabled_features)}.",
            "details": details,
        }
