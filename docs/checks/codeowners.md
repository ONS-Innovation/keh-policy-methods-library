# CODEOWNERS Check

The CODEOWNERS check verifies whether a repository contains a `CODEOWNERS` file in one of the locations recognised by GitHub.
This helps ensure that every repository has clearly defined code ownership, enabling GitHub to automatically request reviews from the appropriate owners when pull requests are opened.

## GitHub Usage Policy Origin

Based on GitHub Usage Policy, clause 5.3.4, in summary:

- All repositories must include a `CODEOWNERS` file that contains the GitHub Team name or GitHub ID(s) defining who is responsible for the repository.

## Check Criteria

- The check will look for a `CODEOWNERS` file in the following locations, in order:
  1. Repository root (`CODEOWNERS`)
  2. `.github/` directory (`.github/CODEOWNERS`)
  3. `docs/` directory (`docs/CODEOWNERS`)
- If a `CODEOWNERS` file is found in any of these locations and contains non-whitespace content, the check will pass.
- If a `CODEOWNERS` file is found but contains only whitespace (or is completely empty), the check will fail.
- If no `CODEOWNERS` file is found in any location, the check will fail.
- Should the API request fail for any reason other than a file not being present, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.codeowners.check_codeowners

## Usage Example

```python
from policy_methods_library.checks.codeowners import check_codeowners
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

response = check_codeowners(client=client, repository_name=repository_name)

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
        details = response.get("details")
        print(f"CODEOWNERS found at: {details.get('codeowners_path')}")
    case "fail":
        print(f"Check Failed: {message}")
        details = response.get("details")
        if details.get("codeowners_path"):
            print(f"Empty CODEOWNERS found at: {details.get('codeowners_path')}")
        else:
            print(f"Locations checked: {details.get('checked_paths')}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## GitHub Integration Used

The check uses the `GET /repos/{owner}/{repo}/contents/{path}` endpoint to probe each of the recognised CODEOWNERS locations.
A `404` response indicates the file is absent at that path; any other HTTP error is treated as an unexpected failure.

[GitHub Documentation :link:](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content)

### Required Permissions

This check requires the following GitHub App permissions:

- `contents: read` – Required to access repository file contents

## Details Object

The `details` object returned by this check contains the following fields:

- `repository_name`: The name of the repository that was checked.
- `codeowners_path` *(pass only)*: The path within the repository where the `CODEOWNERS` file was found (e.g. `CODEOWNERS`, `.github/CODEOWNERS`, or `docs/CODEOWNERS`).
- `checked_paths` *(fail only)*: The list of paths that were checked before the check determined no `CODEOWNERS` file exists.
