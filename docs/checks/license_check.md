# LICENSE Check

The LICENSE check verifies whether a repository contains a `license` file at the top level of the repository.
This helps ensure that repositories specify the terms of use for the project.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.3.6, in summary:

- A license file must be included in each public repository.

## Check Criteria

- The check retrieves the top-level contents of the repository.
- If a file named `license` or `license.md` or `license.txt` is present, the check will pass.
- If the `license` file is not present, the check will fail.
- If the repository is private, the check will pass as license file is not required for private repositories.
- If the repository contents cannot be retrieved, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.license.check_license

## Usage Example

```python
from policy_methods_library.checks.license import check_license
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

response = check_license(client=client, repository_name=repository_name)

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

The check uses the `GET /repos/{owner}/{repo}/contents/` endpoint to retrieve the top-level contents of the repository and look for `license.md`, `license.txt`, or `license`

[GitHub Documentation :link:](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content)

### Required Permissions

This check requires the following GitHub App permissions:

- `contents: read` – Required to access repository file contents

## Details Object

The `details` object returned by this check contains the following fields:

- `repository_name`: The name of the repository that was checked.
- `required_file`: The name of the required file that was checked for (`license`).
- `is_public` *(private repository pass only)*: Boolean indicating whether the repository is public. Will be `false` when the check passes due to the repository being private.
