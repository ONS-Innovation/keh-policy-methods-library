# External Pull Request Check

The External Pull Request Check verifies that all open pull requests in a repository are authored by members of the organisation that the client is associated with.
This helps ensure that repositories do not contain external pull requests that may require additional governance controls.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.5.6, in summary:

- Repositories containing external pull requests must not be merged.
- The unsolicited request should be raised to the Technical Lead or Senior member of the team for review and action.

## Check Criteria

- The check first verifies that the client is authenticated against an organisation account.
- The check retrieves open pull requests from the repository (with automatic pagination support to handle repositories with many open PRs).
- For each pull request author, the check verifies whether that user is a member of the organisation.
- If all pull request authors are organisation members, the check will pass.
- If one or more pull request authors are not organisation members, the check will fail.
- If the API requests fail or the response is malformed, the check will return an error status.

> Note: This check does not currently differentiate between internal and external contributors. Any pull request authored by a non-organisation member will be considered an external pull request.
> Additionally, pull requests raised by bots that are not organisation members will also be flagged as external pull requests, with Dependabot Pull Requests being the only exception.

## Reference

::: src.policy_methods_library.checks.external_pull_request.check_external_pull_request

## Usage Example

```python
from policy_methods_library.checks.external_pull_request import check_external_pull_request
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

# Run Check

response = check_external_pull_request(client=client, repository_name="your_repository_name")

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
        details = response.get("details")
        external_pull_requests = details.get("external_pull_requests", [])
        print(f"External pull requests found: {external_pull_requests}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## GitHub Integration Used

The check uses these GitHub API endpoints:

- `GET /orgs/{org}` to verify the client is authenticated as an organisation.

    [GitHub Documentation :link:](https://docs.github.com/en/rest/orgs/orgs?apiVersion=2026-03-10#get-an-organization)

- `GET /repos/{owner}/{repo}/pulls` to list open pull requests in the repository.

    [GitHub Documentation :link:](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#list-pull-requests)

- `GET /orgs/{org}/members/{username}` to verify whether each pull request author is an organisation member.

    [GitHub Documentation :link:](https://docs.github.com/en/rest/orgs/members?apiVersion=2026-03-10#check-organization-membership-for-a-user)

## Details Object

The `details` object returned by this check contains:

- `repository_name`: The repository that was checked.
- `open_pull_request_count`: The total number of open pull requests in the repository.
- `external_pull_requests`: A list of pull requests authored by non-organisation members.
  Each list item contains:
  - `number`: Pull request number.
  - `title`: Pull request title.
  - `author`: Pull request author username.
