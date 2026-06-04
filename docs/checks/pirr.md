# PIRR Checks

Private/Internal Repository Information (PIRR)
The PIRR check ensures that GitHub repositories adhere to ONS' PIRR conventiion, defined within the GitHub Usage Policy.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.3.3, in summary:

- Repositories are by default  public
- Repositories can be made private or intenal if there is a specific need/requirement then there should be a PIRR.md which includes this need/requirement

## Check Criteria

### repository details  

| visability | private |
| :-------- | :------: |
| public | False |
| private | True |
| internal | True |

- The check will retrieve the repository details using the GitHub API function in utils get_details
- if the repository details for visibilty are public and the repository details for private are False
then the check will return

| Key | Contents |
| :-------- | :------: |
| result | pass |
| message | Repository is public. |
| details | repository_name |
| | repository_details |

- if the repository details private are True, details and visability is either "private" or "internal"
  - The check will retrieve the repository contents
  - if the contents has a pirr.md file
then the check will return

| Key | Contents |
| :-------- | :------: |
| result | pass |
| message | PIRR file is pres. |
| details | repository_name |
| | repository_details |
| | repository contents |

- if the repository details private =True or repository details.visability is either "Private" or "internal", the contents does not have a pirr.md file
then the check will return

| Key | Contents |
| :-------- | :------: |
| result | fail |
| message | Repository is public. |
| details | repository_name |
| | repository_details |
| | repository contents |

- any other combiniation will cause the check to error

## Reference

::: src/policy_methods_library.checks.pirr_checks.check_repo_visibility

## Usage Examples

```python
from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.get_contents import get_repo_contents
from policy_methods_library.utils.get_details import get_repo_details
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

response = check_repository_access(client=client, repository_name="your_repository_name")

# Process response

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
        details = response.get("details")
        individual_collaborators = details.get("individual_collaborators", [])
        print(f"Individual collaborators found: {individual_collaborators}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## GitHub Integration Used

The check uses the fillowing :-

- `GET /repos/{owner}/{repo}/'
see utils get_details
  - Input the githubRestAPI Client and the repository name
  - Returns the repository details as json/dictionary

- 'GET /repos/{owner}/{repo}/contents/'
see utils/get_contents
  - Input the githubRestAPI Client and the repository name
  - Return  a list of files for the repository

## References

[GitHub Usage Policy :]{Software Engineering Principles_Policies_Guidelines_Templates_Plans and more/Software Engineering Policies/GitHub Usage Policy.pdf}

[GitHub Documentation for repository details:](https://docs.github.com/en/rest/repos/contents?apiVersion=2026-03-10)

[GitHub Documentation for repository conents:](https://docs.github.com/en/rest/repos/contents?apiVersion=2026-03-10)
