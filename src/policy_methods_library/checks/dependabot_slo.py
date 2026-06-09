"""Checks that Dependabot security alerts are resolved within the policy-defined SLO."""

from policy_methods_library.github.clients import GitHubRestClient


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

                next_page_url = response.links.get("next", {}).get("url")

                if not next_page_url:
                    has_next_page = False

    except Exception as e:
        return {
            "result": "error",
            "message": f"Error fetching Dependabot alerts: {str(e)}.",
            "details": {},
        }

    number_alerts_by_severity = {
        level: len(alerts) for level, alerts in dependabot_alerts.items()
    }
    total_open_alerts = sum(number_alerts_by_severity.values())

    if total_open_alerts == 0:
        return {
            "result": "pass",
            "message": "No open Dependabot security alerts found.",
            "details": {
                "total_open_alerts": total_open_alerts,
                "number_alerts_by_severity": number_alerts_by_severity,
            },
        }

    return {
        "result": "fail",
        "message": f"Found {total_open_alerts} open Dependabot security alerts. Please resolve these alerts within the policy-defined SLO timeline.",
        "details": {
            "total_open_alerts": total_open_alerts,
            "number_alerts_by_severity": number_alerts_by_severity,
            "failing_alerts": dependabot_alerts,
        },
    }
