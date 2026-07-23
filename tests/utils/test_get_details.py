"""Tests for get_repo_details utility function."""

from unittest.mock import MagicMock

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils import get_details


class TestUtilsGetDetails:
    """Tests for get_repo_details function in utils module."""

    def test_error_when_repository_name_is_empty(self):
        """An empty repository name should return an error object."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "test-owner"

        result = get_details.get_repo_details(github_client=client, repository_name="")

        assert result == {"error": "Repository name is required."}

    def test_error_when_github_client_is_invalid(self):
        """Invalid client should return an error object."""
        result = get_details.get_repo_details(
            github_client={}, repository_name="test-repo"
        )

        assert result == {"error": "GitHubRestClient instance is required."}

    def test_error_when_api_request_fails(self):
        """API errors should be returned as an error object."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "test-owner"
        client.make_request = MagicMock(side_effect=Exception("request failed"))

        result = get_details.get_repo_details(
            github_client=client, repository_name="test-repo"
        )

        assert result == {
            "error": "An error occurred while fetching repository details: request failed"
        }

    def test_success_returns_raw_repository_details(self):
        """Successful requests should return raw repository details."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "test-owner"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 123,
            "name": "test-repo",
            "private": True,
            "visibility": "private",
        }

        client.make_request = MagicMock(return_value=mock_response)

        result = get_details.get_repo_details(
            github_client=client, repository_name="test-repo"
        )

        assert result == {
            "id": 123,
            "name": "test-repo",
            "private": True,
            "visibility": "private",
        }
