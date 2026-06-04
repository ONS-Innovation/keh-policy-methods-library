from policy_methods_library.utils import get_details
from unittest.mock import MagicMock

"Tests for get_repo_details function"
# ---------------------------------------------------------------------------
# get_repo_details
# ---------------------------------------------------------------------------


class Test_Utils_Get_Details:
    """Tests for get_repo_details function in utils module."""

    def test_get_repo_details_no_repository_name(self):
        """Test get_repo_details returns fail when repository name is empty."""
        # Mock the GitHub client
        mock_github_client = MagicMock()
        mock_github_client.owner = "test-owner"

        # Call the get_repo_details function with an empty repository name
        details = get_details.get_repo_details(
            github_client=mock_github_client, repository_name=""
        )
        # Assert that the details indicate failure due to empty repository name
        assert details["result"] == "error"
        assert details["message"] == "Repository name cannot be empty."
        assert details["details"]["repository_name"] == ""

    def test_get_repo_details_no_github_client(self):
        """Test get_repo_details returns fail when GitHub client is None."""
        # Call the get_repo_details function with a None GitHub client
        details = get_details.get_repo_details(
            github_client=None, repository_name="test-repo"
        )
        # Assert that the details indicate failure due to None GitHub client
        assert details["result"] == "error"
        assert details["message"] == "GitHub client cannot be None."
        assert details["details"]["github_client"] is None

    def test_get_repo_details_api_error(self):
        """Test get_repo_details returns fail when API request raises an exception."""
        # Mock the GitHub client to raise an exception when make_request is called
        mock_github_client = MagicMock()
        mock_github_client.owner = "test-owner"
        mock_github_client.make_request.side_effect = Exception("API error")

        # Call the get_repo_details function
        details = get_details.get_repo_details(
            github_client=mock_github_client, repository_name="test-repo"
        )
        # Assert that the details indicate failure due to API error
        assert details["result"] == "error"
        assert (
            details["message"]
            == "An error occurred while fetching repository details: API error"
        )
        assert details["details"] == {}

    def test_get_repo_details_success(self):
        """Test get_repo_details returns pass when API request is successful."""
        # Mock the GitHub client to return a successful response
        mock_github_client = MagicMock()
        mock_github_client.owner = "test-owner"
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 123, "name": "test-repo"}
        mock_github_client.make_request.return_value = mock_response

        # Call the get_repo_details function
        details = get_details.get_repo_details(
            github_client=mock_github_client, repository_name="test-repo"
        )
        # Assert that the details indicate success and contain the expected data
        assert details["result"] == "pass"
        assert (
            details["message"]
            == "Successfully retrieved details for repository 'test-repo'."
        )
        assert details["details"] == {"id": 123, "name": "test-repo"}

    def test_get_repo_details_invalid_json_response(self):
        """Test get_repo_details returns fail when API response is not a valid JSON object."""
        # Mock the GitHub client to return an invalid JSON response
        mock_github_client = MagicMock()
        mock_github_client.owner = "test-owner"
        mock_response = MagicMock()
        mock_response.json.return_value = "invalid-json"
        mock_github_client.make_request.return_value = mock_response

        # Call the get_repo_details function
        details = get_details.get_repo_details(
            github_client=mock_github_client, repository_name="test-repo"
        )
        # Assert that the details indicate failure due to invalid JSON response
        assert details["result"] == "error"
        assert details["message"] == "API response is not a valid JSON object."
        assert details["details"]["response"] == "invalid-json"
