"""Tests for the license check module."""

from unittest.mock import MagicMock, call

from policy_methods_library.checks.license import check_license


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
        client = MagicMock()

        result = check_license(client=client, repository_name=None)

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_passes_when_repository_is_private(self):
        """Private repositories should be treated as exempt from this requirement."""
        client = MagicMock()
        client.owner = "my-org"

        repo_response = MagicMock()
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
        client = MagicMock()
        client.owner = "my-org"

        repo_response = MagicMock()
        repo_response.json.return_value = {"private": False}

        contents_response = MagicMock()
        contents_response.json.return_value = [
            {"name": "LICENSE"},
            {"name": "src"},
        ]

        client.make_request.side_effect = [repo_response, contents_response]

        result = check_license(client=client, repository_name="my-repo")

        client.make_request.assert_has_calls(
            [
                call("GET", "/repos/my-org/my-repo"),
                call("GET", "/repos/my-org/my-repo/contents/"),
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
        client = MagicMock()
        client.owner = "my-org"

        repo_response = MagicMock()
        repo_response.json.return_value = {"private": False}

        contents_response = MagicMock()
        contents_response.json.return_value = [
            {"name": "LICENSE.md"},
        ]

        client.make_request.side_effect = [repo_response, contents_response]

        result = check_license(client=client, repository_name="my-repo")

        assert result["result"] == "pass"

    def test_passes_when_license_txt_is_present(self):
        """A public repository containing LICENSE.txt should pass."""
        client = MagicMock()
        client.owner = "my-org"

        repo_response = MagicMock()
        repo_response.json.return_value = {"private": False}

        contents_response = MagicMock()
        contents_response.json.return_value = [
            {"name": "license.txt"},
        ]

        client.make_request.side_effect = [repo_response, contents_response]

        result = check_license(client=client, repository_name="my-repo")

        assert result["result"] == "pass"

    def test_fails_when_license_is_absent(self):
        """A public repository without a recognized license filename should fail."""
        client = MagicMock()
        client.owner = "my-org"

        repo_response = MagicMock()
        repo_response.json.return_value = {"private": False}

        contents_response = MagicMock()
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
        client = MagicMock()
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_license(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Error fetching repository data: connection timeout",
            "details": {},
        }
