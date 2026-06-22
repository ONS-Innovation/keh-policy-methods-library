# Team Maintainer Check

The Team Maintainer Check verifies that a GitHub Team has at least one maintainer.
This helps ensure that all teams within the organisation have clear ownership and management structure.

## GitHub Usage Policy Origin

Based on GitHub Usage Policy, clause 5.4.2, in summary:

- All teams within the GitHub organisation must have a member with the maintainer role.

## Check Criteria

- The check will retrieve all members of the specified team with the maintainer role using the GitHub API.
- If the team has at least one maintainer, the check will pass.
- If the team has zero maintainers, the check will fail.
- Should the API request fail or return unexpected data, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.team_maintainer.check_team_maintainer

## Usage Example

```python
from policy_methods_library.checks.team_maintainer import check_team_maintainer
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

response = check_team_maintainer(client=client, team_slug="your_team_slug")

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
        details = response.get("details")
        maintainers = details.get("maintainers", [])
        print(f"Team maintainers: {maintainers}")
    case "fail":
        print(f"Check Failed: {message}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## GitHub Integration Used

The check uses the `GET /orgs/{org}/teams/{team_slug}/members` endpoint with the `role=maintainer` query parameter to retrieve all maintainers of the specified team.

[GitHub Documentation :link:](https://docs.github.com/en/rest/teams/members?apiVersion=2026-03-10#list-team-members)

### Required Permissions

This check requires the following GitHub App permissions:

- `members: read` – Required to access team membership and maintainer information

## Details Object

The `details` object returned by this check contains the following fields:

- `team_slug`: The slug identifier of the team that was checked.
- `maintainer_count`: Integer indicating the number of maintainers found for the team.
- `maintainers`: Array of maintainer objects, each containing:
  - `login`: The username/login of the maintainer.
  - `id`: The unique identifier of the maintainer.
