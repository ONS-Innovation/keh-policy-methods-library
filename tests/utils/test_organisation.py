"""Tests for organisation utility helpers."""

from unittest.mock import create_autospec

from requests import Response

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.organisation import verify_client_organisation


class TestVerifyClientOrganisation:
    def test_returns_none_for_valid_organisation(self):
        """Organisation clients should pass validation."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = {"type": "Organization", "login": "my-org"}
        client.make_request.return_value = response

        result = verify_client_organisation(client)

        assert result is None

    def test_returns_error_when_request_fails(self):
        """Request exceptions should return a standard error payload."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = verify_client_organisation(client)

        assert result == {
            "result": "error",
            "message": "An error occurred while verifying organisation authentication: connection timeout",
            "details": {},
        }

    def test_returns_error_when_response_not_dict(self):
        """Non-dict payloads should return a response-shape error."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = ["unexpected", "response"]
        client.make_request.return_value = response

        result = verify_client_organisation(client)

        assert result == {
            "result": "error",
            "message": "API response does not contain organisation data.",
            "details": {"response": ["unexpected", "response"]},
        }

    def test_returns_error_when_type_not_organization(self):
        """Non-Organisation account types should return an auth-context error."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = {"type": "User", "login": "my-org"}
        client.make_request.return_value = response

        result = verify_client_organisation(client)

        assert result == {
            "result": "error",
            "message": "Client is not authenticated as an organisation.",
            "details": {"organisation": {"type": "User", "login": "my-org"}},
        }
