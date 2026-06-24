"""Checks that Dependabot security alerts are resolved within the policy-defined SLO."""

from datetime import datetime, timedelta, timezone

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.organisation import verify_client_organisation
from policy_methods_library.utils.pagination import get_paginated_list

_SLO_DAYS: dict[str, int] = {
    "critical": 5,
    "high": 15,
    "medium": 60,
    "low": 90,
}

NOW = datetime.now(timezone.utc)


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


def _exceeds_slo(alert: dict, severity: str) -> bool:
    """
    Return True if the alert has exceeded its SLO or has a missing/invalid created_at.
    Alerts with a missing or broken created_at are considered failures.
    Alerts exactly at the SLO end date are considered failures.

    Args:
        alert: dictionary for the alert
        severity: string for level of severity

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

    slo_deadline = _add_working_days(created_at, _SLO_DAYS[severity])
    return NOW > slo_deadline


def get_dependabot_slo(
    client: GitHubRestClient,
    levels: list[str] | None = None,
) -> dict:
    """Get open Dependabot security alerts grouped by severity.

    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required.
        levels: A list of alert severities to include in the check.

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

    valid_levels = ["critical", "high", "medium", "low"]

    if levels is None or levels == []:
        levels = valid_levels
    else:
        levels = [level for level in levels if level in valid_levels]

        if not levels:
            levels = valid_levels

    organisation_check_result = verify_client_organisation(client=client)
    if organisation_check_result is not None:
        return organisation_check_result

    dependabot_alerts: dict[str, list] = {level: [] for level in levels}

    for level in levels:
        initial_endpoint = (
            f"/orgs/{client.owner}/dependabot/alerts"
            f"?per_page=100&state=open&severity={level}"
        )

        alerts_for_level = get_paginated_list(
            client,
            initial_endpoint=initial_endpoint,
            list_name=f"Dependabot {level} alerts",
        )

        if isinstance(alerts_for_level, dict) and "error" in alerts_for_level:
            if "response" in alerts_for_level:
                return {
                    "result": "error",
                    "message": alerts_for_level["error"],
                    "details": {"response": alerts_for_level["response"]},
                }

            return {
                "result": "error",
                "message": f"Error fetching Dependabot alerts: {alerts_for_level['error']}.",
                "details": {},
            }

        dependabot_alerts[level].extend(alerts_for_level)

    exceeded_alerts: dict[str, list] = {level: [] for level in levels}
    repositories: dict[str, dict[str, int]] = {}
    for level, alerts in dependabot_alerts.items():
        for alert in alerts:
            # Getting the Repository URL
            repo = alert.get("repository").get("name")
            org = client.owner
            repo_name = f"{org}/{repo}"

            if not _exceeds_slo(alert, level):
                continue

            exceeded_alerts[level].append(alert)

            # Add Repository and add 1 to the SLO level
            if repo_name not in repositories:
                repositories[repo_name] = {lv: 0 for lv in levels}
                repositories[repo_name][level] += 1
            else:
                continue

    total_repositories_affected = len(repositories)
    total_open_alerts = sum(len(alerts) for alerts in dependabot_alerts.values())

    number_exceeded_by_severity = {
        level: len(alerts) for level, alerts in exceeded_alerts.items()
    }
    failing_alerts = sum(number_exceeded_by_severity.values())

    if failing_alerts == 0:
        return {
            "result": "pass",
            "message": "All alerts are within policy defined SLO.",
            "details": {},
        }

    return {
        "result": "fail",
        "message": f"Found {failing_alerts} open Dependabot security alerts exceeding the policy-defined SLO.",
        "details": {
            "total_open_alerts": total_open_alerts,
            "failing_alerts": failing_alerts,
            "number_exceeded_by_severity": number_exceeded_by_severity,
            "total_repositories_affected": total_repositories_affected,
            "repositories": repositories,
        },
    }
