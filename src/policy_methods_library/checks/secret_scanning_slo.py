"""Checks that the secret scanner alerts are resolved within the policy-defined SLO."""

from datetime import datetime, timedelta, timezone

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.organisation import verify_client_organisation
from policy_methods_library.utils.pagination import get_paginated_list

_SLO: int = 5


def _add_working_days(start_date: datetime, num_days: int) -> datetime:
    """Add a number of working days (Monday-Friday) to a date, excluding weekends.

    Args:
        start_date: The starting datetime
        num_days: Number of working days to add

    Returns:
        A datetime representing the start_date plus num_days working days
    """
    current_date = start_date
    days_added = 0

    while days_added < num_days:
        current_date += timedelta(days=1)

        if current_date.weekday() < 5:
            days_added += 1

    return current_date


def _exceeds_slo(alert: dict) -> bool:
    """
    Returns True, if the alerts exceeds the SLO fix by date (5 days)
    Alerts with a missing or broken created_at are considered failures.

    Args:
        alert: dictionary for the alert

    Returns:
        Boolean value for whether the SLO is exceeded or not
    """

    created_at_str = alert.get("created_at")

    if not created_at_str:
        return True

    try:
        created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except (ValueError, TypeError):
        return True

    slo_deadline = _add_working_days(created_at, _SLO)
    now = datetime.now(timezone.utc)
    return now > slo_deadline


def get_secret_scanning_slo(
    client: GitHubRestClient,
) -> dict:
    """Get all open Secret Scanning alerts

    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error),
        'message', and 'details'.
    """

    if client is None:
        return {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    organisation_check_result = verify_client_organisation(client=client)
    if organisation_check_result is not None:
        return organisation_check_result

    initial_endpoint = (
        f"/orgs/{client.owner}/secret-scanning/alerts?per_page=100&state=open"
    )
    secret_scanning_alerts = get_paginated_list(
        client,
        initial_endpoint=initial_endpoint,
        list_name="Secret Scanning alerts",
    )

    if isinstance(secret_scanning_alerts, dict) and "error" in secret_scanning_alerts:
        if "response" in secret_scanning_alerts:
            return {
                "result": "error",
                "message": secret_scanning_alerts["error"],
                "details": {"response": secret_scanning_alerts["response"]},
            }

        return {
            "result": "error",
            "message": f"Error fetching Secret Scanning alerts: {secret_scanning_alerts['error']}.",
            "details": {},
        }

    if not isinstance(secret_scanning_alerts, list):
        return {
            "result": "error",
            "message": "Unexpected Secret Scanning alerts format.",
            "details": {"response": secret_scanning_alerts},
        }

    exceeded_alerts: list = []
    repositories: dict[str, int] = {}
    for alert in secret_scanning_alerts:
        if not isinstance(alert, dict):
            return {
                "result": "error",
                "message": "Secret Scanning alert payload contains an unexpected item format.",
                "details": {"alert": alert},
            }

        # Getting the Repository URL
        repository = alert.get("repository")
        repo = repository.get("name") if isinstance(repository, dict) else None
        org = client.owner
        repo_name = f"{org}/{repo}"

        if not _exceeds_slo(alert):
            continue

        exceeded_alerts.append(alert)

        if repo_name not in repositories:
            repositories[repo_name] = 0
        repositories[repo_name] += 1

    total_repositories_affected = len(repositories)
    total_open_alerts = len(secret_scanning_alerts)

    total_exceeding_alerts = len(exceeded_alerts)

    if total_exceeding_alerts == 0:
        return {
            "result": "pass",
            "message": "No open Secret Scanning security alerts found exceeding SLO.",
            "details": {},
        }

    return {
        "result": "fail",
        "message": f"Found {total_exceeding_alerts} open Secret Scanning security alerts exceeding the policy-defined SLO.",
        "details": {
            "total_open_alerts": total_open_alerts,
            "failing_alerts": total_exceeding_alerts,
            "total_repositories_affected": total_repositories_affected,
            "repositories": repositories,
        },
    }
