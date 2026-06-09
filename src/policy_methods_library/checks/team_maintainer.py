"""This module contains a check to verify that GitHub teams have at least one maintainer."""

from policy_methods_library.github.clients import GitHubRestClient


def check_team_maintainer(
    client: GitHubRestClient,
    team_slug: str,
) -> dict:
    """Check if a GitHub team has at least one maintainer.

    Args:
        client: An instance of the GitHubRestClient to use for API calls. Required.
        team_slug: The slug identifier of the team to check (e.g., "frontend-team"). Required.

    Returns:
        A dictionary with the result of the check, including 'result' (pass/fail/error), 'message', and 'details'.
        Details contains the 'team_slug', 'maintainer_count', and 'maintainers' list.
    """

    if client is None:
        return {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    if not team_slug:
        return {
            "result": "error",
            "message": "Team slug is required.",
            "details": {},
        }

    try:
        # Note: Pagination is not required here as we only need to check if there is at least one maintainer.
        response = client.make_request(
            "GET",
            f"/orgs/{client.owner}/teams/{team_slug}/members?role=maintainer",
        )

        maintainers = response.json()

        # Verify that the API response contains a list of maintainers
        if not isinstance(maintainers, list):
            return {
                "result": "error",
                "message": "API response does not contain expected team members data.",
                "details": {"response": maintainers},
            }

        maintainer_count = len(maintainers)
        maintainer_list = [
            {"login": maintainer.get("login"), "id": maintainer.get("id")}
            for maintainer in maintainers
        ]

        if maintainer_count == 0:
            return {
                "result": "fail",
                "message": f"Team '{team_slug}' does not have any maintainers.",
                "details": {
                    "team_slug": team_slug,
                    "maintainer_count": maintainer_count,
                    "maintainers": maintainer_list,
                },
            }
        else:
            return {
                "result": "pass",
                "message": f"Team '{team_slug}' has {maintainer_count} maintainer(s).",
                "details": {
                    "team_slug": team_slug,
                    "maintainer_count": maintainer_count,
                    "maintainers": maintainer_list,
                },
            }

    except Exception as e:
        return {
            "result": "error",
            "message": f"An error occurred while checking team maintainers: {str(e)}",
            "details": {},
        }
