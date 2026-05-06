"""
This module contains the `GitHubRestClient` class, which provides methods for making REST API calls to GitHub.
It structures the API calls, handles authentication using the `get_access_token` function from the `auth` module, and provides a clean interface for interacting with GitHub's REST API.
"""

import requests
from typing import Optional
from .auth import get_access_token


class GitHubRestClient:
    """A client for making REST API calls to GitHub, authenticated as a GitHub App."""

    def __init__(
        self,
        app_id: Optional[str] = None,
        private_key: Optional[str] = None,
        organisation: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """Initialises the GitHubRestClient with credentials or a direct access token.

        Args:
            app_id (str, optional): The GitHub App's identifier.
            private_key (str, optional): The GitHub App's private key in PEM format.
            organisation (str, optional): The name of the GitHub organization.
            access_token (str, optional): A pre-generated GitHub access token.

        Raises:
            ValueError: If neither access_token nor all of app_id, private_key, and organisation are provided.
        """
        if access_token:
            self.access_token = access_token
        elif app_id and private_key and organisation:
            self.access_token = get_access_token(app_id, private_key, organisation)
        else:
            raise ValueError(
                "You must provide either an access_token or all of app_id, private_key, and organisation."
            )

    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Makes an authenticated request to the GitHub API.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint (e.g., '/repos/{owner}/{repo}').
            **kwargs: Additional arguments to pass to the `requests` method (e.g., json=data).

        Returns:
            requests.Response: The response from the GitHub API.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"https://api.github.com{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        request_headers = kwargs.pop("headers", None)

        if request_headers:
            headers.update(request_headers)

        kwargs.setdefault("timeout", 30)
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()  # Raise an error for bad responses
        return response
