"""Tests for get_contents function"""

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils import get_contents
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# get_contents
# ---------------------------------------------------------------------------


class Test_Utils_Get_Contents:
    """Tests for get_contents function in utils module.
    The get_contents function retrieves the contents of a GitHub repository using the GitHub REST API.
    It takes a GitHubRestClient instance and a repository name as input, makes an API request to fetch the repository contents, and returns a structured result indicating success or failure along with any relevant details.
    """

    def test_error_when_github_client_is_not_instance_of_githubrestclient(self):
        """Test get_repo_contents returns error when github_client is not an instance of GitHubRestClient."""

        result = get_contents.get_repo_contents(
            github_client={}, repository_name="my-repo"
        )

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_empty(self):
        """An empty repository name should return an error result."""
        client = GitHubRestClient.__new__(
            GitHubRestClient
        )  # Create an instance without calling __init__
        client.owner = "my-org"

        result = get_contents.get_repo_contents(
            github_client=client, repository_name=""
        )

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }


def test_error_when_response_is_not_valid_json_array():
    """Test get_repo_contents returns error when API response is not a valid JSON array."""

    client = GitHubRestClient.__new__(GitHubRestClient)
    client.owner = "test-owner"

    mock_response = MagicMock()
    # mock_response.json.return_value = {"invalid": "response"}
    client.make_request = MagicMock(return_value=mock_response)
    client.make_request.side_effect = Exception(
        "API response is not a valid JSON array."
    )

    result = get_contents.get_repo_contents(
        github_client=client, repository_name="test-repo"
    )

    assert result["result"] == "error"
    assert (
        result["message"]
        == "An error occurred while fetching repository contents: API response is not a valid JSON array."
    )
    assert result["details"] == {}


def test_get_contents_successful_response():
    """Test get_repo_contents returns success when API response is a valid JSON array."""

    client = GitHubRestClient.__new__(GitHubRestClient)
    client.owner = "test-owner"

    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"name": "file1.txt", "type": "file"},
        {"name": "dir1", "type": "dir"},
    ]
    client.make_request = MagicMock(return_value=mock_response)

    get_contents.get_repo_contents.make_request = MagicMock(return_value=mock_response)

    result = get_contents.get_repo_contents(
        github_client=client, repository_name="my-repo"
    )

    assert result["result"] == "pass"
    assert result["message"] == "Repository contents retrieved successfully."
    assert result["details"] == {
        "repository_name": "my-repo",
        "contents": [
            {"name": "file1.txt", "type": "file"},
            {"name": "dir1", "type": "dir"},
        ],
    }
