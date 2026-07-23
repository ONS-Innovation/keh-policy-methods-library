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


class TestClassicProtectionApi:
    def test_pass_when_deletions_restricted_and_reviews_required(self):
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": False},
            "required_pull_request_reviews": {
                "require_code_owner_reviews": True,
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
            "details": {"Repository": "my-repo", "Branch": "main"},
        }

    def test_fail_when_deletions_are_allowed(self):
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": True},
            "required_pull_request_reviews": {
                "require_code_owner_reviews": True,
                "required_approving_review_count": 2,
            },
        }
        client.make_request.return_value = response

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "fail",
            "message": "Branch deletions must be restricted",
            "details": {"Repository": "my-repo", "Branch": "main"},
        }

    def test_fail_when_code_owner_reviews_not_required(self):
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": False},
            "required_pull_request_reviews": {
                "require_code_owner_reviews": False,
                "required_approving_review_count": 2,
            },
        }
        client.make_request.return_value = response

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "fail",
            "message": "Review before merge must be enabled",
            "details": {"Repository": "my-repo", "Branch": "main"},
        }

    def test_fail_when_approving_review_count_below_two(self):
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": False},
            "required_pull_request_reviews": {
                "require_code_owner_reviews": True,
                "required_approving_review_count": 1,
            },
        }
        client.make_request.return_value = response

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "fail",
            "message": "Review before merge must be enabled",
            "details": {"Repository": "my-repo", "Branch": "main"},
        }

    def test_restrict_deletions_checked_before_review_before_merge(self):
        """When both criteria fail, restrict_deletions should be reported first."""
        client = _make_client()
        response = MagicMock()
        response.json.return_value = {
            "allow_deletions": {"enabled": True},
            "required_pull_request_reviews": {
                "require_code_owner_reviews": False,
                "required_approving_review_count": 0,
            },
        }
        client.make_request.return_value = response

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result["message"] == "Branch deletions must be restricted"


class TestRulesetsFallback:
    """Covers the path where the classic protection endpoint 404s and the
    code falls back to /branches/{branch}/protected + rulesets."""

    def _http_error_response(self):
        response = MagicMock()
        response.json.side_effect = requests.exceptions.HTTPError("404 Not Found")
        return response

    def test_fail_when_branch_is_not_protected(self):
        client = _make_client()

        protection_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": False}

        client.make_request.side_effect = [protection_response, branch_response]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "fail",
            "message": "Branch protection is not enabled for branch main",
        }

    def test_pass_when_rules_satisfy_both_criteria(self):
        client = _make_client()

        protection_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": True}
        rules_response = MagicMock()
        rules_response.json.return_value = [
            {"type": "deletion", "parameters": {}},
            {
                "type": "pull_request",
                "parameters": {
                    "require_code_owner_review": True,
                    "required_approving_review_count": 2,
                },
            },
        ]

        client.make_request.side_effect = [
            protection_response,
            branch_response,
            rules_response,
        ]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "pass",
            "message": "Branch is protected",
            "details": {"Repository": "my-repo", "Branch": "main"},
        }

    def test_fail_when_no_deletion_rule_present(self):
        client = _make_client()

        protection_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": True}
        rules_response = MagicMock()
        rules_response.json.return_value = [
            {
                "type": "pull_request",
                "parameters": {
                    "require_code_owner_review": True,
                    "required_approving_review_count": 2,
                },
            },
        ]

        client.make_request.side_effect = [
            protection_response,
            branch_response,
            rules_response,
        ]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "fail",
            "message": "Branch deletions must be restricted",
            "details": {"Repository": "my-repo", "Branch": "main"},
        }

    def test_fail_when_pull_request_rule_insufficient(self):
        client = _make_client()

        protection_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": True}
        rules_response = MagicMock()
        rules_response.json.return_value = [
            {"type": "deletion", "parameters": {}},
            {
                "type": "pull_request",
                "parameters": {
                    "require_code_owner_review": True,
                    "required_approving_review_count": 1,
                },
            },
        ]

        client.make_request.side_effect = [
            protection_response,
            branch_response,
            rules_response,
        ]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "fail",
            "message": "Review before merge must be enabled",
            "details": {"Repository": "my-repo", "Branch": "main"},
        }

    def test_ignores_unknown_rule_types(self):
        """Rule types other than 'deletion'/'pull_request' should be ignored,
        not cause an error."""
        client = _make_client()

        protection_response = self._http_error_response()
        branch_response = MagicMock()
        branch_response.json.return_value = {"protected": True}
        rules_response = MagicMock()
        rules_response.json.return_value = [
            {"type": "deletion", "parameters": {}},
            {
                "type": "pull_request",
                "parameters": {
                    "require_code_owner_review": True,
                    "required_approving_review_count": 2,
                },
            },
            {"type": "required_signatures", "parameters": {}},
        ]

        client.make_request.side_effect = [
            protection_response,
            branch_response,
            rules_response,
        ]

        result = check_branch_protection(
            client=client, repository_name="my-repo", branch_name="main"
        )

        assert result == {
            "result": "pass",
            "message": "Branch is protected",
            "details": {"Repository": "my-repo", "Branch": "main"},
        }


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

    def test_error_when_required_pull_request_reviews_missing(self):
        """Documents current behavior: a missing optional key is caught by the
        broad except-Exception block and reported as an 'error', not a 'fail'.
        This is a known gap - see review notes - and this test should be
        updated once the code defensively handles missing keys with .get()."""
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
