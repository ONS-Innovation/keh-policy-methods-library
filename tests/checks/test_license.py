"""Tests for the license check module."""

from unittest.mock import call, create_autospec, patch

from requests import Response

from policy_methods_library.checks.license import check_license
from policy_methods_library.github.clients import GitHubRestClient


# ---------------------------------------------------------------------------
# check_license
# ---------------------------------------------------------------------------


class TestCheckLicense:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = check_license(client=None, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_none(self):
        """A missing repository name should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)

        result = check_license(client=client, repository_name=None)

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_passes_when_repository_is_private(self):
        """Private repositories should be treated as exempt from this requirement."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        repo_response = create_autospec(Response, instance=True)
        repo_response.json.return_value = {"private": True}
        client.make_request.return_value = repo_response

        result = check_license(client=client, repository_name="my-repo")

        client.make_request.assert_called_once_with("GET", "/repos/my-org/my-repo")

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' is not public and does not require a license file.",
            "details": {
                "repository_name": "my-repo",
                "required_file": "license",
                "is_public": False,
            },
        }

    def test_passes_when_license_is_present(self):
        """A public repository containing LICENSE should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        repo_response = create_autospec(Response, instance=True)
        repo_response.json.return_value = {"private": False}

        contents_response = create_autospec(Response, instance=True)
        contents_response.json.return_value = [
            {"name": "LICENSE"},
            {"name": "src"},
        ]

        client.make_request.side_effect = [repo_response, contents_response]

        result = check_license(client=client, repository_name="my-repo")

        client.make_request.assert_has_calls(
            [
                call("GET", "/repos/my-org/my-repo"),
                call("GET", "/repos/my-org/my-repo/contents"),
            ]
        )

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' contains a license file.",
            "details": {
                "repository_name": "my-repo",
                "required_file": "license",
                "is_public": True,
            },
        }

    def test_passes_when_license_md_is_present(self):
        """A public repository containing LICENSE.md should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        repo_response = create_autospec(Response, instance=True)
        repo_response.json.return_value = {"private": False}

        contents_response = create_autospec(Response, instance=True)
        contents_response.json.return_value = [
            {"name": "LICENSE.md"},
        ]

        client.make_request.side_effect = [repo_response, contents_response]

        result = check_license(client=client, repository_name="my-repo")

        assert result["result"] == "pass"

    def test_passes_when_license_txt_is_present(self):
        """A public repository containing LICENSE.txt should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        repo_response = create_autospec(Response, instance=True)
        repo_response.json.return_value = {"private": False}

        contents_response = create_autospec(Response, instance=True)
        contents_response.json.return_value = [
            {"name": "license.txt"},
        ]

        client.make_request.side_effect = [repo_response, contents_response]

        result = check_license(client=client, repository_name="my-repo")

        assert result["result"] == "pass"

    def test_fails_when_license_is_absent(self):
        """A public repository without a recognized license filename should fail."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        repo_response = create_autospec(Response, instance=True)
        repo_response.json.return_value = {"private": False}

        contents_response = create_autospec(Response, instance=True)
        contents_response.json.return_value = [
            {"name": "README.md"},
            {"name": "src"},
        ]

        client.make_request.side_effect = [repo_response, contents_response]

        result = check_license(client=client, repository_name="my-repo")

        assert result == {
            "result": "fail",
            "message": "Repository 'my-repo' does not contain a license file.",
            "details": {
                "repository_name": "my-repo",
                "required_file": "license",
                "is_public": True,
            },
        }

    def test_error_when_client_raises_exception(self):
        """An exception during the API call should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_license(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "An error occurred while fetching repository details: connection timeout",
            "details": {},
        }

    def test_error_when_repo_details_utility_returns_string(self):
        """Type narrowing guard should catch if details utility returns wrong shape."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        with patch(
            "policy_methods_library.checks.license.get_repo_details"
        ) as mock_details:
            mock_details.return_value = "unexpected_string"

            result = check_license(client=client, repository_name="my-repo")

            assert result["result"] == "error"
            assert "Unexpected repository details format" in result["message"]

    def test_error_when_contents_utility_returns_string(self):
        """Type narrowing guard should catch if contents utility returns wrong shape."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        with (
            patch(
                "policy_methods_library.checks.license.get_repo_details"
            ) as mock_details,
            patch(
                "policy_methods_library.checks.license.get_repo_contents"
            ) as mock_contents,
        ):
            mock_details.return_value = {"private": False}
            mock_contents.return_value = "unexpected_string"

            result = check_license(client=client, repository_name="my-repo")

            assert result["result"] == "error"
            assert "Unexpected repository contents format" in result["message"]

    def test_error_when_utility_exception_propagates(self):
        """Outer exception handler should catch any unexpected errors."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        with patch(
            "policy_methods_library.checks.license.get_repo_details"
        ) as mock_details:
            mock_details.side_effect = RuntimeError("unexpected error")

            result = check_license(client=client, repository_name="my-repo")

            assert result["result"] == "error"
            assert "Error fetching repository data" in result["message"]
            assert "unexpected error" in result["message"]

    def test_error_when_get_repo_contents_returns_error_dict(self):
        """When get_repo_contents utility returns error dict, should propagate error."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        with (
            patch(
                "policy_methods_library.checks.license.get_repo_details"
            ) as mock_details,
            patch(
                "policy_methods_library.checks.license.get_repo_contents"
            ) as mock_contents,
        ):
            mock_details.return_value = {"private": False}
            mock_contents.return_value = {"error": "Repository not found"}

            result = check_license(client, "my-repo")

            assert result["result"] == "error"
            assert result["message"] == "Repository not found"

    def test_license_check_with_empty_repository_name(self):
        """When repository_name is empty string, should return error."""
        client = GitHubRestClient(
            owner="my-org",
            access_token="test_token",
        )

        result = check_license(client, "")

        assert result["result"] == "error"
        assert "Repository name is required" in result["message"]
