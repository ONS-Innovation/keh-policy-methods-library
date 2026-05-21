from policy_methods_library.utils import get_details
from unittest.mock import MagicMock

"Tests for get_repo_details function"
# ---------------------------------------------------------------------------
# get_repo_details


class TestCheckGetDetails:
    """Tests for get_repo_details function in pirr_checks module."""

    from unittest.mock import MagicMock

    def test_get_repo_details_no_repository_name(self):
        """Test get_repo_details returns fail when repository name is empty."""
        # Mock the GitHub client
        mock_github_client = MagicMock()

        # Call the get_repo_details function with an empty repository name
        details = get_details.get_repo_details(
            github_client=mock_github_client,
            repository_name="",
        )

        # Assert that the details indicate failure due to empty repository name
        assert details["result"] == "fail"
        assert details["message"] == "Repository name cannot be empty."
        assert details["details"]["repository_name"] == ""

    def test_get_repo_details_success(self):
        """Test get_repo_details returns correct details on success."""
        # Mock the GitHub client and its make_request method
        mock_github_client = MagicMock()
        mock_github_client.make_request.return_value = {
            "name": "test-repo",
            "private": "true",
            "visibility": "internal",
        }

        # Call the get_details function with the mocked clientß
        details = get_details.get_repo_details(
            github_client=mock_github_client,
            repository_name="test-repo",
        )

        # Assert that the details are as expected
        assert details != {}
        assert details["name"] == "test-repo"
        assert details["private"] == "true"
        assert details["visibility"] == "internal"

    def test_get_repo_details_failure(self):
        """Test get_repo_details returns empty dict on failure."""
        # Mock the GitHub client to raise an exception

        mock_github_client = MagicMock()
        mock_github_client.make_request.return_value = None

        # Call the get_repo_details function with the mocked client
        details = get_details.get_repo_details(
            github_client=mock_github_client,
            repository_name="test-repo",
        )

        # Assert that the details is an empty dict
        assert details != {}
        assert details["result"] == "fail"
        assert details["message"] == "Repository not found."
        assert details["details"]["repository_name"] == "test-repo"
