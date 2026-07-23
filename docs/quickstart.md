# Quickstart Guide

This quickstart shows the fastest path to running checks and handling results.

## 1. Install

```bash
pip install git+https://github.com/ONS-Innovation/keh-policy-methods-library@<version>
```

## 2. Create a GitHub client

Use GitHub App credentials (recommended):

```python
from policy_methods_library.github.clients import GitHubRestClient

client = GitHubRestClient(
    owner="your_github_organisation",
    app_id="your_app_id",
    private_key="your_private_key",
)
```

You can also use a token:

```python
from policy_methods_library.github.clients import GitHubRestClient

client = GitHubRestClient(
    owner="your_github_organisation",
    access_token="your_access_token",
)
```

> It is recommended that the credentials used to set up the client are stored and retrieved securely, for example using environment variables or a secrets manager. Avoid hard-coding credentials in your codebase.

## 3. Run a single repository check

```python
from policy_methods_library.checks.readme import check_readme

result = check_readme(client=client, repository_name="your_repository")
print(result)
```

Typical response shape:

```json
{
  "result": "pass",
  "message": "Repository 'your_repository' contains a readme.md file.",
  "details": {
    "repository_name": "your_repository",
    "required_file": "readme.md"
  }
}
```

> The `details` field contains check-specific information, which can be used to verify the check's outcome or for further processing. This is often unique to each check and may contain different fields depending on the check's purpose and implementation.
> Information on what `details` fields are returned for each check can be found in the individual check documentation pages under [Policy Checks](checks/overview.md).

## 4. Run multiple checks for one repository

```python
from policy_methods_library.checks.codeowners import check_codeowners
from policy_methods_library.checks.dependabot import check_dependabot
from policy_methods_library.checks.gitignore import check_gitignore
from policy_methods_library.checks.inactivity import check_inactivity
from policy_methods_library.checks.license import check_license
from policy_methods_library.checks.readme import check_readme
from policy_methods_library.checks.repository_access import check_repository_access
from policy_methods_library.checks.security_scanning import check_security_scanning

repository_name = "your_repository"

results = {
    "readme": check_readme(client=client, repository_name=repository_name),
    "gitignore": check_gitignore(client=client, repository_name=repository_name),
    "license": check_license(client=client, repository_name=repository_name),
    "codeowners": check_codeowners(client=client, repository_name=repository_name),
    "inactivity": check_inactivity(client=client, repository_name=repository_name),
    "security_scanning": check_security_scanning(client=client, repository_name=repository_name),
    "dependabot": check_dependabot(client=client, repository_name=repository_name),
    "repository_access": check_repository_access(client=client, repository_name=repository_name),
}

for name, response in results.items():
    print(name, response["result"], response["message"])
```

For some repository checks, you can also pass data directly (without making an API call):

```python
from policy_methods_library.checks.inactivity import check_inactivity
from policy_methods_library.checks.naming_convention import check_naming_convention
from policy_methods_library.checks.security_scanning import check_security_scanning

naming_result = check_naming_convention("example-repository")

inactivity_result = check_inactivity(
    data={"updated_at": "2025-08-01T10:30:00Z"}
)

security_result = check_security_scanning(
    data={
        "visibility": "public",
        "security_and_analysis": {
            "secret_scanning_push_protection": {"status": "enabled"},
            "secret_scanning": {"status": "enabled"},
        },
    }
)

print(naming_result["result"], naming_result["message"])
print(inactivity_result["result"], inactivity_result["message"])
print(security_result["result"], security_result["message"])
```

> This is useful if your application already has the required repository metadata. Lots of checks share common metadata, so you can avoid extra API requests by passing the data directly to multiple checks. See the individual check documentation pages for usage examples for data passthrough ([Policy Checks](checks/overview.md)).

## 5. Run organisation-level checks

```python
from policy_methods_library.checks.dependabot_slo import get_dependabot_slo
from policy_methods_library.checks.secret_scanning_slo import get_secret_scanning_slo
from policy_methods_library.checks.team_maintainer import check_team_maintainer

dependabot_slo_result = get_dependabot_slo(client=client)
secret_slo_result = get_secret_scanning_slo(client=client)
team_result = check_team_maintainer(client=client, team_slug="your_team_slug")

print(dependabot_slo_result["result"], dependabot_slo_result["message"])
print(secret_slo_result["result"], secret_slo_result["message"])
print(team_result["result"], team_result["message"])
```

To limit Dependabot SLO checks to specific severities:

```python
dependabot_slo_result = get_dependabot_slo(
    client=client,
    levels=["critical", "high"],
)
```

## 6. Recommended result handling

Use this pattern in scripts and CI:

```python
def handle_result(name: str, response: dict) -> None:
    result = response.get("result")
    message = response.get("message")

    if result == "pass":
        print(f"[PASS] {name}: {message}")
    elif result == "fail":
        print(f"[FAIL] {name}: {message}")
    elif result == "error":
        print(f"[ERROR] {name}: {message}")
    else:
        print(f"[UNKNOWN] {name}: {response}")
```

## 7. Next reference pages

- Check-by-check detail pages under [Policy Checks](checks/overview.md)
- Permission requirements: [GitHub App Permissions](github-app-permissions.md)
- Full matrix: [Checks Matrix](checks_matrix.md)
- Common questions and troubleshooting: [FAQ and User Guide](faq.md)
