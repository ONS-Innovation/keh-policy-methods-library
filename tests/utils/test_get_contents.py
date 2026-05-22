from policy_methods_library.utils import get_contents
from unittest.mock import MagicMock


"Tests for get_contents function"
# ---------------------------------------------------------------------------
# get_contents
# ---------------------------------------------------------------------------


class TestCheckGetContents:
    """Tests for get_contents function in pirr_checks module."""

    mock_github_client = MagicMock()

    def test_get_repo_contents_no_repository_name(self):
        """Test get_repo_contents returns fail when repository name is empty."""
        # Mock the GitHub client

        # Call the get_repo_contents function with an empty repository name
        contents = get_contents.get_repo_contents(
            github_client=self.mock_github_client,
            repository_name="",
        )

        # Assert that the contents indicate failure due to empty repository name
        assert contents["result"] == "fail"
        assert contents["message"] == "Repository name cannot be empty."
        assert contents["details"]["repository_name"] == ""

    def test_get_repo_contents_failure(self):
        """Test get_repo_contents returns fail when repository contents cannot be retrieved."""
        # Mock the GitHub client to return None
        mock_github_client = MagicMock()
        mock_github_client.make_request.return_value = None

        # Call the get_repo_contents function with the mocked client
        contents = get_contents.get_repo_contents(
            github_client=mock_github_client,
            repository_name="test-repo",
        )

        # Assert that the contents indicate failure due to inability to retrieve contents
        assert contents != {}
        assert contents["result"] == "fail"
        assert contents["message"] == "Unable to retrieve repository contents."
        assert contents["details"]["repository_name"] == "test-repo"

    def test_get_repo_contents_success(self):
        """Test get_repo_contents returns correct contents on success."""
        # Mock the GitHub client and its make_request method
        mock_github_client = MagicMock()
        mock_github_client.make_request.return_value = '{"name": "test-repo", "entries": [{"name": "src"}, {"name": "README.md"}, {"name": "LICENSE"}, {"name": "setup.py"}]}'

        # Call the get_repo_contents function with the mocked client

        contents = get_contents.get_repo_contents(
            github_client=mock_github_client,
            repository_name="test-repo",
        )

        # Assert that the contents are as expected
        assert contents != {}
        assert contents["name"] == "test-repo"
        assert len(contents["entries"]) == 4
        assert contents["entries"][0]["name"] == "src"

    def test_get_repo_contents_success_with_json_method(self):
        """Test get_repo_contents uses response.json() when available."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "name": "test-repo",
            "entries": [
                {"name": "src"},
                {"name": "README.md"},
                {"name": "LICENSE"},
                {"name": "setup.py"},
            ],
        }

        mock_github_client = MagicMock()
        mock_github_client.make_request.return_value = mock_response

        contents = get_contents.get_repo_contents(
            github_client=mock_github_client,
            repository_name="test-repo",
        )

        assert contents == mock_response.json.return_value
        assert contents["name"] == "test-repo"
        assert len(contents["entries"]) == 4
        assert contents["entries"][1]["name"] == "README.md"
