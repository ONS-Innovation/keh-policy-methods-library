"""Tests for the team_maintainer check module."""

from unittest.mock import create_autospec

from requests import Response

from policy_methods_library.checks.team_maintainer import check_team_maintainer
from policy_methods_library.github.clients import GitHubRestClient


# ---------------------------------------------------------------------------
# check_team_maintainer
# ---------------------------------------------------------------------------


class TestCheckTeamMaintainer:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = check_team_maintainer(client=None, team_slug="my-team")

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_team_slug_is_none(self):
        """A None team_slug should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        result = check_team_maintainer(client=client, team_slug=None)

        assert result == {
            "result": "error",
            "message": "Team slug is required.",
            "details": {},
        }

    def test_error_when_team_slug_is_empty_string(self):
        """An empty team_slug should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        result = check_team_maintainer(client=client, team_slug="")

        assert result == {
            "result": "error",
            "message": "Team slug is required.",
            "details": {},
        }

    def test_error_when_client_raises_exception(self):
        """An exception during the API call should return an error result with the error message."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_team_maintainer(client=client, team_slug="my-team")

        assert result == {
            "result": "error",
            "message": "An error occurred while checking team maintainers: connection timeout",
            "details": {},
        }

    def test_error_when_response_is_not_a_list(self):
        """A non-list response payload should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = {"message": "unexpected"}
        client.make_request.return_value = response

        result = check_team_maintainer(client=client, team_slug="my-team")

        assert result == {
            "result": "error",
            "message": "API response does not contain expected team members data.",
            "details": {"response": {"message": "unexpected"}},
        }

    def test_fails_when_team_has_no_maintainers(self):
        """A team with zero maintainers should fail."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = []
        client.make_request.return_value = response

        result = check_team_maintainer(client=client, team_slug="my-team")

        assert result == {
            "result": "fail",
            "message": "Team 'my-team' does not have any maintainers.",
            "details": {
                "team_slug": "my-team",
                "maintainer_count": 0,
                "maintainers": [],
            },
        }

    def test_passes_when_team_has_one_maintainer(self):
        """A team with one maintainer should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = [
            {
                "login": "alice",
                "id": 12345,
                "type": "User",
            }
        ]
        client.make_request.return_value = response

        result = check_team_maintainer(client=client, team_slug="my-team")

        assert result == {
            "result": "pass",
            "message": "Team 'my-team' has 1 maintainer(s).",
            "details": {
                "team_slug": "my-team",
                "maintainer_count": 1,
                "maintainers": [
                    {
                        "login": "alice",
                        "id": 12345,
                    }
                ],
            },
        }

    def test_passes_when_team_has_multiple_maintainers(self):
        """A team with multiple maintainers should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = [
            {
                "login": "alice",
                "id": 12345,
                "type": "User",
            },
            {
                "login": "bob",
                "id": 67890,
                "type": "User",
            },
        ]
        client.make_request.return_value = response

        result = check_team_maintainer(client=client, team_slug="my-team")

        assert result == {
            "result": "pass",
            "message": "Team 'my-team' has 2 maintainer(s).",
            "details": {
                "team_slug": "my-team",
                "maintainer_count": 2,
                "maintainers": [
                    {
                        "login": "alice",
                        "id": 12345,
                    },
                    {
                        "login": "bob",
                        "id": 67890,
                    },
                ],
            },
        }

    def test_calls_correct_api_endpoint(self):
        """The check should call the correct API endpoint with role=maintainer filter."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = []
        client.make_request.return_value = response

        check_team_maintainer(client=client, team_slug="my-team")

        client.make_request.assert_called_once_with(
            "GET", "/orgs/my-org/teams/my-team/members?role=maintainer"
        )

    def test_passes_with_additional_response_fields(self):
        """Additional fields in the API response should not affect the check result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        response = create_autospec(Response, instance=True)
        response.json.return_value = [
            {
                "login": "alice",
                "id": 12345,
                "type": "User",
                "avatar_url": "https://example.com/avatar.jpg",
                "url": "https://api.github.com/users/alice",
                "html_url": "https://github.com/alice",
            }
        ]
        client.make_request.return_value = response

        result = check_team_maintainer(client=client, team_slug="my-team")

        assert result["result"] == "pass"
        assert result["details"]["maintainer_count"] == 1
