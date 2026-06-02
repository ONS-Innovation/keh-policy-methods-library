"""Tests for the dependabot check module."""

from unittest.mock import MagicMock
from policy_methods_library.checks.dependabot import check_dependabot


# ---------------------------------------------------------------------------
# check_dependabot
# ---------------------------------------------------------------------------


class TestCheckDependabot:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = check_dependabot(client=None, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_none(self):
        """A client without a repository_name should return an error result."""
        client = MagicMock()

        result = check_dependabot(client=client, repository_name=None)

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_error_when_client_raises_exception(self):
        """An exception during the API call should return an error result with the error message."""
        client = MagicMock()
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_dependabot(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Error fetching automated security fixes data: connection timeout",
            "details": {},
        }

    def test_error_when_response_missing_enabled(self):
        """An API response without 'enabled' should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"enable_auto_merge": False}
        client.make_request.return_value = response

        result = check_dependabot(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "API response does not contain 'enabled' field.",
            "details": {"response": response.json.return_value},
        }

    def test_error_when_response_enabled_is_not_a_boolean(self):
        """A non-boolean 'enabled' in the API response should return a type error result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"enabled": "true"}
        client.make_request.return_value = response

        result = check_dependabot(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Invalid type for 'enabled'. Expected boolean.",
            "details": {"enabled": "true"},
        }

    def test_passes_when_dependabot_enabled(self):
        """A valid API response with enabled=true should pass."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"enabled": True, "enable_auto_merge": False}
        client.make_request.return_value = response

        result = check_dependabot(client=client, repository_name="my-repo")

        assert result == {
            "result": "pass",
            "message": "Dependabot automated security fixes are enabled for my-repo repository.",
            "details": {"enabled": True},
        }

    def test_fails_when_dependabot_disabled(self):
        """A valid API response with enabled=false should fail."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"enabled": False}
        client.make_request.return_value = response

        result = check_dependabot(client=client, repository_name="my-repo")

        assert result == {
            "result": "fail",
            "message": "Dependabot automated security fixes are not enabled for my-repo repository.",
            "details": {"enabled": False},
        }

    def test_calls_correct_api_endpoint(self):
        """The check should call the correct API endpoint."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"enabled": True}
        client.make_request.return_value = response

        check_dependabot(client=client, repository_name="my-repo")

        client.make_request.assert_called_once_with(
            "GET", "/repos/my-org/my-repo/automated-security-fixes"
        )

    def test_passes_with_additional_response_fields(self):
        """Additional fields in the API response should not affect the check result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {
            "enabled": True,
            "enable_auto_merge": False,
            "other_field": "value",
        }
        client.make_request.return_value = response

        result = check_dependabot(client=client, repository_name="my-repo")

        assert result["result"] == "pass"
        assert result["details"]["enabled"] is True
