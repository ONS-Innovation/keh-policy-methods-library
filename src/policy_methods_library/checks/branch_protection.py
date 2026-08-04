"""This module contains a check to verify that branch protection is enabled"""

from policy_methods_library.github.clients import GitHubRestClient
import requests


def check_branch_protection(
    client: GitHubRestClient, repository_name: str, branch_name: str
) -> dict:
    """Check if a GitHub repository has branch protection enabled.
    Fails if branch protection is not enabled on either the legacy endpoint or the new
    rulesets endpoint.

    First makes a request to the legacy endpoint for branch protection, if that fails
    it then moves onto the endpoint for rulesets.

    Branch protection may be defined on either of these two endpoints so it is important to check both.

    Args:
        client: An instance of the GitHubRestClient to use for API calls.
        repository_name: The name of the repository to check.
        branch_name: The name of the branch to check.
    
    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error), 'message', and 'details'.
    """

    if client is None:
        return {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    if repository_name is None:
        return {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    if branch_name is None:
        return {
            "result": "error",
            "message": "Branch name is required.",
            "details": {},
        }

    criteria = {
        "restrict_deletions": False,
        "review_before_merge": False,
    }

    try:
        # First check legacy branch protection if that is enabled for the repository
        return check_legacy_branch_protection(client, repository_name, branch_name, criteria)
    except requests.exceptions.HTTPError:
        # If legacy branch protection does not exist for the repository, then check the
        # rulesets protection.
        return check_rulesets_branch_protection(client, repository_name, branch_name, criteria)
    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while checking repository access: {str(e)}",
            "details": {},
        }

def check_legacy_branch_protection(client, repository_name, branch_name, criteria):
    response = client.make_request(
            "GET",
            f"/repos/{client.owner}/{repository_name}/branches/{branch_name}/protection",
        )
    data = response.json()

    restrict_deletions = not data["allow_deletions"]["enabled"]
    require_code_owner_reviews = data["required_pull_request_reviews"][
        "require_code_owner_reviews"
    ]
    required_approving_review_count = data["required_pull_request_reviews"][
        "required_approving_review_count"
    ]

    if require_code_owner_reviews and required_approving_review_count >= 2:
        criteria["review_before_merge"] = True

    if restrict_deletions:
        criteria["restrict_deletions"] = True

    if not criteria["restrict_deletions"]:
        return message(
            "restrict_deletions",
            repository_name=repository_name,
            branch_name=branch_name,
        )

    if not criteria["review_before_merge"]:
        return message(
            "review_before_merge",
            repository_name=repository_name,
            branch_name=branch_name,
        )

    return {
        "result": "pass",
        "message": "Branch is protected",
        "details": {
            "Repository": repository_name,
            "Branch": branch_name,
        },
    }

def check_rulesets_branch_protection(client, repository_name, branch_name, criteria):
    response = client.make_request(
            "GET", f"/repos/{client.owner}/{repository_name}/branches/{branch_name}"
        ).json()

    if not response["protected"]:
        return {
            "result": "fail",
            "message": f"Branch protection is not enabled for branch {branch_name}",
            "details": {}
        }

    response = client.make_request(
        "GET",
        f"/repos/{client.owner}/{repository_name}/rules/branches/{branch_name}",
    ).json()

    for rule in response:
        match rule["type"]:
            case "deletion":
                criteria["restrict_deletions"] = True
            case "pull_request":
                require_code_owner_review = rule["parameters"][
                    "require_code_owner_review"
                ]
                required_approving_review_count = rule["parameters"][
                    "required_approving_review_count"
                ]

                if (
                    require_code_owner_review
                    and required_approving_review_count >= 2
                ):
                    criteria["review_before_merge"] = True
            case _:
                pass

    if not criteria["restrict_deletions"]:
        return message(
            "restrict_deletions",
            repository_name=repository_name,
            branch_name=branch_name,
        )

    if not criteria["review_before_merge"]:
        return message(
            "review_before_merge",
            repository_name=repository_name,
            branch_name=branch_name,
        )

    return {
        "result": "pass",
        "message": "Branch is protected",
        "details": {
            "Repository": repository_name,
            "Branch": branch_name,
        },
    }


def message(criterion: str, **kwargs) -> dict:
    """Return error message for the appropriate criterion"""

    if criterion == "review_before_merge":
        return {
            "result": "fail",
            "message": "Branch is not protected",
            "details": {
                "Repository": kwargs["repository_name"],
                "Branch": kwargs["branch_name"],
                "Details": "Review before merge must be enabled"
            },
        }

    if criterion == "restrict_deletions":
        return {
            "result": "fail",
            "message": "Branch is not protected",
            "details": {
                "Repository": kwargs["repository_name"],
                "Branch": kwargs["branch_name"],
                "Details": "Branch deletions must be restricted"
            },
        }

    return {
        "result": "fail",
        "message": "Branch is not protected",
        "details": {
            "Repository": kwargs["repository_name"],
            "Branch": kwargs["branch_name"],
            "Details": "Failed on unknown criterion"
        }
    }
