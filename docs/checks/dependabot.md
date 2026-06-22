# Dependabot Check

The Dependabot Check verifies that Dependabot automated security fixes are enabled for a repository.
This helps ensure that repositories have automated dependency management and security updates, which are crucial for maintaining secure and up-to-date codebases.

## GitHub Usage Policy Origin

Based on GitHub Usage Policy, clause 5.5.2.4, in summary:

- All repositories must have Dependabot enabled.

## Check Criteria

- The check will analyse the `enabled` status of automated security fixes (Dependabot) for the repository.
- If Dependabot automated security fixes are enabled, the check will pass.
- If Dependabot automated security fixes are disabled, the check will fail.
- Should the `enabled` status be unavailable or not a boolean, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.dependabot.check_dependabot

## Usage Example

```python
from policy_methods_library.checks.dependabot import check_dependabot
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

response = check_dependabot(client=client, repository_name="your_repository_name")

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

The check will use the `GET /repos/{owner}/{repo}/automated-security-fixes` endpoint to retrieve the enabled status of Dependabot automated security fixes.

[GitHub Documentation :link:](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#check-if-dependabot-security-updates-are-enabled-for-a-repository)

### Required Permissions

This check requires the following GitHub App permissions:

- `administration: read` – Required to access repository administration settings
