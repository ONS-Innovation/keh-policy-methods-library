"""Tests for the external_pull_request check module."""

from unittest.mock import MagicMock, call

from requests import HTTPError

from policy_methods_library.checks.external_pull_request import (
    check_external_pull_request,
)


# ---------------------------------------------------------------------------
# check_external_pull_request
# ---------------------------------------------------------------------------


class TestCheckExternalPullRequest:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = check_external_pull_request(client=None, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_empty(self):
        """An empty repository name should return an error result."""
        client = MagicMock()

        result = check_external_pull_request(client=client, repository_name="")

        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_error_when_verifying_organisation_raises_exception(self):
        """An exception during organisation verification should return an error result."""
        client = MagicMock()
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "An error occurred while verifying organisation authentication: connection timeout",
            "details": {},
        }

    def test_error_when_client_is_not_an_organisation(self):
        """A non-organisation /orgs response should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "User", "login": "my-org"}
        client.make_request.return_value = org_response

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Client is not authenticated as an organisation.",
            "details": {"organisation": {"type": "User", "login": "my-org"}},
        }

    def test_error_when_organisation_response_is_not_a_dict(self):
        """A non-dictionary organisation response should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = ["unexpected", "response"]
        client.make_request.return_value = org_response

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "API response does not contain organisation data.",
            "details": {"response": ["unexpected", "response"]},
        }

    def test_error_when_fetching_pull_requests_raises_exception(self):
        """An exception during pull request retrieval should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                raise RuntimeError("connection timeout")
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "An error occurred while retrieving pull requests: connection timeout",
            "details": {},
        }

    def test_error_when_pull_request_response_is_not_a_list(self):
        """A non-list response payload should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        response = MagicMock()
        response.json.return_value = {"message": "unexpected"}

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "API response does not contain a list of pull requests.",
            "details": {"response": {"message": "unexpected"}},
        }

    def test_error_when_pull_request_author_is_missing(self):
        """A pull request without an author login should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        pulls_response = MagicMock()
        pulls_response.json.return_value = [{"number": 1, "title": "Improve docs"}]

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return pulls_response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "Pull request data is missing author username.",
            "details": {"pull_request": {"number": 1, "title": "Improve docs"}},
        }

    def test_passes_when_no_open_pull_requests_exist(self):
        """No open pull requests should pass."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        pulls_response = MagicMock()
        pulls_response.json.return_value = []

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return pulls_response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' has no external pull requests.",
            "details": {
                "repository_name": "my-repo",
                "external_pull_requests": [],
            },
        }

    def test_passes_when_all_pull_request_authors_are_org_members(self):
        """A repository with PRs authored by org members only should pass."""
        client = MagicMock()
        client.owner = "my-org"

        pulls_response = MagicMock()
        pulls_response.json.return_value = [
            {"number": 1, "title": "Update workflow", "user": {"login": "alice"}},
            {"number": 2, "title": "Bump deps", "user": {"login": "bob"}},
        ]

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        membership_response = MagicMock()
        membership_response.status_code = 204

        def make_request_side_effect(method: str, endpoint: str, **kwargs):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return pulls_response
            if endpoint in [
                "/orgs/my-org/members/alice",
                "/orgs/my-org/members/bob",
            ]:
                assert kwargs.get("allow_redirects") is False
                return membership_response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' has no external pull requests.",
            "details": {
                "repository_name": "my-repo",
                "external_pull_requests": [],
            },
        }

    def test_passes_when_only_open_pull_request_is_dependabot(self):
        """A dependabot PR should be ignored as an allowed exception."""
        client = MagicMock()
        client.owner = "my-org"

        pulls_response = MagicMock()
        pulls_response.json.return_value = [
            {
                "number": 77,
                "title": "Bump urllib3 from 2.2.1 to 2.2.2",
                "user": {"login": "dependabot[bot]"},
            }
        ]

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        def make_request_side_effect(method: str, endpoint: str, **kwargs):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return pulls_response
            if endpoint == "/orgs/my-org/members/dependabot[bot]":
                raise AssertionError("dependabot[bot] membership should not be checked")
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "pass",
            "message": "Repository 'my-repo' has no external pull requests.",
            "details": {
                "repository_name": "my-repo",
                "external_pull_requests": [],
            },
        }

    def test_ignores_dependabot_and_still_fails_for_other_external_authors(self):
        """Dependabot should be ignored while non-members still cause a failure."""
        client = MagicMock()
        client.owner = "my-org"

        pulls_response = MagicMock()
        pulls_response.json.return_value = [
            {
                "number": 77,
                "title": "Bump urllib3 from 2.2.1 to 2.2.2",
                "user": {"login": "dependabot[bot]"},
            },
            {
                "number": 88,
                "title": "Community patch",
                "user": {"login": "external-contributor"},
            },
        ]

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        def make_request_side_effect(method: str, endpoint: str, **kwargs):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return pulls_response
            if endpoint == "/orgs/my-org/members/dependabot[bot]":
                raise AssertionError("dependabot[bot] membership should not be checked")
            if endpoint == "/orgs/my-org/members/external-contributor":
                assert kwargs.get("allow_redirects") is False
                not_member_response = MagicMock()
                not_member_response.status_code = 404
                raise HTTPError("Not Found", response=not_member_response)
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "fail",
            "message": "Repository 'my-repo' has external pull requests authored by non-organisation members.",
            "details": {
                "repository_name": "my-repo",
                "external_pull_requests": [
                    {
                        "number": 88,
                        "title": "Community patch",
                        "author": "external-contributor",
                    }
                ],
            },
        }

    def test_fails_when_external_pull_request_exists(self):
        """A repository with at least one non-member PR author should fail."""
        client = MagicMock()
        client.owner = "my-org"

        pulls_response = MagicMock()
        pulls_response.json.return_value = [
            {"number": 101, "title": "Internal PR", "user": {"login": "alice"}},
            {
                "number": 202,
                "title": "External contribution",
                "user": {"login": "external-contributor"},
            },
        ]

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        membership_response = MagicMock()
        membership_response.status_code = 204

        def make_request_side_effect(method: str, endpoint: str, **kwargs):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return pulls_response

            if endpoint == "/orgs/my-org/members/alice":
                assert kwargs.get("allow_redirects") is False
                return membership_response

            if endpoint == "/orgs/my-org/members/external-contributor":
                assert kwargs.get("allow_redirects") is False
                not_member_response = MagicMock()
                not_member_response.status_code = 404
                raise HTTPError("Not Found", response=not_member_response)

            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "fail",
            "message": "Repository 'my-repo' has external pull requests authored by non-organisation members.",
            "details": {
                "repository_name": "my-repo",
                "external_pull_requests": [
                    {
                        "number": 202,
                        "title": "External contribution",
                        "author": "external-contributor",
                    }
                ],
            },
        }

    def test_error_when_membership_check_returns_unexpected_http_error(self):
        """A non-404 HTTP error during membership check should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        pulls_response = MagicMock()
        pulls_response.json.return_value = [
            {
                "number": 11,
                "title": "Refactor check logic",
                "user": {"login": "alice"},
            }
        ]

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        def make_request_side_effect(method: str, endpoint: str, **kwargs):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return pulls_response

            if endpoint == "/orgs/my-org/members/alice":
                assert kwargs.get("allow_redirects") is False
                forbidden_response = MagicMock()
                forbidden_response.status_code = 403
                raise HTTPError("Forbidden", response=forbidden_response)

            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "An error occurred while checking pull request authors: Forbidden",
            "details": {},
        }

    def test_error_when_membership_check_returns_302(self):
        """A 302 from membership check should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        pulls_response = MagicMock()
        pulls_response.json.return_value = [
            {
                "number": 11,
                "title": "Refactor check logic",
                "user": {"login": "alice"},
            }
        ]

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        membership_response = MagicMock()
        membership_response.status_code = 302

        def make_request_side_effect(method: str, endpoint: str, **kwargs):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return pulls_response

            if endpoint == "/orgs/my-org/members/alice":
                assert kwargs.get("allow_redirects") is False
                return membership_response

            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = check_external_pull_request(client=client, repository_name="my-repo")

        assert result == {
            "result": "error",
            "message": "An error occurred while checking pull request authors: Unexpected membership response status code: 302",
            "details": {},
        }

    def test_calls_expected_pull_request_endpoint(self):
        """The check should call the pull requests endpoint for the repository."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        pulls_response = MagicMock()
        pulls_response.json.return_value = []

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if endpoint == "/repos/my-org/my-repo/pulls?state=open":
                return pulls_response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        check_external_pull_request(client=client, repository_name="my-repo")

        client.make_request.assert_has_calls(
            [
                call("GET", "/orgs/my-org"),
                call("GET", "/repos/my-org/my-repo/pulls?state=open"),
            ]
        )
