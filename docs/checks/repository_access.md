# Repository Access Check

The Repository Access Check verifies that a repository's access permissions are managed through teams rather than direct individual user access.
This helps ensure that access control is organised, auditable, and follows best practices for collaborative development.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.5.3.1, in summary:

- Repository access should be granted to teams rather than individual users.

## Check Criteria

- The check will retrieve the list of direct collaborators for the repository using the GitHub API.
- If any collaborators with type `User` (individual users) are found, the check will fail.
- If all collaborators are teams or bots, the check will pass.
- Should the API request fail or return unexpected data, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.repository_access.check_repository_access

## Usage Example

```python
from policy_methods_library.checks.repository_access import check_repository_access
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

response = check_repository_access(client=client, repository_name="your_repository_name")

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
        details = response.get("details")
        individual_collaborators = details.get("individual_collaborators", [])
        print(f"Individual collaborators found: {individual_collaborators}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## GitHub Integration Used

The check uses the `GET /repos/{owner}/{repo}/collaborators` endpoint with `affiliation=direct` parameter to retrieve direct collaborators.

If `affiliation=direct` is not included, the response may include collaborators with indirect access through teams or organisation membership, which would not be relevant for this check.

This endpoint returns a list of collaborators with their access type and permissions.

[GitHub Documentation :link:](https://docs.github.com/en/rest/collaborators/collaborators?apiVersion=2026-03-10#list-repository-collaborators)

### Required Permissions

This check requires the following GitHub App permissions:

- `metadata: read` – Required to access repository collaborators
