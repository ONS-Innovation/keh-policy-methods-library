from policy_methods_library.utils import get_contents
from unittest.mock import MagicMock


"Tests for get_contents function"
# ---------------------------------------------------------------------------
# get_contents
# ---------------------------------------------------------------------------


class Test_Utils_Get_Contents:
    """Tests for get_contents function in utils module."""

    def test_error_when_github_client_is_none(self):
        """Test get_repo_contents returns error when repository name is empty."""

        result = get_contents.get_repo_contents(
            github_client=None, repository_name="my-repo"
        )

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

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
        client = MagicMock()

        result = get_contents.get_repo_contents(
            github_client=client, repository_name=""
        )

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_empty_string(self):
        """An empty repository name should return an error result."""
        client = MagicMock()

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
    client = MagicMock()
    client.owner = "my-org"
    client.make_request.return_value.json.return_value = {"invalid": "response"}

    result = get_contents.get_repo_contents(
        github_client=client, repository_name="my-repo"
    )

    assert result == {
        "result": "error",
        "message": "API response is not a valid JSON array.",
        "details": {"response": {"invalid": "response"}},
    }


def test_successful_response():
    """Test get_repo_contents returns success when API response is a valid JSON array."""
    client = MagicMock()
    client.owner = "my-org"
    client.make_request.return_value.json.return_value = [
        {"name": "file1.txt", "type": "file"},
        {"name": "dir1", "type": "dir"},
    ]

    result = get_contents.get_repo_contents(
        github_client=client, repository_name="my-repo"
    )

    assert result == {
        "result": "pass",
        "message": "Successfully retrieved contents for repository 'my-repo'.",
        "details": [
            {"name": "file1.txt", "type": "file"},
            {"name": "dir1", "type": "dir"},
        ],
    }


def test_exception_handling():
    """Test get_repo_contents returns error when an exception occurs during API request."""
    client = MagicMock()
    client.owner = "my-org"
    client.make_request.side_effect = Exception("API request failed")

    result = get_contents.get_repo_contents(
        github_client=client, repository_name="my-repo"
    )

    assert result == {
        "result": "error",
        "message": "An error occurred while fetching repository contents: API request failed",
        "details": {},
    }
