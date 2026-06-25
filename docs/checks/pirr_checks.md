# PIRR Check

The PIRR check verifies whether private and internal repositories include a `pirr.md` file at the top level of the repository.
This helps ensure that non-public repositories include documented justification in line with ONS policy.

PIRR stands for "Private/Internal Repository Reasoning Record" and is a document that should be included in private or internal repositories to provide reasoning for their non-public status.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.3.3, in summary:

- Repositories are public by default.
- Repositories may be private or internal only where there is a specific requirement, documented in `pirr.md`.

## Check Criteria

- The check retrieves repository details to determine visibility and privacy settings.
- If visibility is `public`, the check passes without further action. This is because public repositories do not require a `pirr.md` file.
- If visibility is `private` or `internal`: 
  - Repository contents are retrieved to check for the presence of `pirr.md` at the top level.
  - If `pirr.md` is found, the check passes.
  - If `pirr.md` is not found, the check fails.
- If repository details or contents cannot be retrieved, or visibility/privacy values are inconsistent, the check returns an error status.

## Reference

::: src.policy_methods_library.checks.pirr.check_pirr

## Usage Example

```python
from policy_methods_library.checks.pirr import check_pirr
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

response = check_pirr(client=client, repository_name=repository_name)

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

- `GET /repos/{owner}/{repo}` to retrieve repository details.

[GitHub Documentation for repository details :link:](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository)

- `GET /repos/{owner}/{repo}/contents/` to retrieve top-level repository contents.

[GitHub Documentation for repository contents :link:](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content)

### Required Permissions

This check requires the following GitHub App permissions:

- `metadata: read` – Required to access repository visibility and privacy settings
- `contents: read` – Required to access top-level repository contents and check for `pirr.md`

## Details Object

The `details` object returned by this check can contain the following fields:

- `repository_name`: The name of the repository that was checked.
- `repository_details`: Repository metadata returned from the repository details endpoint, including fields such as `visibility` and `private`.
- `repository_contents`: The top-level repository contents returned by the contents endpoint. This field is included when content lookup is attempted for private/internal repositories.
