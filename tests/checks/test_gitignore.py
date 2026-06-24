"""Tests for the gitignore check module."""

from unittest.mock import create_autospec, patch

from requests import Response

from policy_methods_library.checks.gitignore import check_gitignore
from policy_methods_library.github.clients import GitHubRestClient


# ---------------------------------------------------------------------------
# check_gitignore
# ---------------------------------------------------------------------------


class TestCheckGitignore:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = check_gitignore(client=None, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_none(self):
        """A missing repository name should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)

        result = check_gitignore(client=client, repository_name=None)

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_passes_when_gitignore_is_present(self):
        """A repository containing .gitignore should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = [
            {"name": ".gitignore"},
            {"name": "src"},
            {"name": "docs"},
        ]
        client.make_request.return_value = response

        result = check_gitignore(client=client, repository_name="my-repo")

        client.make_request.assert_called_once_with(
            "GET", "/repos/my-org/my-repo/contents"
        )

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' contains a .gitignore file.",
            "details": {
                "repository_name": "my-repo",
                "required_file": ".gitignore",
            },
        }

    def test_fails_when_gitignore_is_absent(self):
        """A repository without .gitignore should fail."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = [
            {"name": "src"},
            {"name": "docs"},
            {"name": "LICENSE"},
        ]
        client.make_request.return_value = response

        result = check_gitignore(client=client, repository_name="my-repo")

        assert result == {
            "result": "fail",
            "message": "Repository 'my-repo' does not contain a .gitignore file.",
            "details": {
                "repository_name": "my-repo",
                "required_file": ".gitignore",
            },
        }

    def test_passes_when_gitignore_name_has_different_case(self):
        """.gitignore matching should be case-insensitive."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = [
            {"name": ".GitIgnore"},
        ]
        client.make_request.return_value = response

        result = check_gitignore(client=client, repository_name="my-repo")

        assert result["result"] == "pass"

    def test_error_when_client_raises_exception(self):
        """An exception during the API call should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_gitignore(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "An error occurred while fetching repository contents: connection timeout",
            "details": {},
        }

    def test_error_when_contents_utility_returns_string(self):
        """Type narrowing guard should catch if contents utility returns wrong shape."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        with patch(
            "policy_methods_library.checks.gitignore.get_repo_contents"
        ) as mock_contents:
            mock_contents.return_value = "unexpected_string"

            result = check_gitignore(client=client, repository_name="my-repo")

            assert result["result"] == "error"
            assert "Unexpected repository contents format" in result["message"]

    def test_error_when_utility_exception_propagates(self):
        """Outer exception handler should catch any unexpected errors."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        with patch(
            "policy_methods_library.checks.gitignore.get_repo_contents"
        ) as mock_contents:
            mock_contents.side_effect = RuntimeError("unexpected error")

            result = check_gitignore(client=client, repository_name="my-repo")

            assert result["result"] == "error"
            assert "Error fetching repository data" in result["message"]
            assert "unexpected error" in result["message"]
