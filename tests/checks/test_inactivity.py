"""Tests for the inactivity check module."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock


from policy_methods_library.checks.inactivity import check_inactivity


# ---------------------------------------------------------------------------
# check_inactivity – data-driven path
# ---------------------------------------------------------------------------


class TestCheckInactivityWithData:
    def test_error_when_updated_at_missing_from_data(self):
        """data that does not contain 'updated_at' should return an error result."""
        result = check_inactivity(data={"name": "my-repo"})

        assert result == {
            "result": "error",
            "message": "Data must include 'updated_at' field.",
            "details": {"data": {"name": "my-repo"}},
        }

    def test_error_when_updated_at_is_not_a_string(self):
        """A non-string 'updated_at' value should return a type error result."""
        result = check_inactivity(data={"updated_at": 123})

        assert result == {
            "result": "error",
            "message": "Invalid type for 'updated_at'. Expected ISO 8601 string.",
            "details": {"updated_at": 123},
        }

    def test_error_when_updated_at_has_invalid_format(self):
        """An 'updated_at' value that is not ISO 8601 should return an error result."""
        result = check_inactivity(data={"updated_at": "not-a-date"})

        assert result == {
            "result": "error",
            "message": "Invalid date format for 'updated_at'. Expected ISO 8601 format.",
            "details": {"updated_at": "not-a-date"},
        }

    def test_fails_when_repo_inactive_for_over_a_year(self):
        """A repository last updated more than 365 days ago should fail."""
        old_date = (datetime.utcnow() - timedelta(days=400)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        result = check_inactivity(data={"updated_at": old_date})

        assert result["result"] == "fail"
        assert "inactive since" in result["message"]
        assert result["details"]["last_updated"] == old_date

    def test_passes_when_repo_updated_within_a_year(self):
        """A repository updated within the last 365 days should pass."""
        recent_date = (datetime.utcnow() - timedelta(days=30)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        result = check_inactivity(data={"updated_at": recent_date})

        assert result["result"] == "pass"
        assert "has been updated within the last year" in result["message"]
        assert result["details"] == {"last_updated": recent_date}

    def test_passes_when_repo_updated_exactly_under_a_year(self):
        """A repository updated exactly 364 days ago should pass."""
        near_boundary = (datetime.utcnow() - timedelta(days=364)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        result = check_inactivity(data={"updated_at": near_boundary})

        assert result["result"] == "pass"

    def test_fails_when_repo_updated_exactly_over_a_year(self):
        """A repository updated exactly 366 days ago should fail."""
        past_boundary = (datetime.utcnow() - timedelta(days=366)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        result = check_inactivity(data={"updated_at": past_boundary})

        assert result["result"] == "fail"


# ---------------------------------------------------------------------------
# check_inactivity – client-driven path
# ---------------------------------------------------------------------------


class TestCheckInactivityWithClient:
    def test_error_when_client_is_none(self):
        """No client and no data should return an error result."""
        result = check_inactivity()

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required if data is not provided.",
            "details": {},
        }

    def test_error_when_repository_name_is_none(self):
        """A client without a repository_name should return an error result."""
        client = MagicMock()

        result = check_inactivity(client=client)

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

        result = check_inactivity(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Error fetching repository data: connection timeout",
            "details": {},
        }

    def test_error_when_response_missing_updated_at(self):
        """An API response without 'updated_at' should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"name": "my-repo"}
        client.make_request.return_value = response

        result = check_inactivity(client=client, repository_name="my-repo")

        assert result["result"] == "error"
        assert "updated_at" in result["message"]

    def test_error_when_response_updated_at_is_not_a_string(self):
        """A non-string 'updated_at' in the API response should return a type error result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"updated_at": 123}
        client.make_request.return_value = response

        result = check_inactivity(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Invalid type for 'updated_at'. Expected ISO 8601 string.",
            "details": {"updated_at": 123},
        }

    def test_passes_for_recently_updated_repo_via_client(self):
        """A valid API response with a recent updated_at date should pass."""
        client = MagicMock()
        client.owner = "my-org"

        recent_date = (datetime.utcnow() - timedelta(days=10)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        response = MagicMock()
        response.json.return_value = {"updated_at": recent_date}
        client.make_request.return_value = response

        result = check_inactivity(client=client, repository_name="my-repo")

        assert result["result"] == "pass"
        assert (
            "Repository my-repo has been updated within the last year."
            in result["message"]
        )
        assert result["details"]["last_updated"] == recent_date

    def test_fails_for_inactive_repo_via_client(self):
        """A valid API response with an old updated_at date should fail."""
        client = MagicMock()
        client.owner = "my-org"

        old_date = (datetime.utcnow() - timedelta(days=500)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        response = MagicMock()
        response.json.return_value = {"updated_at": old_date}
        client.make_request.return_value = response

        result = check_inactivity(client=client, repository_name="my-repo")

        assert result["result"] == "fail"
        assert "Repository my-repo has been inactive since" in result["message"]
