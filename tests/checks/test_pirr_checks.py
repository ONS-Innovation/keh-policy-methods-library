#
"""
Tests for the PIRR check module
"""

from unittest.mock import create_autospec, patch

from policy_methods_library.github.clients import GitHubRestClient

from policy_methods_library.checks import pirr_checks

from policy_methods_library.utils.get_contents import get_repo_contents

from policy_methods_library.utils.get_details import get_repo_details


# ---------------------------------------------------------------------------
# pirr_checks
# ---------------------------------------------------------------------------


class TestCheckPIRR:
    """Tests for check_pirr function.
    These tests cover various scenarios for checking repository visibility and 
    the presence of PIRR documentation, including error handling for invalid 
    inputs and API call failures."""

    def test_repository_name_error_when_empty(self):
        """Test that the check fails when the repository name is empty."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        result = pirr_checks.check_pirr(client, "")
        assert result["result"] == "error"
        assert result["message"] == "Repository name is required."
        assert result["details"] == {}

    def test_client_error_when_not_required_format(self):
        """Test that the check fails when the client is not a GitHubRestClient 
        instance."""

        client = "not_a_githubrestclient"
        result = pirr_checks.check_pirr(client, "TestRepo")
        assert result["result"] == "error"
        assert result["message"] == "GitHubRestClient instance is required."
        assert result["details"] == {}

    @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    @patch("policy_methods_library.checks.pirr_checks.get_repo_content")

    def test_success_for_public_repository(self, mock_get_content, mock_get_details):

        """Test that the check passes when the repository is public."""

        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        repository_name = "TestRepo"

        # Mock the return value for get_repo_details
        mock_get_details.return_value = {
            "result": "pass",
            "message": (
                f"Successfully retrieved the details for repository "
                f"{repository_name}."
            ),
            "details": {
                "repository_name": repository_name,
                "details": {"private": False, "visibility": "public"},
            
            },
        }
        mock_get_content.return_value = {}

        result = pirr_checks.check_pirr(client, repository_name)
        print(result)

        mock_get_details.assert_called_once_with(client, repository_name)

        mock_get_content.assert_not_called()

        assert result["result"] == "pass"

        assert result["message"] ==  f"Successfully retrieved the details for repository {repository_name}"
        assert result["details"]["repository_name"] == repository_name
        assert result["details"]["repository_details"] == {
            "private": False,
            "visibility": "public",
        }

    # @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    # @patch("policy_methods_library.checks.pirr_checks.get_repo_content")

    # def test_error_for_public_repository_get_details(
    #     self, mock_get_contents, mock_get_details
    # ):
    #     """Test that the check fails when get_repo_details raises an error."""
    #     client = create_autospec(GitHubRestClient, instance=True)
    #     client.owner = "my-org"
    #     repository_name = "TestRepo"

    #     mock_get_details.side_effect = Exception("Invalid Json")

    #     result = pirr_checks.check_pirr(client, repository_name)

    #     mock_get_details.assert_called_once_with(client, repository_name)
    #     mock_get_contents.assert_called_once_with(client, repository_name)

    #     assert result["result"] == "error"
    #     # assert result["details"] == {}
    #     # assert (
    #     #     result["message"] == "An error occurred while fetching 
    #     # repository details: "
    #     # )

    # @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    # @patch("policy_methods_library.checks.pirr_checks.get_repo_content")

    # def test_success_for_private_repository(self, 
    #                                         mock_get_contents, mock_get_details):
    #     """
    #     Test that the check passes when the repository is private and contains
    #     PIRR documentation.
    #     """
    #     client = create_autospec(GitHubRestClient, instance=True)
    #     client.owner = "my-org"
    #     repository_name = "TestRepo"

    #     # Mock the return value for get_repo_details
    #     mock_get_details.return_value = {
    #         "result": "pass",
    #         "message": "successfully recieved repository details",
    #         "details": {
    #             "repository name": repository_name,
    #             "repository details": {"private": True, "visibility": "private"},
    #         },
    #     }

    #     # Mock the return value for get_contents to simulate .github directory exists
    #     mock_get_contents.return_value ={
    #         "result": "pass",
    #         "message": "successfully recieved repository contents",
    #         "details": {
    #             "repository name": repository_name,
    #             "repository details": {"private": True, "visibility": "private"},
    #             "repository contents": [
    #         {"name": "README.md", "type": "file"},
    #         {"name": "PIRR.md", "type": "file"},
    #     ]
    #         },
    #     }
    #     result = pirr_checks.check_pirr(client, repository_name)
    #     print(result["details"])

    #     mock_get_details.assert_called_once_with(client, repository_name)
    #     # mock_get_contents.assert_called_once_with(client, repository_name)

    #     assert result["result"] == "pass"
    #     assert result["message"] == "Repository contains PIRR documentation."
    #     assert result['details']['repository_name'] == repository_name
    #     assert result["details"]['contents'] == mock_get_contents.return_value

    # @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    # @patch("policy_methods_library.checks.pirr_checks.get_repo_content")

    # def test_success_for_private_internal_repository(
    #     self, mock_get_contents, mock_get_details
    # ):
    #     """Test that the checking test passes when the repository is 
    #     private internal and pirr docunented."""

    #     client = create_autospec(GitHubRestClient, instance=True)
    #     client.owner = "my-org"
    #     repository_name = "TestRepo"

    #     # Mock the return value for get_repo_details
    #     mock_get_details.return_value = {
    #         "result": "pass",
    #         "message": "successfully recieved repository details",
    #         "details": {
    #             "repository name": repository_name,
    #             "repository details": {"private": True, "visibility": "internal"},
    #         },
    #     }

    #     # Mock the return value for get_contents to simulate .github directory exists
    #     mock_get_contents.return_value ={
    #         "result": "pass",
    #         "message": "successfully recieved repository contents",
    #         "details": {
    #             "repository name": repository_name,
    #             "repository contents": [
    #         {"name": "README.md", "type": "file"},
    #         {"name": "PIRR.md", "type": "file"},
    #     ]
    #         },
    #     }
    #     result = pirr_checks.check_pirr(client, repository_name)
    #     print(result)

    #     mock_get_details.assert_called_once_with(client, repository_name)
    #     mock_get_contents.assert_called_once_with(client, repository_name)

    #     assert result["result"] == "pass"
    #     assert result["message"] == "Repository contains PIRR documentation."
    #     assert result['details']['repository_name'] == repository_name
    #     assert result["details"]['contents'] == mock_get_contents.return_value

    # @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    # @patch("policy_methods_library.checks.pirr_checks.get_repo_content")

    # def test_error_get_contents_for_private_repository(
    #     self, mock_get_contents, mock_get_details
    # ):
    #     """Test that the check errors when get_repo_contents raises an error."""
    #     client = create_autospec(GitHubRestClient, instance=True)
    #     client.owner = "my-org"
    #     repository_name = "TestRepo"

    #     # Mock the return value for get_repo_details
    #     mock_get_details.return_value = {"private": True, "visibility": "internal"}

    #     # Mock the return value for get_repo_contents
    #     mock_get_contents.side_effect = Exception("Invalid Json")

    #     result = pirr_checks.check_pirr(client, repository_name)

    #     mock_get_details.assert_called_once_with(client, repository_name)

    #     mock_get_contents.assert_called_once_with(client, repository_name)

    #     assert result["result"] == "error"
    #     # assert result["details"] == {}
    #     # assert (
    #     #     result["message"]
    #     #     == "An error occurred while fetching repository contents: "
    #     # )

    # @patch("policy_methods_library.checks.pirr_checks.get_repo_details")
    # @patch("policy_methods_library.checks.pirr_checks.get_repo_content")

    # def test_fail_for_private_repositorty_without_pirr_file(
    #     self, mock_get_contents, mock_get_details):

    #     """Test that the check fails when the repository is private and does 
    #     not contain PIRR documentation."""

    #     client = create_autospec(GitHubRestClient, instance=True)
    #     client.owner = "my-org"
    #     repository_name = "TestRepo"

    #     # Mock the return value for get_repo_details
    #     mock_get_details.return_value = {"private": True, "visibility": "private"}

    #     # Mock the return value for get_contents to simulate .github directory exists
    #     mock_get_contents.return_value = [
    #         {"name": "README.md", "type": "file"},
    #         {"name": "CODE_OF_CONDUCT.md", "type": "file"}]

    #     result = pirr_checks.check_pirr(client, repository_name)

    #     mock_get_details.assert_called_once_with(client, repository_name)
    #     mock_get_contents.assert_called_once_with(client, repository_name)

    #     assert result["result"] == "fail"

    #     # assert result["message"] == 
    #     # "Repository does not contain PIRR documentation."
    #     # assert result["details"]["repository_name"] == "TestRepo"
    #     # assert result["details"]["repository_details"] == {
    #     #     "private": True,
    #     #     "visibility": "private",
    #     # }
    #     # fileNames = [
    #     #     content.get("name").lower()
    #     #     for content in result["details"]["repository_contents"]
    #     # ]
    #     # assert "pirr.md" not in fileNames
    #     # assert result["result"] == "fail"
