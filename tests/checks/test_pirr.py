"""Tests for the PIRR check module."""

from unittest.mock import create_autospec, patch

from policy_methods_library.checks import pirr
from policy_methods_library.github.clients import GitHubRestClient


class TestCheckPIRR:
    """Tests for check_pirr function."""

    def test_repository_name_error_when_empty(self):
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        result = pirr.check_pirr(client, "")

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_client_error_when_not_github_client(self):
        result = pirr.check_pirr("not_a_githubrestclient", "TestRepo")

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_success_for_public_repository(self, mock_get_contents, mock_get_details):
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {
            "visibility": "public",
        }

        mock_get_details.return_value = repository_details

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_not_called()
        assert result["result"] == "pass"
        assert (
            result["message"]
            == "Repository is public. PIRR documentation is not required."
        )
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_visibility"] == "public"

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_error_when_get_repo_details_returns_error(
        self, mock_get_contents, mock_get_details
    ):
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        mock_get_details.return_value = {
            "error": "An error occurred while fetching repository details: Invalid Json"
        }

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_not_called()
        assert result == {
            "result": "error",
            "message": "An error occurred while fetching repository details: Invalid Json",
            "details": {},
        }

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_error_when_get_repo_contents_returns_error(
        self, mock_get_contents, mock_get_details
    ):
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {
            "visibility": "private",
        }

        mock_get_details.return_value = repository_details
        mock_get_contents.return_value = {
            "error": "An error occurred while fetching repository contents: Invalid Json"
        }

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)
        assert result["result"] == "error"
        assert (
            result["message"]
            == "An error occurred while fetching repository contents: Invalid Json"
        )
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_visibility"] == "private"
        assert result["details"]["repository_contents"] == {}

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_fail_for_private_repository_without_pirr(
        self, mock_get_contents, mock_get_details
    ):
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {
            "visibility": "private",
        }
        repository_contents = [
            {"name": "README.md", "path": "README.md", "type": "file"},
            {"name": "main.py", "path": "main.py", "type": "file"},
        ]

        mock_get_details.return_value = repository_details
        mock_get_contents.return_value = repository_contents

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)
        assert result["result"] == "fail"
        assert result["message"] == "Repository missing PIRR documentation."
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_visibility"] == "private"
        assert result["details"]["repository_contents"] == repository_contents

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_success_for_private_repository_with_pirr(
        self, mock_get_contents, mock_get_details
    ):
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {
            "visibility": "private",
        }
        repository_contents = [
            {"name": "README.md", "path": "README.md", "type": "file"},
            {"name": "PIRR.md", "path": "PIRR.md", "type": "file"},
            {"name": "main.py", "path": "main.py", "type": "file"},
        ]

        mock_get_details.return_value = repository_details
        mock_get_contents.return_value = repository_contents

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)
        assert result["result"] == "pass"
        assert result["message"] == "Repository contains PIRR documentation."
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_visibility"] == "private"
        assert result["details"]["repository_contents"] == repository_contents

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_fail_for_internal_repository_without_pirr(
        self, mock_get_contents, mock_get_details
    ):
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {
            "visibility": "internal",
        }
        repository_contents = [
            {"name": "README.md", "path": "README.md", "type": "file"},
            {"name": "main.py", "path": "main.py", "type": "file"},
        ]

        mock_get_details.return_value = repository_details
        mock_get_contents.return_value = repository_contents

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)
        assert result["result"] == "fail"
        assert result["message"] == "Repository missing PIRR documentation."
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_visibility"] == "internal"
        assert result["details"]["repository_contents"] == repository_contents

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_error_when_get_repo_contents_returns_unexpected_format(
        self, mock_get_contents, mock_get_details
    ):
        """get_repo_contents returning a non-error, non-list dict hits the unexpected-format guard."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {"visibility": "private"}

        mock_get_details.return_value = repository_details
        mock_get_contents.return_value = {"unexpected": "payload"}

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)
        assert result["result"] == "error"
        assert result["message"] == "Unexpected repository contents format."
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_visibility"] == "private"
        assert result["details"]["repository_contents"] == {}

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_error_when_get_repo_contents_raises_exception(
        self, mock_get_contents, mock_get_details
    ):
        """get_repo_contents raising an exception is caught by the inner except block."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {"visibility": "private"}

        mock_get_details.return_value = repository_details
        mock_get_contents.side_effect = Exception("connection reset")

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)
        assert result["result"] == "error"
        assert (
            result["message"] == "Error fetching repository content: connection reset."
        )
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_visibility"] == "private"
        assert result["details"]["repository_contents"] == {}

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_error_when_get_repo_details_raises_exception(
        self, mock_get_contents, mock_get_details
    ):
        """get_repo_details raising an exception is caught by the outer except block."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        mock_get_details.side_effect = Exception("timeout")

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_not_called()
        assert result["result"] == "error"
        assert result["message"] == "Error evaluating PIRR check: timeout"
        assert result["details"] == {}

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_error_for_unknown_visibility(self, mock_get_contents, mock_get_details):
        """When visibility is not public, private, or internal, should return error."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {"visibility": "unknown"}

        mock_get_details.return_value = repository_details

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_not_called()
        assert result["result"] == "error"
        assert result["message"] == (
            f"Repository visibility is unexpected for {repository_name}."
        )
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_visibility"] == "unknown"
        assert result["details"].get("repository_contents") is None
