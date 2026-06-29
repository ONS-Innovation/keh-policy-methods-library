# PIRR Checks

Private/Internal Repository Resonig Record (PIRR)
The PIRR check ensures that GitHub repositories adhere to ONS' PIRR convention, defined within the GitHub Usage Policy.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.3.3, in summary:

- Repositories are by default public
- Repositories can be made private or intenal if there is a specific need/requirement then there should be a PIRR.md which includes this need/requirement

## Check Criteria

### repository details  / repository contents

| visability | private | pirr file    |
|:-----------|:--------|:-------------|
| public     | False   | not required |
| private    | True    | required     |
| internal   | True    | required     |

- The check will obtain the details for the repository.
- If the visibility is public then return pass PIRR is not required
- If the visibility is either private or internal then the check will obtain the content of the repository and check for a pirr.md file
if found will return a success else return a fail
- any other combiniation will cause the check to error

## Reference

::: src.policy_methods_library.checks.pirr.py

## Usage Examples

```python
    from policy_methods_library.github.clients import GitHubRestClient
    from policy_methods_library.utils.get_contents import get_repo_contents
    from policy_methods_library.utils.get_details import get_repo_details

    # example calls 
    
    repo_details = get_repo_details(client, repository_name)
    repo_contents = get_repo_contents(client, repository_name)

    # example queries from response 

    # finds any file with required name
    any(
                    content.get("name", "").lower() == "pirr.md"
                    for content in repo_contents["details"]["repository_contents"]
                )
    # eliminates public repositories
    (not repo_details["details"]["repository_details"]["private"] and
            repo_details["details"]["repository_details"]["visibility"].lower() == "public")

    example return
    return {
            "result": "pass",
            "message": "Repository contains PIRR documentation.",
            "details": {
                "repository_name": repository_name,
                "repository_details": repo_details["details"]       ["repository_details"],
                "repository_contents": repo_contents['details']['repository_contents'],
                        },
                    }
```

## GitHub Integration Used

The check uses the fillowing :-

- `GET /repos/{owner}/{repo}/`
see utils get_details
  - Input the githubRestAPI Client and the repository name
  - Returns the repository details as json/dictionary

- `GET /repos/{owner}/{repo}/contents/`
see utils/get_contents
  - Input the githubRestAPI Client and the repository name
  - Return a list of files for the repository

## References

[GitHub Usage Policy:](https://github.com/ONSdigital/software-engineer-community/blob/master/Software%20Engineering%20Principles_Policies_Guidelines_Templates_Plans%20and%20more/Software%20Engineering%20Policies/GitHub%20Usage%20Policy.pdf)

[GitHub Documentation for repository details:](https://docs.github.com/en/rest/repos/contents?apiVersion=2026-03-10)
