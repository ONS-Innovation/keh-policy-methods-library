# GitHub App Permissions

When using this library, the functionality and quality of the data you can access is determined by the permissions granted to your GitHub App. The following table outlines the permissions required for various features of this library:

| Feature | Required Permissions |
| --------- | ---------------------- |
| CODEOWNERS Check | `contents: read` |
| Dependabot Check | `administration: read` |
| Dependabot SLO Check | `dependabot_alerts: read` |
| External Pull Request Check | `pull_requests: read`, `members: read` |
| .gitignore Check | `contents: read` |
| Inactivity Check | `metadata: read` |
| LICENSE Check | `contents: read` |
| Naming Convention Check | None (no API access required) |
| PIRR Check | `metadata: read`, `contents: read` |
| README Check | `contents: read` |
| Repository Access Check | `metadata: read` |
| Secret Scanning SLO Check | `secret_scanning_alerts: read` |
| Security Scanning Check | `administration: read` |
| Team Maintainer Check | `members: read` |

In summary, to unlock the full potential of this library, it is recommended to grant your GitHub App the following permissions:

- `contents: read`
- `administration: read`
- `dependabot_alerts: read`
- `pull_requests: read`
- `members: read`
- `metadata: read`
- `secret_scanning_alerts: read`

At the moment, this library does not need **any** write permissions to perform its checks.
