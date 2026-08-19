"""Unit tests for check_branch_protection."""

import requests
from unittest.mock import create_autospec, MagicMock
from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.checks.branch_protection import check_branch_protection


def _make_client():
    client = create_autospec(GitHubRestClient)
    client.owner = "my-org"
    return client


class TestCheckBranchProtectionInputValidation:
    def test_error_when_client_is_none(self):
        result = check_branch_protection(
            client=None, repository_name="my-repo", branch_name="main"
        )
        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_repository_name_is_none(self):
        client = _make_client()
        result = check_branch_protection(
            client=client, repository_name=None, branch_name="main"
        )
        assert result == {
            "result": "error",
            "message": "Repository name is required.",
            "details": {},
        }

    def test_error_when_branch_name_is_none(self):
        client = _make_client()
        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name=None
        )
        assert result == {
            "result": "error",
            "message": "Branch name is required.",
            "details": {},
        }


class TestLegacyBranchProtection:
    def test_pass_when_deletions_restricted_and_reviews_required(self):
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": False},
            "required_pull_request_reviews": {
                "required_approving_review_count": 2,
            },
        }
        client.make_request.return_value = response

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "pass",
            "message": "Branch is protected",
            "details": {
                "repository": "my-repo",
                "branch": "main",
                "criteria": {
                    "restrict_deletions": True,
                    "review_before_merge": True,
                },
            },
        }

    def test_fail_when_deletions_are_allowed(self):
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": True},
            "required_pull_request_reviews": {
                "required_approving_review_count": 2,
            },
        }
        client.make_request.return_value = response

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "fail",
            "message": (
                "Branch 'main' is unprotected. Branches should restrict "
                "deletions and require a review before merge."
            ),
            "details": {
                "repository": "my-repo",
                "branch": "main",
                "criteria": {
                    "restrict_deletions": False,
                    "review_before_merge": True,
                },
            },
        }

    def test_fail_when_approving_review_count_below_two(self):
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": False},
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
            },
        }
        client.make_request.return_value = response

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["result"] == "fail"
        assert result["details"]["criteria"] == {
            "restrict_deletions": True,
            "review_before_merge": False,
        }

    def test_fail_when_both_criteria_fail(self):
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": True},
            "required_pull_request_reviews": {
                "required_approving_review_count": 0,
            },
        }
        client.make_request.return_value = response

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["result"] == "fail"
        assert result["details"]["criteria"] == {
            "restrict_deletions": False,
            "review_before_merge": False,
        }


class TestRulesetsFallback:
    """Covers the path where the legacy protection endpoint raises HTTPError
    and the code falls back to /branches/{branch} + rulesets."""

    def _http_error_response(self):
        response = MagicMock()
        response.json.side_effect = requests.exceptions.HTTPError("404 Not Found")
        return response

    def test_fail_when_branch_is_not_protected(self):
        client = _make_client()

        legacy_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": False}

        client.make_request.side_effect = [legacy_response, branch_response]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "fail",
            "message": (
                "Branch 'main' is unprotected. Branches should restrict "
                "deletions and require a review before merge."
            ),
            "details": {},
        }

    def test_pass_when_rules_satisfy_both_criteria(self):
        client = _make_client()

        legacy_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": True}
        rules_response = MagicMock()
        rules_response.json.return_value = [
            {"type": "deletion", "parameters": {}},
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 2,
                },
            },
        ]

        client.make_request.side_effect = [
            legacy_response,
            branch_response,
            rules_response,
        ]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "pass",
            "message": "Branch is protected",
            "details": {
                "repository": "my-repo",
                "branch": "main",
                "criteria": {
                    "restrict_deletions": True,
                    "review_before_merge": True,
                },
            },
        }

    def test_fail_when_no_deletion_rule_present(self):
        client = _make_client()

        legacy_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": True}
        rules_response = MagicMock()
        rules_response.json.return_value = [
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 2,
                },
            },
        ]

        client.make_request.side_effect = [
            legacy_response,
            branch_response,
            rules_response,
        ]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["result"] == "fail"
        assert result["details"] == {
            "repository": "my-repo",
            "branch": "main",
            "criteria": {
                "restrict_deletions": False,
                "review_before_merge": True,
            },
        }

    def test_fail_when_pull_request_rule_insufficient(self):
        client = _make_client()

        legacy_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": True}
        rules_response = MagicMock()
        rules_response.json.return_value = [
            {"type": "deletion", "parameters": {}},
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 1,
                },
            },
        ]

        client.make_request.side_effect = [
            legacy_response,
            branch_response,
            rules_response,
        ]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["result"] == "fail"
        assert result["details"]["criteria"] == {
            "restrict_deletions": True,
            "review_before_merge": False,
        }

    def test_ignores_unknown_rule_types(self):
        """Rule types other than 'deletion'/'pull_request' should be ignored,
        not cause an error."""
        client = _make_client()

        legacy_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": True}
        rules_response = MagicMock()
        rules_response.json.return_value = [
            {"type": "deletion", "parameters": {}},
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 2,
                },
            },
            {"type": "required_signatures", "parameters": {}},
        ]

        client.make_request.side_effect = [
            legacy_response,
            branch_response,
            rules_response,
        ]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["result"] == "pass"


class TestGenericErrorHandling:
    def test_error_returned_when_unexpected_exception_raised(self):
        client = _make_client()
        client.make_request.side_effect = ValueError("boom")

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["result"] == "error"
        assert "boom" in result["message"]
        assert result["details"] == {}

    def test_error_when_rulesets_check_raises_unexpected_exception(self):
        client = _make_client()
        client.make_request.side_effect = [
            requests.exceptions.HTTPError("404 Not Found"),
            ValueError("rulesets boom"),
        ]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["result"] == "error"
        assert "rulesets boom" in result["message"]
        assert result["details"] == {}

    def test_fail_when_rulesets_branch_lookup_raises_http_error(self):
        client = _make_client()
        not_found = requests.exceptions.HTTPError("404 Not Found")
        client.make_request.side_effect = [not_found, not_found]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["result"] == "fail"
        assert result["message"] == (
            "Branch 'main' is unprotected. Branches should restrict deletions "
            "and require a review before merge."
        )
        assert result["details"] == {}

    def test_error_when_required_pull_request_reviews_missing(self):
        """Documents current behavior: a missing optional key is caught by the
        broad except-Exception block in check_branch_protection and reported
        as an 'error', not a 'fail'. This is a known gap (see review notes)
        and should be updated once the code defensively handles missing keys
        with .get() instead of direct indexing."""
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": False},
            # required_pull_request_reviews intentionally omitted
        }
        client.make_request.return_value = response

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["result"] == "error"
