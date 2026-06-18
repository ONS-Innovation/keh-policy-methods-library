# Dependabot SLO Check

The Dependabot SLO Check verifies that all open Dependabot security alerts in an organisation are resolved, failing if any alerts remain open.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.5.4.

Where open Dependabot alerts must be resolved within defined SLOs:

| Severity | Timeframe      |
|----------|----------------|
| Critical | 5 days         |
| High     | 15 days        |
| Medium   | 60 days        |
| Low      | 90 days        |

## Check Criteria

- The check first verifies that the client is authenticated against an organisation account.
- The check retrieves all open Dependabot security alerts from the organisation (with automatic pagination support to handle organisations with many alerts).
- Alerts are grouped by severity level: critical, high, medium, and low.
- If no open Dependabot alerts are found, or all alerts are within their severity-level SLO, the check will pass.
- If one or more open Dependabot alerts exist that exceed their severity-level SLO, the check will fail.
- Alerts with missing or invalid `created_at` timestamps are treated as failures (exceeding SLO).
- Alerts created exactly at the SLO boundary are considered as exceeding the SLO.
- If the API requests fail or the response is malformed, the check will return an error status.

> Note: This check retrieves alerts across all severity levels by default. The severity levels checked can be customised by providing a custom list of severity values.
> The check returns the count and grouping of alerts by severity to help prioritise remediation efforts.

## Reference

::: src.policy_methods_library.checks.dependabot_slo.get_dependabot_slo

## Usage Example

```python
from policy_methods_library.checks.dependabot_slo import get_dependabot_slo
from policy_methods_library.github.clients import GitHubRestClient

# Setup GitHub Client

# Note: These credentials are placeholders. In a real implementation,
# you would securely retrieve these from your environment or a secrets manager.
app_id = "your_app_id"
private_key = "your_private_key"
github_organisation = "your_github_organisation"

client = GitHubRestClient(
    owner=github_organisation,
    app_id=app_id,
    private_key=private_key,
)

# Run Check

response = get_dependabot_slo(client=client)

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
        details = response.get("details")
        total_alerts = details.get("total_open_alerts", 0)
        by_severity = details.get("number_alerts_by_severity", {})
        print(f"Total open alerts: {total_alerts}")
        print(f"Alerts by severity: {by_severity}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## Customising Severity Levels

You can customise which severity levels to check by passing a `levels` parameter:

```python
# Check only critical and high severity alerts
response = get_dependabot_slo(
    client=client,
    levels=["critical", "high"]
)
```

## GitHub Integration Used

The check uses these GitHub API endpoints:

- `GET /orgs/{org}` to verify the client is authenticated as an organisation.

    [GitHub Documentation :link:](https://docs.github.com/en/rest/orgs/orgs?apiVersion=2026-03-10#get-an-organization)

- `GET /orgs/{org}/dependabot/alerts` to list open Dependabot security alerts in the organisation.

    [GitHub Documentation :link:](https://docs.github.com/en/rest/dependabot/alerts?apiVersion=2026-03-10#list-dependabot-alerts-for-an-organization)

## Details Object

The `details` object returned by this check contains:

- `total_open_alerts`: The total number of open Dependabot security alerts across all severity levels.
- `number_alerts_by_severity`: A dictionary showing the count of open alerts for each severity level (critical, high, medium, low).
- `failing_alerts`: (Only present when check fails) A dictionary containing the full list of open alerts grouped by severity level. Each alert object contains:
  - `number`: Alert identifier.
  - `state`: Alert state (e.g., "open").
  - `dependency`: Object containing the affected package name and version.
  - `security_advisory`: Object containing vulnerability details including CVE, severity, and description.
  - `security_update`: Object containing information about available security updates.
  - `url`: URL to the alert on GitHub.
  - `html_url`: Direct link to view the alert in the GitHub web interface.
  - `created_at`: Timestamp when the alert was created.
  - `updated_at`: Timestamp of the last update to the alert.
  - `dismissed_at`: Timestamp if the alert was dismissed (null if not dismissed).
  - `dismissed_by`: User who dismissed the alert (null if not dismissed).
  - `dismissed_reason`: Reason for dismissal if applicable.
  - `fixed_at`: Timestamp when the vulnerability was fixed (null if not yet fixed).
