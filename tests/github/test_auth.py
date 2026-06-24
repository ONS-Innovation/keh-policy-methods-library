"""Tests for the auth module."""

from unittest.mock import create_autospec, patch

import pytest
from requests import Response

from policy_methods_library.github.auth import (
    _generate_jwt,
    _get_installation_id,
    get_access_token,
)


# ---------------------------------------------------------------------------
# _generate_jwt
# ---------------------------------------------------------------------------


class TestGenerateJwt:
    def test_raises_if_app_id_missing(self):
        """A missing app_id should raise a ValueError with a descriptive message."""
        with pytest.raises(ValueError, match="GitHub App ID is required"):
            _generate_jwt("", "some-key")

    def test_raises_if_private_key_missing(self):
        """A missing private_key should raise a ValueError with a descriptive message."""
        with pytest.raises(ValueError, match="GitHub App private key is required"):
            _generate_jwt("123", "")

    def test_raises_on_invalid_private_key_format(self):
        """A private key that is not valid PEM should raise a ValueError."""
        with pytest.raises(ValueError, match="Invalid private key format"):
            _generate_jwt("123", "not-a-valid-pem-key")

    def test_returns_string_for_valid_credentials(self, rsa_private_key):
        """Valid app_id and PEM private key should return a non-empty JWT string."""
        token = _generate_jwt("123", rsa_private_key)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_jwt_contains_expected_claims(self, rsa_private_key):
        """The generated JWT should contain the correct issuer, issued-at, and expiry claims."""
        import jwt as jwt_lib

        token = _generate_jwt("my-app-id", rsa_private_key)
        # Decode without verification to inspect claims
        instance = jwt_lib.JWT()
        message = instance.decode(token, do_verify=False)
        assert message["iss"] == "my-app-id"
        assert "iat" in message
        assert "exp" in message


# ---------------------------------------------------------------------------
# _get_installation_id
# ---------------------------------------------------------------------------


class TestGetInstallationId:
    def test_raises_if_organisation_missing(self):
        """A missing organisation should raise a ValueError with a descriptive message."""
        with pytest.raises(ValueError, match="GitHub organisation name is required"):
            _get_installation_id("", "some-jwt")

    def test_raises_if_jwt_missing(self):
        """A missing JWT should raise a ValueError with a descriptive message."""
        with pytest.raises(ValueError, match="JWT is required"):
            _get_installation_id("my-org", "")

    def test_raises_when_no_installations_found(self):
        """An empty installations list in the API response should raise a ValueError."""
        mock_response = create_autospec(Response, instance=True)
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None

        with patch(
            "policy_methods_library.github.auth.requests.get",
            return_value=mock_response,
            autospec=True,
        ):
            with pytest.raises(
                ValueError, match="No installations found for organisation 'my-org'"
            ):
                _get_installation_id("my-org", "some-jwt")

    def test_returns_installation_id(self):
        """When an installation is returned, its ID should be returned."""
        mock_response = create_autospec(Response, instance=True)
        mock_response.json.return_value = {"id": 42}
        mock_response.raise_for_status.return_value = None

        with patch(
            "policy_methods_library.github.auth.requests.get",
            return_value=mock_response,
            autospec=True,
        ):
            result = _get_installation_id("my-org", "some-jwt")

        assert result == 42

    def test_sends_correct_headers(self):
        """The request to retrieve installations should include a Bearer token Authorization header."""
        mock_response = create_autospec(Response, instance=True)
        mock_response.json.return_value = {"id": 1}
        mock_response.raise_for_status.return_value = None

        with patch(
            "policy_methods_library.github.auth.requests.get",
            return_value=mock_response,
            autospec=True,
        ) as mock_get:
            _get_installation_id("my-org", "test-jwt")

        _, kwargs = mock_get.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-jwt"

    def test_raises_on_http_error(self):
        """An HTTP error from the GitHub API should propagate as a requests.HTTPError."""
        import requests

        mock_response = create_autospec(Response, instance=True)
        mock_response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")

        with patch(
            "policy_methods_library.github.auth.requests.get",
            return_value=mock_response,
            autospec=True,
        ):
            with pytest.raises(requests.HTTPError):
                _get_installation_id("my-org", "some-jwt")


# ---------------------------------------------------------------------------
# get_access_token
# ---------------------------------------------------------------------------


class TestGetAccessToken:
    def test_raises_if_app_id_missing(self):
        """A missing app_id should raise a ValueError before any API call is made."""
        with pytest.raises(ValueError, match="GitHub App ID is required"):
            get_access_token("", "key", "org")

    def test_raises_if_private_key_missing(self):
        """A missing private_key should raise a ValueError before any API call is made."""
        with pytest.raises(ValueError, match="GitHub App private key is required"):
            get_access_token("123", "", "org")

    def test_raises_if_organisation_missing(self):
        """A missing organisation should raise a ValueError before any API call is made."""
        with pytest.raises(ValueError, match="GitHub organisation name is required"):
            get_access_token("123", "key", "")

    def test_returns_access_token(self, rsa_private_key):
        """Valid credentials should return the token string from the GitHub API response."""
        """Valid credentials should return the token string from the GitHub API response."""
        installations_response = create_autospec(Response, instance=True)
        installations_response.json.return_value = {"id": 7}
        installations_response.raise_for_status.return_value = None

        token_response = create_autospec(Response, instance=True)
        token_response.json.return_value = {"token": "ghs_test_token"}
        token_response.raise_for_status.return_value = None

        with (
            patch(
                "policy_methods_library.github.auth.requests.get",
                return_value=installations_response,
                autospec=True,
            ),
            patch(
                "policy_methods_library.github.auth.requests.post",
                return_value=token_response,
                autospec=True,
            ),
        ):
            result = get_access_token("my-app-id", rsa_private_key, "my-org")

        assert result == "ghs_test_token"

    def test_calls_correct_token_endpoint(self, rsa_private_key):
        """The access token POST request should target the installation-specific endpoint."""
        installations_response = create_autospec(Response, instance=True)
        installations_response.json.return_value = {"id": 55}
        installations_response.raise_for_status.return_value = None

        token_response = create_autospec(Response, instance=True)
        token_response.json.return_value = {"token": "ghs_abc"}
        token_response.raise_for_status.return_value = None

        with (
            patch(
                "policy_methods_library.github.auth.requests.get",
                return_value=installations_response,
                autospec=True,
            ),
            patch(
                "policy_methods_library.github.auth.requests.post",
                return_value=token_response,
                autospec=True,
            ) as mock_post,
        ):
            get_access_token("my-app-id", rsa_private_key, "my-org")

        args, _ = mock_post.call_args
        assert args[0] == "https://api.github.com/app/installations/55/access_tokens"

    def test_raises_on_http_error_during_token_generation(self, rsa_private_key):
        """An HTTP error from the access token endpoint should propagate as a requests.HTTPError."""
        import requests

        installations_response = create_autospec(Response, instance=True)
        installations_response.json.return_value = {"id": 7}
        installations_response.raise_for_status.return_value = None

        token_response = create_autospec(Response, instance=True)
        token_response.raise_for_status.side_effect = requests.HTTPError(
            "401 Unauthorised"
        )

        with (
            patch(
                "policy_methods_library.github.auth.requests.get",
                return_value=installations_response,
                autospec=True,
            ),
            patch(
                "policy_methods_library.github.auth.requests.post",
                return_value=token_response,
                autospec=True,
            ),
        ):
            with pytest.raises(requests.HTTPError):
                get_access_token("my-app-id", rsa_private_key, "my-org")
