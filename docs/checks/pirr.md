# PIRR Checks

Private/Internal Repository Information (PIRR)
The PIRR check ensures that GitHub repositories adhere to ONS' PIRR conventiion, defined within the GitHub Usage Policy.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.3.3, in summary:

- Repositories are by default  public
- Repositories can be made private or intenal if there is a specific need/requirement then there should be a PIRR.md which includes this need/requirement

## Check Criteria

### repository details  / repository contents

| visability | private | pirr file    |
|:-----------|:--------|:-------------|
| public     | False   | not required |
| private    | True    | required     |
| internal   | True    | required     |

- The check will obtain the details for the repository.
- If the visibity is public then return pass PIRR is not required
If the visibility is either private or internal then the check will obtain the content of the repository and check for a pirr.md file
if found will return a success else return a fail
- any other combiniation will cause the check to error

## Reference

::: src.policy_methods_library.checks.pirr_checks.check_repo_visibility

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

repository_details = get_repo_details(client=client, repository_name="your_repository_name")
repository_conents = 

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

[GitHub Usage Policy :](https://github.com/ONSdigital/software-engineer-community/blob/master/Software%20Engineering%20Principles_Policies_Guidelines_Templates_Plans%20and%20more/Software%20Engineering%20Policies/GitHub%20Usage%20Policy.pdf)

[GitHub Documentation for repository details:](https://docs.github.com/en/rest/repos/contents?apiVersion=2026-03-10)

[GitHub Documentation for repository conents:](https://docs.github.com/en/rest/repos/contents?apiVersion=2026-03-10)
