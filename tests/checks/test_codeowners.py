"""Tests for the codeowners check module."""

import base64
from unittest.mock import call, create_autospec

import requests
from requests import Response

from policy_methods_library.checks.codeowners import check_codeowners
from policy_methods_library.github.clients import GitHubRestClient


def _make_file_response(text: str) -> Response:
    """Build a mock API response containing base64-encoded file content."""
    response = create_autospec(Response, instance=True)
    encoded = base64.b64encode(text.encode()).decode()
    response.json.return_value = {"content": encoded}
    return response


# ---------------------------------------------------------------------------
# check_codeowners
# ---------------------------------------------------------------------------


class TestCheckCodeowners:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = check_codeowners(client=None, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_none(self):
        """A missing repository name should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)

        result = check_codeowners(client=client, repository_name=None)

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_passes_when_codeowners_in_root(self):
        """A repository with a non-empty CODEOWNERS in the root should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        client.make_request.return_value = _make_file_response("* @my-org/owners\n")

        result = check_codeowners(client=client, repository_name="my-repo")

        client.make_request.assert_called_once_with(
            "GET", "/repos/my-org/my-repo/contents/CODEOWNERS"
        )

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' contains a CODEOWNERS file at 'CODEOWNERS'.",
            "details": {
                "repository_name": "my-repo",
                "codeowners_path": "CODEOWNERS",
            },
        }

    def test_passes_when_codeowners_in_github_directory(self):
        """A repository with a non-empty CODEOWNERS in .github/ should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        not_found = requests.HTTPError(
            response=create_autospec(Response, instance=True, status_code=404)
        )
        client.make_request.side_effect = [
            not_found,
            _make_file_response("* @my-org/owners\n"),
        ]

        result = check_codeowners(client=client, repository_name="my-repo")

        assert client.make_request.call_count == 2
        client.make_request.assert_any_call(
            "GET", "/repos/my-org/my-repo/contents/.github/CODEOWNERS"
        )

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' contains a CODEOWNERS file at '.github/CODEOWNERS'.",
            "details": {
                "repository_name": "my-repo",
                "codeowners_path": ".github/CODEOWNERS",
            },
        }

    def test_passes_when_codeowners_in_docs_directory(self):
        """A repository with a non-empty CODEOWNERS in docs/ should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        not_found = requests.HTTPError(
            response=create_autospec(Response, instance=True, status_code=404)
        )
        client.make_request.side_effect = [
            not_found,
            not_found,
            _make_file_response("* @my-org/owners\n"),
        ]

        result = check_codeowners(client=client, repository_name="my-repo")

        assert client.make_request.call_count == 3
        client.make_request.assert_any_call(
            "GET", "/repos/my-org/my-repo/contents/docs/CODEOWNERS"
        )

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' contains a CODEOWNERS file at 'docs/CODEOWNERS'.",
            "details": {
                "repository_name": "my-repo",
                "codeowners_path": "docs/CODEOWNERS",
            },
        }

    def test_fails_when_codeowners_absent_in_all_locations(self):
        """A repository with no CODEOWNERS file in any location should fail."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        not_found = requests.HTTPError(
            response=create_autospec(Response, instance=True, status_code=404)
        )
        client.make_request.side_effect = [not_found, not_found, not_found]

        result = check_codeowners(client=client, repository_name="my-repo")

        assert client.make_request.call_count == 3

        assert result == {
            "result": "fail",
            "message": "Repository 'my-repo' does not contain a CODEOWNERS file.",
            "details": {
                "repository_name": "my-repo",
                "checked_paths": [
                    "CODEOWNERS",
                    ".github/CODEOWNERS",
                    "docs/CODEOWNERS",
                ],
            },
        }

    def test_fails_when_codeowners_is_whitespace_only(self):
        """A CODEOWNERS file containing only whitespace should fail."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        client.make_request.return_value = _make_file_response("   \n  \n")

        result = check_codeowners(client=client, repository_name="my-repo")

        assert result == {
            "result": "fail",
            "message": "Repository 'my-repo' contains a CODEOWNERS file at 'CODEOWNERS' but it is empty.",
            "details": {
                "repository_name": "my-repo",
                "codeowners_path": "CODEOWNERS",
            },
        }

    def test_fails_when_codeowners_has_no_content(self):
        """A completely empty CODEOWNERS file should fail."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        client.make_request.return_value = _make_file_response("")

        result = check_codeowners(client=client, repository_name="my-repo")

        assert result["result"] == "fail"
        assert "empty" in result["message"]

    def test_checks_all_paths_in_order(self):
        """The check should probe root, .github/, and docs/ in that order."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        not_found = requests.HTTPError(
            response=create_autospec(Response, instance=True, status_code=404)
        )
        client.make_request.side_effect = [not_found, not_found, not_found]

        check_codeowners(client=client, repository_name="my-repo")

        client.make_request.assert_has_calls(
            [
                call("GET", "/repos/my-org/my-repo/contents/CODEOWNERS"),
                call("GET", "/repos/my-org/my-repo/contents/.github/CODEOWNERS"),
                call("GET", "/repos/my-org/my-repo/contents/docs/CODEOWNERS"),
            ]
        )

    def test_error_when_client_raises_non_404_http_error(self):
        """A non-404 HTTP error during the API call should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        server_error = requests.HTTPError(
            response=create_autospec(Response, instance=True, status_code=500)
        )
        client.make_request.side_effect = server_error

        result = check_codeowners(client=client, repository_name="my-repo")

        assert result["result"] == "error"
        assert "An error occurred while fetching repository contents" in result[
            "message"
        ]

    def test_error_when_client_raises_exception(self):
        """An unexpected exception during the API call should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_codeowners(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "An error occurred while fetching repository contents: connection timeout",
            "details": {},
        }
