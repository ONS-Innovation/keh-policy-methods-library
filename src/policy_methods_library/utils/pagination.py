"""Utilities for handling paginated GitHub API responses."""

from typing import Any

from policy_methods_library.github.clients import GitHubRestClient


def get_paginated_list(
    github_client: GitHubRestClient,
    initial_endpoint: str,
    list_name: str,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch a paginated GitHub endpoint expected to return list payloads.

    Args:
        github_client: GitHub REST client used to make API calls.
        initial_endpoint: Initial relative endpoint path to request.
        list_name: Human-readable label used in validation error messages.

    Returns:
        On success: Aggregated list across all pages.
        On error: {
            "error": "<message>",
            "response": <payload>  # only for unexpected non-list payloads
        }
    """

    if not isinstance(github_client, GitHubRestClient):
        return {"error": "GitHubRestClient instance is required."}

    if not isinstance(initial_endpoint, str) or initial_endpoint.strip() == "":
        return {"error": "Initial endpoint is required."}

    if not isinstance(list_name, str) or list_name.strip() == "":
        return {"error": "List name is required."}

    items: list[dict[str, Any]] = []
    next_page_url = initial_endpoint

    try:
        while True:
            response = github_client.make_request("GET", next_page_url)
            response_items = response.json()

            if not isinstance(response_items, list):
                return {
                    "error": f"API response does not contain a list of {list_name}.",
                    "response": response_items,
                }

            items.extend(response_items)

            if response.links and "next" in response.links:
                next_page_url = response.links["next"]["url"].replace(
                    "https://api.github.com", ""
                )
            else:
                break

        return items

    except Exception as e:
        return {"error": str(e)}