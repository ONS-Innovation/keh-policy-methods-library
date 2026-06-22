# README Check

The README check verifies whether a repository contains a `readme.md` file at the top level of the repository.
This helps ensure that repositories include basic project documentation for contributors and users.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.3.5, in summary:

- All repositories should include a README file that provides an overview of the project, installation instructions, and usage guidelines.

## Check Criteria

- The check retrieves the top-level contents of the repository.
- If a file named `readme.md` is present, the check will pass.
- If `readme.md` is not present, the check will fail.
- If the repository contents cannot be retrieved, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.readme.check_readme

## Usage Example

```python
from policy_methods_library.checks.readme import check_readme
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

response = check_readme(client=client, repository_name=repository_name)

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

The check uses the `GET /repos/{owner}/{repo}/contents/` endpoint to retrieve the top-level contents of the repository and look for `readme.md`.

[GitHub Documentation :link:](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content)

### Required Permissions

This check requires the following GitHub App permissions:

- `contents: read` – Required to access repository file contents

## Details Object

The `details` object returned by this check contains the following fields:

- `repository_name`: The name of the repository that was checked.
- `required_file`: The name of the required file that was checked for (`readme.md`).