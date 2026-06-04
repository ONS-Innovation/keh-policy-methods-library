# ---------------------------------------------------------------------------
# pirr_checks
# ---------------------------------------------------------------------------

from unittest.mock import create_autospec, patch
from policy_methods_library.github.clients import GitHubRestClient

from policy_methods_library.checks import pirr_checks


class TestCheckPIRR:
    """Tests for check_repo_visibility function in pirr_checks module."""

    def test_repository_name_error_when_empty(self):
        """Test that the check fails when the repository name is empty."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        result = pirr_checks.check_repo_visibility(client, "")
        assert result["result"] == "error"
        assert result["message"] == "Repository name is required."
        assert result["details"] == {}

    def test_repository_name_error_when_none(self):
        """Test that the check fails when the repository name is None."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        result = pirr_checks.check_repo_visibility(client, None)
        assert result["result"] == "error"
        assert result["message"] == "Repository name is required."
        assert result["details"] == {}

    def test_client_error_when_not_required_format(self):
        """Test that the check fails when the client is not a GitHubRestClient instance."""
        client = "not_a_githubrestclient"
        result = pirr_checks.check_repo_visibility(client, "TestRepo")
        assert result["result"] == "error"
        assert result["message"] == "GitHubRestClient instance is required."
        assert result["details"] == {}

    def test_client_error_when_none(self):
        """Test that the check fails when the client is None."""
        client = None
        result = pirr_checks.check_repo_visibility(client, "TestRepo")
        assert result["result"] == "error"
        assert result["message"] == "GitHubRestClient instance is required."
        assert result["details"] == {}

    @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    def test_repository_visibility_public_success(self, mock_get_details):
        """Test that the check passes when the repository is public."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {
            "result": "pass",
            "message": f"Successfully retrieved details for repository '{repository_name}'.",
            "details": {"private": False, "visibility": "public"},
        }

        result = pirr_checks.check_repo_visibility(client, repository_name)
        assert result["message"] == "Repository is public."
        assert result["details"]["repository_name"] == "TestRepo"
        assert result["details"]["repository_details"] == {
            "private": False,
            "visibility": "public",
        }
        assert result["result"] == "pass"

        # Verify the mock was called with correct arguments
        mock_get_details.assert_called_once_with(client, repository_name)

    @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    def test_repository_public_error(self, mock_get_details):
        """Test that the check fails when get_repo_details raises an error."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        # Mock the return value for get_repo_details
        mock_get_details.side_effect = Exception("")

        result = pirr_checks.check_repo_visibility(client, repository_name)

        assert result["result"] == "error"
        assert result["details"] == {}
        assert (
            result["message"] == "An error occurred while fetching repository details: "
        )

        # Verify the mock was called with correct arguments
        mock_get_details.assert_called_once_with(client, repository_name)

    @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    @patch("policy_methods_library.checks.pirr_checks.get_repo_contents")
    def test_repository_private_success(self, mock_get_contents, mock_get_details):
        """Test that the check fails when the repository is private."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {"private": True, "visibility": "private"}

        # Mock the return value for get_contents to simulate .github directory exists
        mock_get_contents.return_value = [
            {"name": "README.md", "type": "file"},
            {"name": "PIRR.md", "type": "file"},
        ]

        result = pirr_checks.check_repo_visibility(client, repository_name)
        assert result["message"] == "Repositor contains PIRR documentation."
        assert result["details"]["repository_name"] == "TestRepo"
        assert result["details"]["repository_details"] == {
            "private": True,
            "visibility": "private",
        }

        assert result["details"]["repository_contents"][1]["name"] == "PIRR.md"
        assert result["result"] == "pass"

        # Verify the mocks were called with correct arguments
        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)

    @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    @patch("policy_methods_library.checks.pirr_checks.get_repo_contents")
    def test_repository_internal_success(self, mock_get_contents, mock_get_details):
        """Test that the check fails when the repository is internal."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {"private": True, "visibility": "internal"}

        # Mock the return value for get_contents to simulate .github directory exists
        mock_get_contents.return_value = [
            {"name": "README.md", "type": "file"},
            {"name": "PIRR.md", "type": "file"},
        ]

        result = pirr_checks.check_repo_visibility(client, repository_name)

        assert result["message"] == "Repositor contains PIRR documentation."
        assert result["details"]["repository_name"] == "TestRepo"
        assert result["details"]["repository_details"] == {
            "private": True,
            "visibility": "internal",
        }
        assert result["details"]["repository_contents"] is not None
        fileNames = [
            content.get("name").lower()
            for content in result["details"]["repository_contents"]
        ]

        assert "pirr.md" in fileNames
        assert result["result"] == "pass"

        # Verify the mocks were called with correct arguments
        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)

    @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    @patch("policy_methods_library.checks.pirr_checks.get_repo_contents")
    def test_repository_get_contents_error(self, mock_get_contents, mock_get_details):
        """Test that the check fails when get_repo_contents raises an error."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {"private": True, "visibility": "internal"}

        # Mock the return value for get_repo_contents
        mock_get_contents.side_effect = Exception("")

        result = pirr_checks.check_repo_visibility(client, repository_name)

        assert result["result"] == "error"
        assert result["details"] == {}
        assert (
            result["message"]
            == "An error occurred while fetching repository contents: "
        )

        # Verify the mock was called with correct arguments
        mock_get_details.assert_called_once_with(client, repository_name)

    @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    @patch("policy_methods_library.checks.pirr_checks.get_repo_contents")
    def test_repository_details_private_no_pirr_file_error(
        self, mock_get_contents, mock_get_details
    ):
        """Test that the check fails when the repository is private."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {"private": True, "visibility": "private"}

        # Mock the return value for get_contents to simulate .github directory exists
        mock_get_contents.return_value = [
            {"name": "README.md", "type": "file"},
            {"name": "CODE_OF_CONDUCT.md", "type": "file"},
        ]

        result = pirr_checks.check_repo_visibility(client, repository_name)
        assert result["message"] == "Repository does not contain PIRR documentation."
        assert result["details"]["repository_name"] == "TestRepo"
        assert result["details"]["repository_details"] == {
            "private": True,
            "visibility": "private",
        }
        fileNames = [
            content.get("name").lower()
            for content in result["details"]["repository_contents"]
        ]
        assert "pirr.md" not in fileNames
        assert result["result"] == "fail"

        # Verify the mocks were called with correct arguments
        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)
