# Branch Protection Check

The branch protection check ensures that a given branch is protected by checking that both
branch deletions are restricted and that there are at least two approved reviews before merging.
This helps ensure our branches are protected by enforcing stricter code reviews and making sure important branches are not mistakenly deleted.

## GitHub Usage Policy Origin

Based on GitHub Usage Policy, clause 5.4.8, in summary:

* Branch protection must be used, which includes both restricting deletions and enforcing code reviews.

## Legacy and Rulesets Endpoints

To check for branch protection, there are two possible endpoints to look at. The legacy endpoint and the rulesets endpoint. Branch protection may be defined in any of these two places. To ensure full coverage, the branch protection check looks at both.

## Check Criteria

* The check will make a request to the legacy endpoint for branch protection
* If the request to the legacy endpoint fails, it will make a second request to the rulesets endpoint for branch protection
* Whilst at either of these two endpoints, it will check if deletions are restricted and also check if there are at least two reviewers before merging for pull requests.
* If either of these criteria fail, the check will fail. Both need to be passing in order for the check to pass.

## Reference

::: src.policy_methods_library.checks.branch_protection.check_branch_protection

## Usage Example

```python
from policy_methods_library.checks.branch_protection import check_branch_protection
from policy_methods_library.github.clients import GitHubRestClient

# Setup GitHub Client

# Note: These credentials are placeholders. In a real implementation,
# you would securely retrieve these from your environment or a secrets manager.
app_id = "your_app_id"
private_key = "your_private_key"
github_organisation = "your_github_organisation"
repository_name = "your_repository_name"

client = GitHubRestClient(
    owner=github_organisation,
    app_id=app_id,
    private_key=private_key,
)

# Run Check

response = check_branch_protection(client, repository_name, branch_name)
result = response.get("result")
message = response.get("message")

match result
    case "pass":
        print(f"Check passed: {message}")
    case "fail":
        print(f"Check failed: {message}")
        details = result.get("details")
        details = details.get("Details")
        print(details)
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## GitHub Integration Used

The check uses the `GET /repos/{owner}/{repo}/branches/{branch}/protection` endpoint for the legacy branch protection check. If that fails, the check uses `GET /repos/{owner}/{repo}/rules/branches/{branch}`.

[GitHub Documentation: Protection API :link:](https://docs.github.com/en/rest/branches/branch-protection?apiVersion=2026-03-10#get-branch-protection)
[GitHub Documentation: Rulesets API :link:](https://docs.github.com/en/rest/repos/rules?apiVersion=2026-03-10#get-rules-for-a-branch)

## Required Permissions

The check requires the following GitHub App permissions:

* `"Administration" repository permissions (read)` - Required to access endpoint for legacy branch protection
* `"Metadata" repository permissions (read)` - Required to access endpoint for repository rulesets

## Details Object

The `details` object returned by this check contains the following fields:

* `repository`: The name of the repository that was checked.
* `branch`: The name of the branch that was checked.
* `criteria`: The specific details explaining why the branch is not protected (e.g restricted deletions, less than two reviewers).
