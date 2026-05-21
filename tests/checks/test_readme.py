"""Tests for the readme check module."""

from unittest.mock import MagicMock

from policy_methods_library.checks.readme import check_readme


# ---------------------------------------------------------------------------
# check_readme
# ---------------------------------------------------------------------------


class TestCheckReadme:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = check_readme(client=None, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_none(self):
        """A missing repository name should return an error result."""
        client = MagicMock()

        result = check_readme(client=client, repository_name=None)

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_passes_when_readme_md_is_present(self):
        """A repository containing readme.md should pass."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = [
            {"name": "README.md"},
            {"name": "src"},
            {"name": "docs"},
        ]
        client.make_request.return_value = response

        result = check_readme(client=client, repository_name="my-repo")

        client.make_request.assert_called_once_with(
            "GET", "/repos/my-org/my-repo/contents/"
        )

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' contains a readme.md file.",
            "details": {
                "repository_name": "my-repo",
                "required_file": "readme.md",
            },
        }

    def test_fails_when_readme_md_is_absent(self):
        """A repository without readme.md should fail."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = [
            {"name": "src"},
            {"name": "docs"},
            {"name": "LICENSE"},
        ]
        client.make_request.return_value = response

        result = check_readme(client=client, repository_name="my-repo")

        assert result == {
            "result": "fail",
            "message": "Repository 'my-repo' does not contain a readme.md file.",
            "details": {
                "repository_name": "my-repo",
                "required_file": "readme.md",
            },
        }

    def test_passes_when_readme_name_has_different_case(self):
        """README matching should be case-insensitive."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = [
            {"name": "ReadMe.MD"},
        ]
        client.make_request.return_value = response

        result = check_readme(client=client, repository_name="my-repo")

        assert result["result"] == "pass"

    def test_error_when_client_raises_exception(self):
        """An exception during the API call should return an error result."""
        client = MagicMock()
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_readme(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Error fetching repository data: connection timeout",
            "details": {},
        }
