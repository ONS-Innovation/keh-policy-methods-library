# FAQ and User Guide

This page answers common questions about using the Policy Methods Library, so teams can self-serve before reaching out for support.

## Start here

If you are new to the library, read these pages first:

- [Quickstart](quickstart.md) for setup and copy-paste usage snippets.
- [Checks Matrix](checks_matrix.md) for check scope, inputs, pass/fail conditions, and required permissions.

## What does this library do?

The library provides reusable policy checks for GitHub repositories and organisations, aligned to ONS GitHub Usage Policy.

Each check returns a standard result object:

```json
{
  "result": "pass" | "fail" | "error",
  "message": "Human-readable summary",
  "details": {}
}
```

Use `pass` and `fail` for policy outcomes, and `error` for operational issues (for example permissions, malformed inputs, or API/network failures).

## How do I install and start using the library?

Install from GitHub:

```bash
pip install git+https://github.com/ONS-Innovation/keh-policy-methods-library@<version>
```

Or use your package manager of choice:

```bash
# Poetry Example
poetry add git+https://github.com/ONS-Innovation/keh-policy-methods-library@<version>
```

Create a client and run a check:

```python
from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.checks.readme import check_readme

client = GitHubRestClient(
    owner="your_github_organisation",
    app_id="your_app_id",
    private_key="your_private_key",
)

result = check_readme(client=client, repository_name="your_repository")
print(result)
```

## Do I need a GitHub App or can I use a PAT?

Both are supported by `GitHubRestClient`:

- GitHub App credentials (`app_id` + `private_key` + `owner`)
- Direct token (`access_token` + `owner`)

GitHub App authentication is recommended for better permission scoping and governance.

## What is the difference between `fail` and `error`?

- `fail`: The check ran successfully and found policy non-compliance.
- `error`: The check could not complete reliably (for example missing inputs, missing permissions, API timeout, or unexpected response shape).

If you run checks in CI, treat `error` as an operational problem to investigate, not as a direct policy failure.

## Which checks are repository-level and which are organisation-level?

Repository-level checks:

- Naming Convention
- Inactivity
- README
- .gitignore
- License
- CODEOWNERS
- Dependabot enabled
- Security Scanning enabled
- Repository Access
- External Pull Requests
- PIRR

Organisation-level checks:

- Dependabot SLO
- Secret Scanning SLO
- Team Maintainer

## Why does the External Pull Request check flag some bots?

The check considers a pull request external if the author is not a member of the configured organisation.

`dependabot[bot]` is explicitly allowed.
Other bot accounts may be flagged unless they are organisation members.

## What counts as a valid CODEOWNERS file?

The check looks for `CODEOWNERS` in GitHub-recognised paths:

- `CODEOWNERS`
- `.github/CODEOWNERS`
- `docs/CODEOWNERS`

It must also contain non-whitespace content. An empty or whitespace-only file fails.

## Do README and license checks look for exact filenames?

- README check expects `readme.md` at repository top level (case-insensitive match).
- License check accepts `LICENSE`, `LICENSE.md`, or `LICENSE.txt` (case-insensitive match).

## Why does the License check pass for private repositories?

This behaviour is intentional. The policy requirement applies to public repositories, so private repositories pass this check as not applicable.

## Why does Security Scanning pass for private/internal repositories?

This behaviour is intentional. The check is policy-scoped to public repositories and returns pass for `private` and `internal` repositories.

## How are SLO checks calculated?

Both SLO checks use working-day calculations (Monday to Friday):

- Dependabot SLO: severity-based working-day thresholds
- Secret Scanning SLO: 5 working days

Alerts with missing or invalid `created_at` are treated as breaching SLO.

## Can I scope Dependabot SLO to selected severities?

Yes. You can pass `levels=[...]` to `get_dependabot_slo`.

Valid values:

- `critical`
- `high`
- `medium`
- `low`

Invalid values are ignored. If no valid values remain, all severities are checked.

## What are the most common setup/authentication issues?

Typical causes of `error` results:

- Client owner is not an organisation for org-level checks
- App/token lacks required permissions for specific endpoints
- App not installed in the target organisation
- Incorrect app private key format
- Network/API transient failures

See the [GitHub App permissions](github-app-permissions.md) page for the full permission set used across checks.

## How should I troubleshoot an `error` result?

Use this quick checklist:

1. Verify required inputs are present (`client`, repository name, team slug, or data payload).
2. Confirm `owner` is correct for the target check scope.
3. Confirm GitHub App installation and permissions.
4. Retry once for transient network/API errors.
5. Log both `message` and `details` to speed diagnosis.

## Is there one function to scan every repository automatically?

Not currently.

The library provides focused check functions. Typical usage is:

1. Enumerate repositories in your application.
2. Run the relevant checks per repository.
3. Aggregate and report results in your own format.

## How should I consume results in pipelines or dashboards?

Recommended handling:

- `pass`: compliant
- `fail`: non-compliant action needed
- `error`: operational issue (auth, permissions, API, malformed input)

Store full result payloads so teams can self-remediate from the `details` field without additional triage.
