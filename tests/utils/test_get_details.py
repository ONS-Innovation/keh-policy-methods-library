"""Tests for get_repo_details function"""

from policy_methods_library.github.clients import GitHubRestClient

from policy_methods_library.utils import get_details

from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# get_repo_details
# ---------------------------------------------------------------------------


class Test_Utils_Get_Details:
    """Tests for get_repo_details function in utils module."""

    def test_error_when_repository_name_is_empty(self):
        """Test get_repo_details returns fail when repository name is empty.
        using a mock for GitHub client"""

        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "test-owner"

        # Call the get_repo_details function with an empty repository name
        results = get_details.get_repo_details(github_client=client, repository_name="")
        # Assert that the details indicate failure due to empty repository name

        assert results["result"] == "error"
        assert results["message"] == "Repository name is required."
        assert results["details"] == {}

    def test_error_when_github_client_is_not_instance_of_githubrestclient(self):
        """Test get_repo_details returns fail when GitHub client is not an instance of GitHubRestClient."""
        # Call the get_repo_details function with a non-GitHubRestClient GitHub client
        results = get_details.get_repo_details(
            github_client={}, repository_name="test-repo"
        )
        # Assert that the details indicate failure due to None GitHub client

        assert results["result"] == "error"
        assert results["message"] == "GitHubRestClient instance is required."
        assert results["details"] == {}

    def test_error_when_response_is_not_valid_json_object(self):
        """Test get_repo_details returns fail when API response is not a valid JSON object.
        using a mock for GitHub client"""

        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "test-owner"

        mock_response = MagicMock()
        # mock_response.json.return_value = {"invalid": "response"}

        client.make_request = MagicMock(return_value=mock_response)
        client.make_request.side_effect = Exception(
            "API response is not a valid JSON array."
        )

        # Call the get_repo_details function
        result = get_details.get_repo_details(
            github_client=client, repository_name="test-repo"
        )
        # Assert that the details indicate failure due to API error

        assert result["result"] == "error"
        assert (
            result["message"]
            == "An error occurred while fetching repository details: API response is not a valid JSON array."
        )
        assert result["details"] == {}

    def test_get_repo_details_success(self):
        """Test get_repo_details returns pass when API request is successful.
        Mock the GitHub client to return a successful response"""

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

        get_details.get_repo_details.make_request = MagicMock(
            return_value=mock_response
        )

        result = get_details.get_repo_details(
            github_client=client, repository_name="test-repo"
        )

        # Assert that the details indicate success and contain the expected data

        assert result["result"] == "pass"
        assert result["message"] == "Repository details retrieved successfully."
        assert result["details"] == {
            "repository_name": "test-repo",
            "repository_details": {
                "id": 123,
                "name": "test-repo",
                "private": True,
                "visibility": "private",
            },
        }
