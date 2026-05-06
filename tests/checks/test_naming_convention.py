"""Tests for the naming_convention check module."""

from unittest.mock import MagicMock

import pytest

from policy_methods_library.checks.naming_convention import check_naming_convention


# ---------------------------------------------------------------------------
# check_naming_convention
# ---------------------------------------------------------------------------


class TestCheckNamingConvention:
    def test_raises_when_data_and_client_missing(self):
        """If data is not provided, a client must be supplied."""
        with pytest.raises(
            ValueError,
            match="A GitHubRestClient instance must be provided if data is not passed directly.",
        ):
            check_naming_convention()

    def test_raises_when_repository_name_missing(self):
        """If data is not provided, repository_name must be supplied."""
        client = MagicMock()

        with pytest.raises(
            ValueError,
            match="A repository name must be provided if data is not passed directly.",
        ):
            check_naming_convention(client=client)

    def test_returns_error_when_client_request_raises(self):
        """Any exception while fetching repo data should return an error result."""
        client = MagicMock()
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("network issue")

        result = check_naming_convention(client=client, repository_name="my-repo")

        assert result["result"] == "error"
        assert (
            result["message"]
            == "An error occurred while fetching repository data: network issue"
        )
        assert result["data"] is None

    def test_returns_error_for_non_200_response(self):
        """A non-200 response should return an error result with the status code."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.status_code = 404
        client.make_request.return_value = response

        result = check_naming_convention(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Failed to fetch repository data. Status code: 404",
            "data": None,
        }

    def test_fetches_repo_data_using_expected_endpoint(self):
        """The check should call make_request with the expected method and endpoint."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"name": "my-repo"}
        client.make_request.return_value = response

        check_naming_convention(client=client, repository_name="my-repo")

        client.make_request.assert_called_once_with("GET", "/repos/my-org/my-repo")

    def test_fails_when_repo_name_has_uppercase(self):
        """Repository names containing uppercase letters should fail."""
        result = check_naming_convention(data={"name": "My-repo"})

        assert result == {
            "result": "fail",
            "message": "Repository name should be in lowercase.",
            "data": {"repository_name": "My-repo"},
        }

    def test_fails_when_repo_name_has_spaces(self):
        """Repository names containing spaces should fail."""
        result = check_naming_convention(data={"name": "my repo"})

        assert result == {
            "result": "fail",
            "message": "Repository name should not contain spaces.",
            "data": {"repository_name": "my repo"},
        }

    def test_fails_when_repo_name_has_special_characters(self):
        """Repository names containing special characters should fail."""
        result = check_naming_convention(data={"name": "my_repo!"})

        assert result == {
            "result": "fail",
            "message": "Repository name should not contain special characters.",
            "data": {"repository_name": "my_repo!"},
        }

    def test_passes_for_valid_repo_name(self):
        """A lowercase repository name with no spaces/special characters should pass."""
        result = check_naming_convention(data={"name": "my-repo_123"})

        assert result == {
            "result": "pass",
            "message": "Repository name follows GitHub Usage Policy Naming Conventions.",
            "data": {"repository_name": "my-repo_123"},
        }
