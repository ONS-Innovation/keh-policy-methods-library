# .gitignore Check

The .gitignore check verifies whether a repository contains a `.gitignore` file at the top level of the repository.
This helps ensure that generated files, environment files, and other non-source artifacts are not accidentally committed.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.3.7, in summary:

- Repositories should include a `.gitignore` file to prevent unnecessary files from being committed to the repository.

## Check Criteria

- The check retrieves the top-level contents of the repository.
- If a file named `.gitignore` is present, the check will pass.
- If `.gitignore` is not present, the check will fail.
- If the repository contents cannot be retrieved, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.gitignore.check_gitignore

## Usage Example

```python
from policy_methods_library.checks.gitignore import check_gitignore
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

response = check_gitignore(client=client, repository_name=repository_name)

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

The check uses the `GET /repos/{owner}/{repo}/contents/` endpoint to retrieve the top-level contents of the repository and look for `.gitignore`.

[GitHub Documentation :link:](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content)
