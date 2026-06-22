# Inactivity Check

The Inactivity Check verifies that a repository has not been inactive (no updates or commits) for a year.
This helps ensure that repositories are actively maintained and not abandoned, which can be crucial for security and reliability.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.3.9, in summary:

- Repositories that have not been updated for a year should be archived by a Tech Lead / Senior Team Member.

## Check Criteria

- The check will analyse the `updated_at` timestamp of the repository.
- If this timestamp indicates that the repository has not been updated for more than a year, the check will fail.
- If the repository has been updated within the last year, the check will pass.
- Should the `updated_at` timestamp be unavailable, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.inactivity.check_inactivity

## Usage Example

### With Data Passed Directly

```python
from policy_methods_library.checks.inactivity import check_inactivity

# Collect Data (In a real implementation, this data would likely come from another API call).

data = {
    "updated_at": "2023-01-01T00:00:00Z"
}

# Run Check with Data Passed Directly

response = check_inactivity(data=data)

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

### With Data Retrieval

```python
from policy_methods_library.checks.inactivity import check_inactivity
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

response = check_inactivity(client=client, repository_name="your_repository_name")

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## GitHub Integration Used

If the data is not passed directly, the check will use the `GET /repos/{owner}/{repo}` endpoint to retrieve the `updated_at` timestamp of the repository.

[GitHub Documentation :link:](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#get-a-repository)

### Required Permissions

This check requires the following GitHub App permissions when retrieving data from the API:

- `metadata: read` – Required to access basic repository metadata

If the data is passed directly (as shown in the first usage example), no API permissions are required.
