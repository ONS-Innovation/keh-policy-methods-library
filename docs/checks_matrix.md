# Checks Matrix

Use this matrix to choose checks quickly, understand required inputs, and troubleshoot common outcomes.

## Matrix

| Check | Function | Scope | Required Inputs | Optional Data-Only Mode | Pass Condition (Summary) | Fail Condition (Summary) | Required GitHub Permissions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Naming Convention | `check_naming_convention` | Repository | `repository_name` | Yes (native) | Name is lowercase, contains no spaces, and uses only letters, numbers, `-`, `_` | Name empty or violates naming rules | None |
| Inactivity | `check_inactivity` | Repository | `client` + `repository_name` | Yes (`data.updated_at`) | `updated_at` is within last 365 days | Repository has been inactive for over 365 days | `metadata: read` (API mode) |
| README | `check_readme` | Repository | `client` + `repository_name` | No | Top-level `readme.md` exists (case-insensitive) | `readme.md` not found | `contents: read` |
| .gitignore | `check_gitignore` | Repository | `client` + `repository_name` | No | Top-level `.gitignore` exists | `.gitignore` not found | `contents: read` |
| LICENSE | `check_license` | Repository | `client` + `repository_name` | No | Repo is private/internal, or public repo has `license`, `license.md`, or `license.txt` | Public repo missing licence file | `contents: read` |
| CODEOWNERS | `check_codeowners` | Repository | `client` + `repository_name` | No | Non-empty CODEOWNERS in `CODEOWNERS`, `.github/CODEOWNERS`, or `docs/CODEOWNERS` | Missing in all paths, or found but empty/whitespace | `contents: read` |
| Repository Access | `check_repository_access` | Repository | `client` + `repository_name` | No | No direct collaborators of type `User` | One or more direct individual users found | `metadata: read` |
| External Pull Request | `check_external_pull_request` | Repository | `client` + `repository_name` | No | All open PR authors are org members (plus `dependabot[bot]` exception) | One or more open PR authors are non-members | `pull_requests: read`, `members: read` |
| Security Scanning | `check_security_scanning` | Repository | `client` + `repository_name` | Yes (`data.visibility` + `data.security_and_analysis`) | Public repo has Push Protection and Secret Scanning enabled, or repo is private/internal (not applicable pass) | Public repo has one or both controls not enabled | `administration: read` (API mode) |
| Dependabot Enabled | `check_dependabot` | Repository | `client` + `repository_name` | No | `enabled == true` from automated security fixes endpoint | `enabled == false` | `administration: read` |
| Dependabot SLO | `get_dependabot_slo` | Organisation | `client` | No | No open alerts exceed severity SLO thresholds | One or more open alerts exceed SLO | `dependabot alerts: read` |
| Secret Scanning SLO | `get_secret_scanning_slo` | Organisation | `client` | No | No open secret scanning alerts exceed 5 working days | One or more open alerts exceed 5 working days | `secret_scanning: read` |
| Team Maintainer | `check_team_maintainer` | Organisation Team | `client` + `team_slug` | No | Team has at least one maintainer | Team has zero maintainers | `members: read` |

## Shared behaviour across all checks

- `result = pass`: check succeeded and policy condition is met.
- `result = fail`: check succeeded and policy condition is not met.
- `result = error`: check could not complete reliably (for example input, permission, auth, or API issues).

## Notes on SLO calculations

- Dependabot SLO and Secret Scanning SLO are calculated using working days (Monday to Friday).
- Alerts with missing or invalid `created_at` are treated as SLO breaches.

## Notes on permissions

- This library currently requires read-only permissions.
- If a check returns `error`, first verify GitHub App installation scope and permission grants.

## Further Information

For further details on each check, see:

- [Checks Overview](checks/overview.md)

> This section will contain links to each check's individual documentation page, which will provide more detailed information on the check's purpose, implementation, and usage.

For required GitHub App permissions across checks, see:

- [GitHub App Permissions](github-app-permissions.md)
