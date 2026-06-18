"""Checks that the secret scanner alerts are resolved within the policy-defined SLO."""

from datetime import datetime, timedelta, timezone

from policy_methods_library.github.clients import GitHubRestClient

_SLO: int = 5

def _exceeds_slo(alert: dict, now: datetime) -> bool:
    """
    Returns True, if the alerts exceeds the SLO fix by date (5 days)
    Alerts with a missing or broken created_at are considered failures.
    
    Args:
        alert: dictionary for the alert
        now: the current time

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
    
    return created_at < timedelta(days=_SLO)


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
        _now: datetime | None = None
) -> dict:
    """Get all open Secret Scanning alerts
    
    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required.
        _now: The current time

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
    
    now = _now if _now is not None else datetime.now(timezone.utc)

    organisation_check_result = _verify_client_organisation(client=client)
    if organisation_check_result is not None:
        return organisation_check_result
    
    secret_scanning_alerts: dict = {"alerts"}

    try:
        next_page_url = (
                f"/orgs/{client.owner}/secret-scanning/alerts"
                f"?per_page=100&state=open"
            )
        has_next_page = True

        while has_next_page:
            response = client.make_request("GET", next_page_url)
            response_secret_scanning_alerts = response.json()

            if isinstance(response_secret_scanning_alerts, list):
                secret_scanning_alerts.extend(response_secret_scanning_alerts)
            else:
                return {
                        "result": "error",
                        "message": f"API response does not contain a list of Secret Scanning alerts.",
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
    for alerts in secret_scanning_alerts.items():
        for alert in alerts:
            if _exceeds_slo(alerts, now):
                exceeded_alerts.append(alert)

    total_open_alerts = len(exceeded_alerts)

    if total_open_alerts == 0:
        return {
            "result": "pass",
            "message": "No open Secret Scanning security alerts found exceeding SLO.",
            "details": {
                "total_open_alerts": total_open_alerts,
            },
        }

    return {
        "result": "fail",
        "message": f"Found {total_open_alerts} open Secret Scanning security alerts exceeding the policy-defined SLO.",
        "details": {
            "total_open_alerts": total_open_alerts,
            "failing_alerts": exceeded_alerts,
        },
    }
