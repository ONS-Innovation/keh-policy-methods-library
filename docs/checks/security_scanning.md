# Security Scanning Check

The Security Scanning Check verifies that both Push Protection and Secret Scanning are enabled for a repository.
This helps ensure that sensitive information (such as API keys, tokens, and credentials) cannot be accidentally committed to the repository and is actively monitored for leaks.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clauses 5.5.2.2 and 5.5.2.3, in summary:

- Push Protection must be enabled for all public repositories.
- Secret Scanning must be enabled for all public repositories.

> Note: This only applies to public repositories, as enabling these features for private repositories will incur additional costs for the organisation due to GitHub Advanced Security licensing.

## Check Criteria

- The repository visibility must be available (`visibility` field).
- The check will analyse the `security_and_analysis` block of the repository settings.
- If the repository visibility is `private` or `internal`, the check will return `pass` because this policy is not applicable.
- If both `secret_scanning_push_protection` and `secret_scanning` have their status set to `enabled`, the check will pass.
- If either feature is disabled or missing, the check will fail.
- Should the `visibility` or `security_and_analysis` fields be unavailable, or if `security_and_analysis` is malformed, the check will return an error status.

## Reference

::: src.policy_methods_library.checks.security_scanning.check_security_scanning

## Usage Example

### With Data Passed Directly

```python
from policy_methods_library.checks.security_scanning import check_security_scanning

# Collect Data (In a real implementation, this data would likely come from another API call).

data = {
    "visibility": "public",
    "security_and_analysis": {
        "secret_scanning_push_protection": {"status": "enabled"},
        "secret_scanning": {"status": "enabled"},
    }
}

# Run Check with Data Passed Directly

response = check_security_scanning(data=data)

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
        details = response.get("details")
        print(f"Push Protection Enabled: {details.get('push_protection_enabled')}")
        print(f"Secret Scanning Enabled: {details.get('secret_scanning_enabled')}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

### With Data Retrieval

```python
from policy_methods_library.checks.security_scanning import check_security_scanning
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

response = check_security_scanning(client=client, repository_name="your_repository_name")

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
        details = response.get("details")
        print(f"Push Protection Enabled: {details.get('push_protection_enabled')}")
        print(f"Secret Scanning Enabled: {details.get('secret_scanning_enabled')}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## GitHub Integration Used

If the data is not passed directly, the check will use the `GET /repos/{owner}/{repo}` endpoint to retrieve the repository's security and analysis settings.

[GitHub Documentation :link:](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#get-a-repository)

## Details Object

For applicable public repositories, the `details` object returned by this check contains the following fields:

- `push_protection_enabled`: Boolean indicating whether Push Protection is currently enabled for the repository.
- `secret_scanning_enabled`: Boolean indicating whether Secret Scanning is currently enabled for the repository.
- `security_and_analysis`: The full `security_and_analysis` block retrieved from the GitHub API, which may contain additional security features beyond Push Protection and Secret Scanning.

For non-applicable repositories (`private` and `internal`), the `details` object contains:

- `visibility`: The repository visibility used to determine that the check is not applicable.
