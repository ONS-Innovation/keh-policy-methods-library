"""Checks that the secret scanner alerts are resolved within the policy-defined SLO."""

from datetime import datetime, timedelta, timezone

from policy_methods_library.github.clients import GitHubRestClient

_SLO: int = 5

_NOW = datetime.now(timezone.utc)

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
    return _NOW > slo_deadline


def _verify_client_organisation(client: GitHubRestClient) -> dict | None:
    """Validate that the client owner resolves to an organisation account.

    Args:
        client: An instance of the GitHubRestClient to validate.

    Returns:
        A standard error result dictionary when validation fails, otherwise None.
    """
    try:
        response = client.make_request("GET", f"/orgs/{client.owner}")
        organisation_data = response.json()
    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while verifying organisation authentication: {str(e)}",
            "details": {},
        }

    if not isinstance(organisation_data, dict):
        return {
            "result": "error",
            "message": "API response does not contain organisation data.",
            "details": {"response": organisation_data},
        }

    if organisation_data.get("type") != "Organization":
        return {
            "result": "error",
            "message": "Client is not authenticated as an organisation.",
            "details": {"organisation": organisation_data},
        }

    return None


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

    organisation_check_result = _verify_client_organisation(client=client)
    if organisation_check_result is not None:
        return organisation_check_result

    secret_scanning_alerts: list = []

    try:
        next_page_url = (
            f"/orgs/{client.owner}/secret-scanning/alerts?per_page=100&state=open"
        )
        has_next_page = True

        while has_next_page:
            response = client.make_request("GET", next_page_url)
            response_secret_scanning_alerts = response.json()

            if isinstance(response_secret_scanning_alerts, list):
                secret_scanning_alerts.extend(response_secret_scanning_alerts)  # type: ignore[union-attr]
            else:
                return {
                    "result": "error",
                    "message": "API response does not contain a list of Secret Scanning alerts.",
                    "details": {"response": response_secret_scanning_alerts},
                }

            if response.links and "next" in response.links:
                next_page_url = response.links["next"]["url"].replace(
                    "https://api.github.com", ""
                )
            else:
                has_next_page = False
    except Exception as e:
        return {
            "result": "error",
            "message": f"Error fetching Secret Scanning alerts: {str(e)}.",
            "details": {},
        }

    exceeded_alerts: list = []
    repositories: dict[str, int] = {}
    for alert in secret_scanning_alerts:
        # Getting the Repository URL
        repo = alert.get("repository").get("name")
        org = client.owner
        repo_name = f"{org}/{repo}"

        if not _exceeds_slo(alert):
            continue

        if not repo_name:
            continue

        exceeded_alerts.append(alert)

        if repo_name not in repositories:
            repositories[repo_name] = 1
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
