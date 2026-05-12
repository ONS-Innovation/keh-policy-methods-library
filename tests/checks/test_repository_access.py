"""Tests for the repository_access check module."""

from unittest.mock import MagicMock

from policy_methods_library.checks.repository_access import check_repository_access


# ---------------------------------------------------------------------------
# check_repository_access
# ---------------------------------------------------------------------------


class TestCheckRepositoryAccess:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = check_repository_access(client=None, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_empty(self):
        """An empty repository name should return an error result."""
        client = MagicMock()

        result = check_repository_access(client=client, repository_name="")

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_error_when_client_request_raises_exception(self):
        """An exception during the API call should return an error result with the error message."""
        client = MagicMock()
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_repository_access(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "An error occurred while checking repository access: connection timeout",
            "details": {},
        }

    def test_error_when_response_is_not_a_list(self):
        """A non-list response payload should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"message": "unexpected"}
        client.make_request.return_value = response

        result = check_repository_access(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "API response does not contain a list of collaborators.",
            "details": {"response": {"message": "unexpected"}},
        }

    def test_fails_when_individual_users_have_access(self):
        """A repository with direct individual collaborators should fail."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = [
            {
                "login": "alice",
                "type": "User",
                "permissions": {"admin": False, "push": True, "pull": True},
            },
            {
                "login": "my-org/admin-team",
                "type": "Team",
                "permissions": {"admin": True, "push": True, "pull": True},
            },
        ]
        client.make_request.return_value = response

        result = check_repository_access(client=client, repository_name="my-repo")

        assert result == {
            "result": "fail",
            "message": "Repository 'my-repo' has individual users with access. It is recommended to use teams for access management.",
            "details": {
                "repository_name": "my-repo",
                "individual_collaborators": [
                    {
                        "login": "alice",
                        "permissions": {
                            "admin": False,
                            "push": True,
                            "pull": True,
                        },
                    }
                ],
            },
        }

    def test_passes_when_no_individual_users_have_access(self):
        """A repository with no direct individual collaborators should pass."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = [
            {
                "login": "my-org/devops-team",
                "type": "Team",
                "permissions": {"admin": False, "push": True, "pull": True},
            },
            {
                "login": "renovate[bot]",
                "type": "Bot",
                "permissions": {"admin": False, "push": False, "pull": True},
            },
        ]
        client.make_request.return_value = response

        result = check_repository_access(client=client, repository_name="my-repo")

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' does not have any individual users with access.",
            "details": {
                "repository_name": "my-repo",
                "individual_collaborators": [],
            },
        }
