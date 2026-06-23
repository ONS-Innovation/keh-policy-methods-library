# Secret Scanning SLO Check

The Secret Scanning SLO Check verifies that open Secret Scanning alerts are resolved within the policy-defined SLO of 5 days.
This helps ensure that potential security vulnerabilities detected by GitHub's secret scanning are addressed promptly to minimise exposure risk.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.5.3, in summary:

- All secret scanning alerts must be resolved within 5 days of alert creation (based on policy defined SLO).

## Check Criteria

- The check will fetch all open Secret Scanning alerts for an organisation using the GitHub API.
- For each alert, it will examine the `created_at` timestamp to determine how long the alert has been open.
- If an alert was created more than 5 days ago (relative to the current time), it is considered as exceeding the SLO and contributes to a failed check.
- Alerts with missing or invalid `created_at` timestamps are treated as exceeding the SLO (conservative approach).
- If no open alerts exceed the 5-day SLO, the check will pass.
- If one or more alerts exceed the SLO, the check will fail and provide details about the failing alerts and affected repositories.
- Should there be any issues verifying the organisation or fetching alerts, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.secret_scanning_slo.get_secret_scanning_slo

## Usage Example

### With Data Retrieval

```python
from policy_methods_library.checks.secret_scanning_slo import get_secret_scanning_slo
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

# Run Check with Data Retrieval

response = get_secret_scanning_slo(client=client)

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
        details = response.get("details")
        print(f"Total Open Alerts: {details.get('total_open_alerts')}")
        print(f"Alerts Exceeding SLO: {details.get('failing_alerts')}")
        print(f"Repositories Affected: {details.get('total_repositories_affected')}")
        print(f"Repository Details: {details.get('repositories')}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

### Required Permissions

This check requires the following GitHub App permissions:

- `secret_scanning: read` – Required to access secret scanning alerts for the organisation

## Details Object

When the check returns a failure, the `details` field includes the following information:

- `total_open_alerts`: The total number of open Secret Scanning alerts in the organisation.
- `failing_alerts`: The number of alerts that exceed the 5-day SLO.
- `total_repositories_affected`: The count of unique repositories that contain alerts exceeding the SLO.
- `repositories`: A dictionary mapping repository identifiers (in the format `{owner}/{repo}`) to the count of failing alerts in each repository.

## GitHub Integration Used

This check uses the following GitHub API endpoints:

- `GET /orgs/{owner}` – Verifies that the client is authenticated as an organisation account
- `GET /orgs/{owner}/secret-scanning/alerts?per_page=100&state=open` – Fetches all open secret scanning alerts for the organisation (paginated)

[GitHub Documentation :link:](https://docs.github.com/en/rest/secret-scanning/secret-scanning)
