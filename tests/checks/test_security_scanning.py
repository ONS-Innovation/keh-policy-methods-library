"""Tests for the security_scanning check module."""

from unittest.mock import MagicMock

from policy_methods_library.checks.security_scanning import check_security_scanning


# ---------------------------------------------------------------------------
# check_security_scanning – data-driven path
# ---------------------------------------------------------------------------


class TestCheckSecurityScanningWithData:
    def test_error_when_visibility_missing_from_data(self):
        """data that does not contain 'visibility' should return an error result."""
        result = check_security_scanning(data={"security_and_analysis": {}})

        assert result == {
            "result": "error",
            "message": "Data must include 'visibility' field to verify the repository is public.",
            "details": {"data": {"security_and_analysis": {}}},
        }

    def test_error_when_security_and_analysis_missing_from_data(self):
        """data that does not contain 'security_and_analysis' should return an error result."""
        result = check_security_scanning(
            data={"name": "my-repo", "visibility": "public"}
        )

        assert result == {
            "result": "error",
            "message": "Data must include 'security_and_analysis' field.",
            "details": {"data": {"name": "my-repo", "visibility": "public"}},
        }

    def test_error_when_security_and_analysis_is_not_a_dict(self):
        """A non-dict 'security_and_analysis' value should return a type error result."""
        result = check_security_scanning(
            data={"visibility": "public", "security_and_analysis": "invalid"}
        )

        assert result == {
            "result": "error",
            "message": "Invalid type for 'security_and_analysis'. Expected dictionary.",
            "details": {"security_and_analysis": "invalid"},
        }

    def test_error_when_security_and_analysis_is_empty(self):
        """An empty 'security_and_analysis' dict should return an error when features are missing."""
        result = check_security_scanning(
            data={"visibility": "public", "security_and_analysis": {}}
        )

        assert result["result"] == "fail"
        assert "Push Protection" in result["message"]
        assert "Secret Scanning" in result["message"]

    def test_fails_when_both_features_disabled(self):
        """A repository with both features disabled should fail."""
        result = check_security_scanning(
            data={
                "visibility": "public",
                "security_and_analysis": {
                    "secret_scanning_push_protection": {"status": "disabled"},
                    "secret_scanning": {"status": "disabled"},
                },
            }
        )

        assert result["result"] == "fail"
        assert "Push Protection" in result["message"]
        assert "Secret Scanning" in result["message"]
        assert result["details"]["push_protection_enabled"] is False
        assert result["details"]["secret_scanning_enabled"] is False

    def test_fails_when_push_protection_disabled(self):
        """A repository with only Push Protection disabled should fail."""
        result = check_security_scanning(
            data={
                "visibility": "public",
                "security_and_analysis": {
                    "secret_scanning_push_protection": {"status": "disabled"},
                    "secret_scanning": {"status": "enabled"},
                },
            }
        )

        assert result["result"] == "fail"
        assert "Push Protection" in result["message"]
        assert "Secret Scanning" not in result["message"]
        assert result["details"]["push_protection_enabled"] is False
        assert result["details"]["secret_scanning_enabled"] is True

    def test_fails_when_secret_scanning_disabled(self):
        """A repository with only Secret Scanning disabled should fail."""
        result = check_security_scanning(
            data={
                "visibility": "public",
                "security_and_analysis": {
                    "secret_scanning_push_protection": {"status": "enabled"},
                    "secret_scanning": {"status": "disabled"},
                },
            }
        )

        assert result["result"] == "fail"
        assert "Secret Scanning" in result["message"]
        assert "Push Protection" not in result["message"]
        assert result["details"]["push_protection_enabled"] is True
        assert result["details"]["secret_scanning_enabled"] is False

    def test_passes_when_both_features_enabled(self):
        """A repository with both features enabled should pass."""
        security_data = {
            "secret_scanning_push_protection": {"status": "enabled"},
            "secret_scanning": {"status": "enabled"},
        }

        result = check_security_scanning(
            data={"visibility": "public", "security_and_analysis": security_data}
        )

        assert result == {
            "result": "pass",
            "message": "Both Push Protection and Secret Scanning are enabled.",
            "details": {
                "push_protection_enabled": True,
                "secret_scanning_enabled": True,
                "security_and_analysis": security_data,
            },
        }

    def test_passes_with_additional_security_analysis_fields(self):
        """A repository with both features enabled and additional fields should pass."""
        security_data = {
            "secret_scanning_push_protection": {"status": "enabled"},
            "secret_scanning": {"status": "enabled"},
            "dependabot_security_updates": {"status": "enabled"},
            "other_field": {"some": "value"},
        }

        result = check_security_scanning(
            data={"visibility": "public", "security_and_analysis": security_data}
        )

        assert result["result"] == "pass"
        assert result["details"]["push_protection_enabled"] is True
        assert result["details"]["secret_scanning_enabled"] is True

    def test_passes_when_repository_is_private(self):
        """Private repositories should pass because this check is not applicable."""
        result = check_security_scanning(
            data={
                "visibility": "private",
                "security_and_analysis": {
                    "secret_scanning_push_protection": {"status": "disabled"},
                    "secret_scanning": {"status": "disabled"},
                },
            }
        )

        assert result == {
            "result": "pass",
            "message": "Repository is private, so Push Protection and Secret Scanning are not applicable.",
            "details": {"visibility": "private"},
        }

    def test_passes_when_repository_is_internal(self):
        """Internal repositories should pass because this check is not applicable."""
        result = check_security_scanning(
            data={
                "visibility": "internal",
                "security_and_analysis": {
                    "secret_scanning_push_protection": {"status": "disabled"},
                    "secret_scanning": {"status": "disabled"},
                },
            }
        )

        assert result == {
            "result": "pass",
            "message": "Repository is internal, so Push Protection and Secret Scanning are not applicable.",
            "details": {"visibility": "internal"},
        }


# ---------------------------------------------------------------------------
# check_security_scanning – client-driven path
# ---------------------------------------------------------------------------


class TestCheckSecurityScanningWithClient:
    def test_error_when_client_is_none(self):
        """No client and no data should return an error result."""
        result = check_security_scanning()

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required if data is not provided.",
            "details": {},
        }

    def test_error_when_repository_name_is_none(self):
        """A client without a repository_name should return an error result."""
        client = MagicMock()

        result = check_security_scanning(client=client)

        assert result == {
            "result": "error",
            "message": "Repository name is required if data is not provided.",
            "details": {},
        }

    def test_error_when_client_raises_exception(self):
        """An exception during the API call should return an error result with the error message."""
        client = MagicMock()
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_security_scanning(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Error fetching repository data: connection timeout",
            "details": {},
        }

    def test_error_when_response_missing_security_and_analysis(self):
        """An API response without 'security_and_analysis' should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"name": "my-repo", "visibility": "public"}
        client.make_request.return_value = response

        result = check_security_scanning(client=client, repository_name="my-repo")

        assert result["result"] == "error"
        assert "security_and_analysis" in result["message"]

    def test_error_when_response_missing_visibility(self):
        """An API response without 'visibility' should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {
            "name": "my-repo",
            "security_and_analysis": {
                "secret_scanning_push_protection": {"status": "enabled"},
                "secret_scanning": {"status": "enabled"},
            },
        }
        client.make_request.return_value = response

        result = check_security_scanning(client=client, repository_name="my-repo")

        assert result["result"] == "error"
        assert "visibility" in result["message"]

    def test_passes_for_enabled_features_via_client(self):
        """A valid API response with both features enabled should pass."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {
            "visibility": "public",
            "security_and_analysis": {
                "secret_scanning_push_protection": {"status": "enabled"},
                "secret_scanning": {"status": "enabled"},
            },
        }
        client.make_request.return_value = response

        result = check_security_scanning(client=client, repository_name="my-repo")

        assert result["result"] == "pass"
        assert result["details"]["push_protection_enabled"] is True
        assert result["details"]["secret_scanning_enabled"] is True

    def test_fails_for_disabled_features_via_client(self):
        """A valid API response with disabled features should fail."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {
            "visibility": "public",
            "security_and_analysis": {
                "secret_scanning_push_protection": {"status": "disabled"},
                "secret_scanning": {"status": "disabled"},
            },
        }
        client.make_request.return_value = response

        result = check_security_scanning(client=client, repository_name="my-repo")

        assert result["result"] == "fail"
        assert "Push Protection" in result["message"]
        assert "Secret Scanning" in result["message"]

    def test_fails_for_partial_features_via_client(self):
        """A valid API response with one feature enabled and one disabled should fail."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {
            "visibility": "public",
            "security_and_analysis": {
                "secret_scanning_push_protection": {"status": "enabled"},
                "secret_scanning": {"status": "disabled"},
            },
        }
        client.make_request.return_value = response

        result = check_security_scanning(client=client, repository_name="my-repo")

        assert result["result"] == "fail"
        assert "Secret Scanning" in result["message"]
        assert "Push Protection" not in result["message"]
        assert result["details"]["push_protection_enabled"] is True
        assert result["details"]["secret_scanning_enabled"] is False

    def test_passes_for_private_repository_via_client(self):
        """Private repositories should pass because this check is not applicable."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {
            "visibility": "private",
            "security_and_analysis": {
                "secret_scanning_push_protection": {"status": "disabled"},
                "secret_scanning": {"status": "disabled"},
            },
        }
        client.make_request.return_value = response

        result = check_security_scanning(client=client, repository_name="my-repo")

        assert result == {
            "result": "pass",
            "message": "Repository is private, so Push Protection and Secret Scanning are not applicable.",
            "details": {"visibility": "private"},
        }

    def test_makes_correct_api_call(self):
        """The check should make the correct API call to retrieve repository data."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {
            "visibility": "public",
            "security_and_analysis": {
                "secret_scanning_push_protection": {"status": "enabled"},
                "secret_scanning": {"status": "enabled"},
            },
        }
        client.make_request.return_value = response

        check_security_scanning(client=client, repository_name="my-repo")

        # Verify the correct endpoint is called
        client.make_request.assert_called_once_with("GET", "/repos/my-org/my-repo")
