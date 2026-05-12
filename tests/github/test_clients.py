"""Tests for the clients module."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from policy_methods_library.github.clients import GitHubRestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """Return a GitHubRestClient initialised with a pre-generated access token."""
    return GitHubRestClient(owner="my-org", access_token="ghs_test_token")


# ---------------------------------------------------------------------------
# GitHubRestClient.__init__
# ---------------------------------------------------------------------------


class TestGitHubRestClientInit:
    def test_initialises_with_access_token(self):
        """Providing a pre-generated access_token should store it directly without any API calls."""
        client = GitHubRestClient(owner="my-org", access_token="ghs_direct")
        assert client.access_token == "ghs_direct"
        assert client.owner == "my-org"

    def test_initialises_with_app_credentials(self, rsa_private_key):
        """Providing app_id, private_key, and organisation should fetch and store an access token."""
        installations_response = MagicMock()
        installations_response.json.return_value = {"id": 1}
        installations_response.raise_for_status.return_value = None

        token_response = MagicMock()
        token_response.json.return_value = {"token": "ghs_from_app"}
        token_response.raise_for_status.return_value = None

        with (
            patch(
                "policy_methods_library.github.auth.requests.get",
                return_value=installations_response,
            ),
            patch(
                "policy_methods_library.github.auth.requests.post",
                return_value=token_response,
            ),
        ):
            client = GitHubRestClient(
                owner="my-org",
                app_id="123",
                private_key=rsa_private_key,
            )

        assert client.access_token == "ghs_from_app"
        assert client.owner == "my-org"

    def test_raises_when_no_credentials_provided(self):
        """Constructing a client with owner but no credentials should raise a ValueError."""
        with pytest.raises(ValueError, match="You must provide either an access_token"):
            GitHubRestClient(owner="my-org")

    def test_raises_when_only_app_id_provided(self):
        """Providing only app_id without private_key should raise a ValueError."""
        with pytest.raises(ValueError, match="You must provide either an access_token"):
            GitHubRestClient(owner="my-org", app_id="123")

    def test_access_token_takes_precedence_over_app_credentials(self):
        """If access_token is provided, app credentials should be ignored."""
        client = GitHubRestClient(
            owner="my-org",
            access_token="ghs_direct",
            app_id="123",
            private_key="key",
        )
        assert client.access_token == "ghs_direct"
        assert client.owner == "my-org"

    def test_raises_when_owner_not_provided(self):
        """Constructing a client without an owner should raise a ValueError. Applies to both access token and app credential authentication."""
        with pytest.raises(
            ValueError, match="Owner is required to authenticate with GitHub."
        ):
            GitHubRestClient(owner="", access_token="ghs_test_token")

        with pytest.raises(
            ValueError, match="Owner is required to authenticate with GitHub."
        ):
            GitHubRestClient(owner="", app_id="123", private_key="key")


# ---------------------------------------------------------------------------
# GitHubRestClient.make_request
# ---------------------------------------------------------------------------


class TestMakeRequest:
    def test_uses_correct_base_url(self, client):
        """The request URL should be the GitHub API base URL concatenated with the given endpoint."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        with patch(
            "policy_methods_library.github.clients.requests.request",
            return_value=mock_response,
        ) as mock_req:
            client.make_request("GET", "/repos/my-org/my-repo")

        args, _ = mock_req.call_args
        assert args[1] == "https://api.github.com/repos/my-org/my-repo"

    def test_sends_bearer_token_header(self, client):
        """Every request should include an Authorization header with the client's Bearer token."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        with patch(
            "policy_methods_library.github.clients.requests.request",
            return_value=mock_response,
        ) as mock_req:
            client.make_request("GET", "/user")

        _, kwargs = mock_req.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer ghs_test_token"

    def test_sends_accept_header(self, client):
        """Every request should include the standard GitHub v3 JSON Accept header."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        with patch(
            "policy_methods_library.github.clients.requests.request",
            return_value=mock_response,
        ) as mock_req:
            client.make_request("GET", "/user")

        _, kwargs = mock_req.call_args
        assert kwargs["headers"]["Accept"] == "application/vnd.github.v3+json"

    def test_passes_http_method(self, client):
        """The HTTP method supplied by the caller should be forwarded to the underlying request."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        with patch(
            "policy_methods_library.github.clients.requests.request",
            return_value=mock_response,
        ) as mock_req:
            client.make_request("POST", "/repos/my-org/my-repo/issues")

        args, _ = mock_req.call_args
        assert args[0] == "POST"

    def test_passes_extra_kwargs(self, client):
        """Additional keyword arguments (e.g. json=) should be forwarded to the underlying request."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        payload = {"title": "Bug report"}

        with patch(
            "policy_methods_library.github.clients.requests.request",
            return_value=mock_response,
        ) as mock_req:
            client.make_request("POST", "/repos/my-org/my-repo/issues", json=payload)

        _, kwargs = mock_req.call_args
        assert kwargs["json"] == payload

    def test_merges_custom_headers(self, client):
        """Caller-provided headers should be merged with default auth and accept headers."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        with patch(
            "policy_methods_library.github.clients.requests.request",
            return_value=mock_response,
        ) as mock_req:
            client.make_request(
                "GET",
                "/user",
                headers={"X-GitHub-Api-Version": "2022-11-28"},
            )

        _, kwargs = mock_req.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer ghs_test_token"
        assert kwargs["headers"]["Accept"] == "application/vnd.github.v3+json"
        assert kwargs["headers"]["X-GitHub-Api-Version"] == "2022-11-28"

    def test_returns_response(self, client):
        """make_request should return the response object from the underlying HTTP call."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        with patch(
            "policy_methods_library.github.clients.requests.request",
            return_value=mock_response,
        ):
            result = client.make_request("GET", "/user")

        assert result is mock_response

    def test_raises_on_http_error(self, client):
        """An HTTP error response should propagate as a requests.HTTPError."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        with patch(
            "policy_methods_library.github.clients.requests.request",
            return_value=mock_response,
        ):
            with pytest.raises(requests.HTTPError):
                client.make_request("GET", "/nonexistent")
