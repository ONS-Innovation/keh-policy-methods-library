"""Tests for the PIRR check module."""

from unittest.mock import create_autospec, patch

from policy_methods_library.github.clients import GitHubRestClient

from policy_methods_library.checks import pirr


# ---------------------------------------------------------------------------
# pirr
# ---------------------------------------------------------------------------


class TestCheckPIRR:
    """Tests for check_pirr function."""

    def test_repository_name_error_when_empty(self):
        """Test that the check fails when the repository name is empty."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        result = pirr.check_pirr(client, "")
        assert result["result"] == "error"
        assert result["message"] == "Repository name is required."
        assert result["details"] == {}

    def test_client_error_when_not_required_format(self):
        """Test that the check fails when the client is not a GitHubRestClient instance."""

        client = "not_a_githubrestclient"
        result = pirr.check_pirr(client, "TestRepo")
        assert result["result"] == "error"
        assert result["message"] == "GitHubRestClient instance is required."
        assert result["details"] == {}

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_success_for_public_repository(self, mock_get_contents, mock_get_details):
        """Test that the check passes when the repository is public."""

        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {
            "private": False,
            "visibility": "public",
        }

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {
            "result": "pass",
            "message": "Repository details retrieved successfully.",
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
            },
        }

        mock_get_contents.return_value = {}

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)

        mock_get_contents.assert_not_called()

        assert result["result"] == "pass"

        assert result["message"] == (
            f"Successfully retrieved the details for repository {repository_name}"
        )
        assert result["details"]["repository_name"] == repository_name

        assert result["details"]["repository_details"] == repository_details

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_error_for_public_repository_get_details(
        self, mock_get_contents, mock_get_details
    ):
        """Test that API errors retrieving repository details return error."""

        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        mock_get_contents.return_value = {}
        mock_get_details.side_effect = Exception("Invalid Json")

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)

        mock_get_contents.assert_not_called()

        assert result["result"] == "error"

        assert result["message"] == ("Error fetching repository details: Invalid Json")
        assert result["details"] == {}

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_error_for_unexpected_repository_details(
        self, mock_get_contents, mock_get_details
    ):
        """
        Test for error when repository details are not in the expected range
        """
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        expected_message = (
            "Repository visibility or privacy settings are unexpected for "
            f"{repository_name}."
        )

        repository_details = {
            "private": True,
            "visibility": "public",
        }

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {
            "result": "error",
            "message": expected_message,
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
            },
        }

        mock_get_contents.return_value = {}

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)

        mock_get_contents.assert_not_called()

        assert result["result"] == "error"

        assert result["message"] == expected_message
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_details"] == repository_details

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_error_for_private_repository_details(
        self, mock_get_contents, mock_get_details
    ):
        """
        Test that the check errors when the format of contents is not expected.
        """
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        expected_contents_message = "Error fetching repository content: Invalid Json."
        expected_details_message = (
            f"Successfully retrieved the details for repository {repository_name}"
        )

        repository_details = {
            "private": True,
            "visibility": "private",
        }

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {
            "result": "pass",
            "message": expected_details_message,
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
            },
        }

        mock_get_contents.return_value = {
            "result": "error",
            "message": expected_contents_message,
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
                "repository_contents": {},
            },
        }

        mock_get_contents.side_effect = Exception("Invalid Json")

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)

        mock_get_contents.assert_called_once_with(client, repository_name)

        assert result["result"] == "error"

        assert result["message"] == expected_contents_message
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_details"] == repository_details
        assert result["details"]["repository_contents"] == {}

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_fail_for_private_repository_details(
        self, mock_get_contents, mock_get_details
    ):
        """
        Test that the check fails when a repository does not have a pirr.md file in contents.
        """
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        expected_contents_message = "Repository missing PIRR documentation."
        expected_details_message = (
            f"Successfully retrieved the details for repository {repository_name}"
        )

        repository_details = {
            "private": True,
            "visibility": "private",
        }

        repository_contents = [
            {"name": "README.md", "type": "file"},
            {"name": "main.py", "type": "file"},
        ]

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {
            "result": "pass",
            "message": expected_details_message,
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
                "repository_contents": repository_contents,
            },
        }

        mock_get_contents.return_value = {
            "result": "fail",
            "message": expected_contents_message,
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
                "repository_contents": repository_contents,
            },
        }

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)

        mock_get_contents.assert_called_once_with(client, repository_name)

        assert result["result"] == "fail"

        assert result["message"] == expected_contents_message
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_details"] == repository_details
        assert result["details"]["repository_contents"] == repository_contents

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_success_for_private_repository_details(
        self, mock_get_contents, mock_get_details
    ):
        """Test that the check passes when PIRR documentation exists."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        expected_contents_message = "Repository contains PIRR documentation."
        expected_details_message = (
            f"Successfully retrieved the details for repository {repository_name}"
        )

        repository_details = {
            "private": True,
            "visibility": "private",
        }

        repository_contents = [
            {"name": "README.md", "type": "file"},
            {"name": "PIRR.md", "type": "file"},
            {"name": "main.py", "type": "file"},
        ]

        mock_get_details.return_value = {
            "result": "pass",
            "message": expected_details_message,
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
                "repository_contents": repository_contents,
            },
        }

        mock_get_contents.return_value = {
            "result": "pass",
            "message": expected_contents_message,
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
                "repository_contents": repository_contents,
            },
        }

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)

        assert result["result"] == "pass"
        assert result["message"] == expected_contents_message
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_details"] == repository_details
        assert result["details"]["repository_contents"] == repository_contents

    @patch("policy_methods_library.checks.pirr.get_repo_details")
    @patch("policy_methods_library.checks.pirr.get_repo_contents")
    def test_fail_for_internal_repository_without_pirr(
        self, mock_get_contents, mock_get_details
    ):
        """Test that internal repositories also require PIRR documentation."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"
        repository_details = {
            "private": True,
            "visibility": "internal",
        }
        repository_contents = [
            {"name": "README.md", "type": "file"},
            {"name": "main.py", "type": "file"},
        ]

        mock_get_details.return_value = {
            "result": "pass",
            "message": "Repository details retrieved successfully.",
            "details": {
                "repository_name": repository_name,
                "repository_details": repository_details,
            },
        }

        mock_get_contents.return_value = {
            "result": "pass",
            "message": "Repository contents retrieved successfully.",
            "details": {
                "repository_name": repository_name,
                "repository_contents": repository_contents,
            },
        }

        result = pirr.check_pirr(client, repository_name)

        mock_get_details.assert_called_once_with(client, repository_name)
        mock_get_contents.assert_called_once_with(client, repository_name)

        assert result["result"] == "fail"
        assert result["message"] == "Repository missing PIRR documentation."
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_details"] == repository_details
        assert result["details"]["repository_contents"] == repository_contents
