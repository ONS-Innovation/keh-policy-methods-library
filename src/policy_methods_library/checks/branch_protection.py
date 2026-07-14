"""This module contains a check to verify that branch protection is enabled"""
from policy_methods_library.github.clients import GitHubRestClient
import requests


def check_branch_protection(
    client: GitHubRestClient,
    repository_name: str,
    branch_name: str
) -> dict:
    """Check if a GitHub repository has branch protection enabled."""

    if client is None:
        return {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    if repository_name is None:
        return {
            "result": "error",
            "message": "Repository name is required if data is not provided.",
            "details": {},
        }

    try:
        response = client.make_request(
            "GET",
            f"/repos/{client.owner}/{repository_name}/branches/{branch_name}/protection",
        )
        data = response.json()
        return {
            "result": "pass",
            "message": f"Branch protection is enabled for the '{branch_name}' branch of repository '{repository_name}'.",
            "details": {
                "required_status_checks": data.get("required_status_checks"),
                "enforce_admins": data.get("enforce_admins", {}).get("enabled", False),
                "required_pull_request_reviews": data.get("required_pull_request_reviews"),
                "restrictions": data.get("restrictions"),
            },
        }
    except requests.exceptions.HTTPError as e:
        response = client.make_request(
            "GET",
            f"/repos/{client.owner}/{repository_name}/branches/{branch_name}"
        ).json()
        
        if not response["protected"]:
            return {
                "result": "fail",
                "message": f"Branch protection is not enabled for branch {branch_name}"
            }
        else:
            response = client.make_request(
                "GET",
                f"/repos/{client.owner}/{repository_name}/rules/branches/{branch_name}"
            ).json()

            criteria = {
                        "restrict_deletions": False,
                        "review_before_merge": False,
                    }

            for rule in response:
                match rule["type"]:
                    case "deletion":
                        criteria["restrict_deletions"] = True
                    case "pull_request":
                        require_code_owner_review = rule["parameters"]["require_code_owner_review"]
                        required_approving_review_count = rule["parameters"]["required_approving_review_count"]

                        if require_code_owner_review and required_approving_review_count >= 2:
                            criteria["review_before_merge"] = True
                    case _:
                        pass
            
            if criteria["restrict_deletions"]:
                return {
                    "result": "fail",
                    "message": "Branch deletions must be restricted",
                    "details": {
                        "Repository": repository_name,
                        "Branch": branch_name,
                    }
                }
            
            if criteria["review_before_merge"]:
                return {
                    "result": "fail",
                    "message": "Review before merge must be enabled",
                    "details": {
                        "Repository": repository_name,
                        "Branch": branch_name,
                    }
                }

            return {
                "result": "pass",
                "message": "Branch is protected",
                "details": {
                    "Repository": repository_name,
                    "Branch": branch_name,
                }
            }
        
        return {
            "result": "error",
            "message": f"An error occurred while checking repository access: {str(e)}",
            "details": {},
        }
    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while checking repository access: {str(e)}",
            "details": {},
        }