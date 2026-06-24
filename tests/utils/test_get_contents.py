"""Tests for get_repo_contents utility function."""

from unittest.mock import MagicMock
import requests
from requests import Response

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils import get_contents


class TestUtilsGetContents:
    """Tests for get_repo_contents in utils module."""

    def test_error_when_github_client_is_invalid(self):
        """Invalid client should return an error object."""
        result = get_contents.get_repo_contents(
            github_client={}, repository_name="my-repo"
        )

        assert result == {"error": "GitHubRestClient instance is required."}

    def test_error_when_repository_name_is_empty(self):
        """An empty repository name should return an error object."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "my-org"

        result = get_contents.get_repo_contents(
            github_client=client, repository_name=""
        )

        assert result == {"error": "Repository name is required."}

    def test_error_when_api_raises_exception(self):
        """API exceptions should be returned as an error object."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "test-owner"
        client.make_request = MagicMock(side_effect=Exception("request failed"))

        result = get_contents.get_repo_contents(
            github_client=client, repository_name="test-repo"
        )

        assert result == {
            "error": "An error occurred while fetching repository contents: request failed"
        }

    def test_success_returns_raw_contents_data(self):
        """Successful requests should return raw repository contents."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "test-owner"

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "file1.txt", "type": "file"},
            {"name": "dir1", "type": "dir"},
        ]
        client.make_request = MagicMock(return_value=mock_response)

        result = get_contents.get_repo_contents(
            github_client=client, repository_name="my-repo"
        )

        assert result == [
            {"name": "file1.txt", "type": "file"},
            {"name": "dir1", "type": "dir"},
        ]

    def test_success_with_path_uses_nested_contents_endpoint(self):
        """Providing path should request nested contents endpoint."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "test-owner"

        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "CODEOWNERS", "type": "file"}
        client.make_request = MagicMock(return_value=mock_response)

        result = get_contents.get_repo_contents(
            github_client=client,
            repository_name="my-repo",
            path=".github/CODEOWNERS",
        )

        client.make_request.assert_called_once_with(
            "GET", "/repos/test-owner/my-repo/contents/.github/CODEOWNERS"
        )
        assert result == {"name": "CODEOWNERS", "type": "file"}

    def test_http_error_includes_status_code(self):
        """HTTP errors should include a status_code field when available."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "test-owner"

        not_found = requests.HTTPError(
            response=MagicMock(spec=Response, status_code=404)
        )
        client.make_request = MagicMock(side_effect=not_found)

        result = get_contents.get_repo_contents(
            github_client=client,
            repository_name="my-repo",
            path="CODEOWNERS",
        )

        assert result["status_code"] == "404"
        assert "An error occurred while fetching repository contents" in result["error"]
