"""Checks that Dependabot security alerts are resolved within the policy-defined SLO."""

from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from policy_methods_library.github.clients import GitHubRestClient

_SLO_DAYS: dict[str, int] = {
    "critical": 5,
    "high": 15,
    "medium": 60,
    "low": 90,
}

NOW = datetime.now(timezone.utc)


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

    slo_deadline = NOW - timedelta(days=_SLO_DAYS[severity])
    return created_at <= slo_deadline


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

    if levels is None or levels == []:
        levels = ["critical", "high", "medium", "low"]

    organisation_check_result = _verify_client_organisation(client=client)
    if organisation_check_result is not None:
        return organisation_check_result

    dependabot_alerts: dict[str, list] = {level: [] for level in levels}

    try:
        for level in levels:
            next_page_url = (
                f"/orgs/{client.owner}/dependabot/alerts"
                f"?per_page=100&state=open&severity={level}"
            )
            has_next_page = True

            while has_next_page:
                response = client.make_request("GET", next_page_url)
                response_dependabot_alerts = response.json()

                if isinstance(response_dependabot_alerts, list):
                    dependabot_alerts[level].extend(response_dependabot_alerts)
                else:
                    return {
                        "result": "error",
                        "message": f"API response does not contain a list of Dependabot {level} alerts.",
                        "details": {"response": response_dependabot_alerts},
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
            "message": f"Error fetching Dependabot alerts: {str(e)}.",
            "details": {},
        }

    exceeded_alerts: dict[str, list] = {level: [] for level in levels}
    repositories: dict[str, dict[str, int]] = {}
    for level, alerts in dependabot_alerts.items():
        for alert in alerts:

            # Getting the Repository URL
            repo_url_raw = alert.get("html_url")

            if not _exceeds_slo(alert,level):
                continue

            if not repo_url_raw:
                continue

            exceeded_alerts[level].append(alert)

            # Splitting the URL into parts
            parts = (
                urlparse(str(repo_url_raw).strip('"'))
                .path.strip("/")
                .split("/")
            )
            # If there are more than two parts in the URL (if not then th elink is invalid)
            if len(parts) >= 2:
                # org_name/repo_name
                repo_name = f"{parts[0]}/{parts[1]}"

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
            "message": "No open Dependabot security alerts found.",
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
