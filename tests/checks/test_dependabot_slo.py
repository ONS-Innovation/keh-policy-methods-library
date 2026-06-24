"""Tests for the dependabot_slo get module."""

from datetime import datetime, timedelta, timezone
from unittest.mock import call, create_autospec

from requests import Response

from policy_methods_library.checks import dependabot_slo as dependabot_slo_check
from policy_methods_library.checks.dependabot_slo import (
    get_dependabot_slo,
)
from policy_methods_library.github.clients import GitHubRestClient

# Fixed "now" used by all SLO-boundary tests so results are deterministic.
_FIXED_NOW = datetime(2026, 6, 18, 12, 0, 0, tzinfo=timezone.utc)
_TEST_REPOSITORY = {"name": "my-repo"}


def _created_at(days_ago: float) -> str:
    """Return an ISO 8601 created_at string relative to _FIXED_NOW."""
    return (_FIXED_NOW - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _alert(number: int, *, created_at: str | None = None) -> dict:
    """Build a Dependabot alert fixture with repository info expected by the check."""
    alert = {
        "number": number,
        "state": "open",
        "repository": _TEST_REPOSITORY,
    }
    if created_at is not None:
        alert["created_at"] = created_at
    return alert


# ---------------------------------------------------------------------------
# get_dependabot_slo
# ---------------------------------------------------------------------------


class TestGetDependabotSLO:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = get_dependabot_slo(client=None)

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_verifying_organisation_raises_exception(self):
        """An exception during organisation verification should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = get_dependabot_slo(client=client)

        assert result == {
            "result": "error",
            "message": "An error occurred while verifying organisation authentication: connection timeout",
            "details": {},
        }

    def test_error_when_client_is_not_an_organisation(self):
        """A non-organisation /orgs response should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "User", "login": "my-org"}
        client.make_request.return_value = org_response

        result = get_dependabot_slo(client=client)

        assert result == {
            "result": "error",
            "message": "Client is not authenticated as an organisation.",
            "details": {"organisation": {"type": "User", "login": "my-org"}},
        }

    def test_error_when_organisation_response_is_not_a_dict(self):
        """A non-dictionary organisation response should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = ["unexpected", "response"]
        client.make_request.return_value = org_response

        result = get_dependabot_slo(client=client)

        assert result == {
            "result": "error",
            "message": "API response does not contain organisation data.",
            "details": {"response": ["unexpected", "response"]},
        }

    def test_error_when_fetching_dependabot_alerts_raises_exception(self):
        """An exception during dependabot alerts retrieval should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical"
            ):
                raise RuntimeError("connection timeout")
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result == {
            "result": "error",
            "message": "Error fetching Dependabot alerts: connection timeout.",
            "details": {},
        }

    def test_error_when_pull_request_response_is_not_a_list(self):
        """A non-list response payload should return an error result."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        response = create_autospec(Response, instance=True)
        response.json.return_value = {"message": "unexpected"}

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical"
            ):
                return response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result == {
            "result": "error",
            "message": "API response does not contain a list of Dependabot critical alerts.",
            "details": {"response": {"message": "unexpected"}},
        }

    def test_passes_when_no_open_dependabot_alerts_exist(self):
        """No open dependabot alerts should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        response = create_autospec(Response, instance=True)
        response.json.return_value = []
        response.links = {}

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical"
            ):
                return response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result == {
            "result": "pass",
            "message": "All alerts are within policy defined SLO.",
            "details": {},
        }

    def test_fails_when_open_dependabot_alerts_exist(self):
        """Open dependabot alerts should fail."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        fake_open_alert = {
            "number": 101,
            "state": "open",
            "html_url": "https://github.com/orgs/my-org/security/dependabot/101",
            "repository": _TEST_REPOSITORY,
        }

        response = create_autospec(Response, instance=True)
        response.json.return_value = [
            fake_open_alert,
        ]
        response.links = {}

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical"
            ):
                return response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result == {
            "result": "fail",
            "message": "Found 1 open Dependabot security alerts exceeding the policy-defined SLO.",
            "details": {
                "total_open_alerts": 1,
                "failing_alerts": 1,
                "number_exceeded_by_severity": {"critical": 1},
                "total_repositories_affected": 1,
                "repositories": {"my-org/my-repo": {"critical": 1}},
            },
        }

    def test_sorts_dependabot_alerts_correctly(self):
        """No open dependabot alerts should pass."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        fake_open_critical_alert = {
            "number": 101,
            "state": "open",
            "html_url": "https://github.com/orgs/my-org/security/dependabot/101",
            "repository": _TEST_REPOSITORY,
        }

        fake_open_low_alert = {
            "number": 102,
            "state": "open",
            "html_url": "https://github.com/orgs/my-org/security/dependabot/102",
            "repository": _TEST_REPOSITORY,
        }

        critical_response = create_autospec(Response, instance=True)
        critical_response.json.return_value = [fake_open_critical_alert]
        critical_response.links = {}

        low_response = create_autospec(Response, instance=True)
        low_response.json.return_value = [fake_open_low_alert]
        low_response.links = {}

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical"
            ):
                return critical_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=low"
            ):
                return low_response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = get_dependabot_slo(client=client, levels=["critical", "low"])

        assert result == {
            "result": "fail",
            "message": "Found 2 open Dependabot security alerts exceeding the policy-defined SLO.",
            "details": {
                "total_open_alerts": 2,
                "failing_alerts": 2,
                "number_exceeded_by_severity": {"critical": 1, "low": 1},
                "total_repositories_affected": 1,
                "repositories": {"my-org/my-repo": {"critical": 1, "low": 0}},
            },
        }

    def test_calls_expected_dependabot_alert_endpoint(self):
        """The check should call the dependabot alerts endpoint for the repository."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        response = create_autospec(Response, instance=True)
        response.json.return_value = []
        response.links = {}

        def make_request_side_effect(method: str, endpoint: str):
            if endpoint == "/orgs/my-org":
                return org_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical"
            ):
                return response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        get_dependabot_slo(client=client, levels=["critical"])

        client.make_request.assert_has_calls(
            [
                call("GET", "/orgs/my-org"),
                call(
                    "GET",
                    "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical",
                ),
            ]
        )

    def test_handles_paginated_dependabot_alerts(self):
        """The check should handle paginated dependabot alerts across multiple pages."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        page1_alerts = [
            {
                "number": 101,
                "state": "open",
                "html_url": "https://github.com/orgs/my-org/security/dependabot/101",
                "repository": _TEST_REPOSITORY,
            },
        ]
        page2_alerts = [
            {
                "number": 102,
                "state": "open",
                "html_url": "https://github.com/orgs/my-org/security/dependabot/102",
                "repository": _TEST_REPOSITORY,
            },
        ]

        # First page response with a next link
        page1_response = create_autospec(Response, instance=True)
        page1_response.json.return_value = page1_alerts
        page1_response.links = {
            "next": {
                "url": "https://api.github.com/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical&page=2"
            },
        }

        # Second page response without a next link
        page2_response = create_autospec(Response, instance=True)
        page2_response.json.return_value = page2_alerts
        page2_response.links = {}

        def make_request_side_effect(method: str, endpoint: str, **kwargs):
            if endpoint == "/orgs/my-org":
                return org_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical"
            ):
                return page1_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical&page=2"
            ):
                return page2_response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result == {
            "result": "fail",
            "message": "Found 2 open Dependabot security alerts exceeding the policy-defined SLO.",
            "details": {
                "total_open_alerts": 2,
                "failing_alerts": 2,
                "number_exceeded_by_severity": {"critical": 2},
                "total_repositories_affected": 1,
                "repositories": {"my-org/my-repo": {"critical": 1}},
            },
        }

        # Verify pagination was handled correctly
        client.make_request.assert_has_calls(
            [
                call("GET", "/orgs/my-org"),
                call(
                    "GET",
                    "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical",
                ),
                call(
                    "GET",
                    "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical&page=2",
                ),
            ]
        )

    def test_handles_dependabot_alert_with_no_links_attribute(self):
        """The check should handle responses where links is None."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"

        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        open_critical_alert = {
            "number": 101,
            "state": "open",
            "html_url": "https://github.com/orgs/my-org/security/dependabot/101",
            "repository": _TEST_REPOSITORY,
        }

        response = create_autospec(Response, instance=True)
        response.json.return_value = [open_critical_alert]
        response.links = None

        def make_request_side_effect(method: str, endpoint: str, **kwargs):
            if endpoint == "/orgs/my-org":
                return org_response
            if (
                endpoint
                == "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical"
            ):
                return response
            raise AssertionError(f"Unexpected endpoint called: {endpoint}")

        client.make_request.side_effect = make_request_side_effect

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result == {
            "result": "fail",
            "message": "Found 1 open Dependabot security alerts exceeding the policy-defined SLO.",
            "details": {
                "total_open_alerts": 1,
                "failing_alerts": 1,
                "number_exceeded_by_severity": {"critical": 1},
                "total_repositories_affected": 1,
                "repositories": {"my-org/my-repo": {"critical": 1}},
            },
        }

        # Verify no additional pages were requested
        assert client.make_request.call_count == 2

        client.make_request.assert_has_calls(
            [
                call("GET", "/orgs/my-org"),
                call(
                    "GET",
                    "/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical",
                ),
            ]
        )

    def _make_org_client(self):
        """Return an autospecced client pre-configured to pass the org check."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.owner = "my-org"
        org_response = create_autospec(Response, instance=True)
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        def _side_effect(method, endpoint, **kwargs):
            if endpoint == "/orgs/my-org":
                return org_response
            raise AssertionError(f"Unexpected endpoint: {endpoint}")

        client.make_request.side_effect = _side_effect
        return client

    def _setup_alert_response(self, client, level, alerts):
        """Attach a single-page alert response for one severity level."""
        alert_response = create_autospec(Response, instance=True)
        alert_response.json.return_value = alerts
        alert_response.links = {}
        original = client.make_request.side_effect

        def _side_effect(method, endpoint, **kwargs):
            if (
                endpoint
                == f"/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity={level}"
            ):
                return alert_response
            return original(method, endpoint, **kwargs)

        client.make_request.side_effect = _side_effect

    def _set_fixed_now(self):
        """Set module-global NOW so SLO boundary tests stay deterministic."""
        dependabot_slo_check.NOW = _FIXED_NOW

    def test_passes_when_all_alerts_are_within_slo(self):
        """Alerts that have not yet exceeded their SLO should not cause a failure."""
        client = self._make_org_client()
        self._set_fixed_now()
        # 4 days old — critical SLO is 5 days, so still within SLO.
        alert = _alert(1, created_at=_created_at(4))
        self._setup_alert_response(client, "critical", [alert])

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result == {
            "result": "pass",
            "message": "All alerts are within policy defined SLO.",
            "details": {},
        }

    def test_fails_when_alert_exceeds_slo(self):
        """An alert older than its SLO threshold should be returned as failing."""
        client = self._make_org_client()
        self._set_fixed_now()
        # 8 days old — critical SLO is 5 working days, so exceeded.
        alert = _alert(1, created_at=_created_at(8))
        self._setup_alert_response(client, "critical", [alert])

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result == {
            "result": "fail",
            "message": "Found 1 open Dependabot security alerts exceeding the policy-defined SLO.",
            "details": {
                "total_open_alerts": 1,
                "failing_alerts": 1,
                "number_exceeded_by_severity": {"critical": 1},
                "total_repositories_affected": 1,
                "repositories": {"my-org/my-repo": {"critical": 1}},
            },
        }

    def test_passes_when_alert_is_exactly_at_slo_boundary(self):
        """An alert created exactly at the SLO boundary is still compliant."""
        client = self._make_org_client()
        self._set_fixed_now()
        # Exactly at deadline: 7 days old maps to 5 working days from creation.
        alert = _alert(1, created_at=_created_at(7))
        self._setup_alert_response(client, "critical", [alert])

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result["result"] == "pass"
        assert result["details"] == {}

    def test_passes_when_alert_is_one_second_within_boundary(self):
        """An alert one second younger than the SLO threshold should not fail."""
        client = self._make_org_client()
        self._set_fixed_now()
        # Just under 5 days old (5 days minus 1 second).
        created_at = (_FIXED_NOW - timedelta(days=5) + timedelta(seconds=1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        alert = _alert(1, created_at=created_at)
        self._setup_alert_response(client, "critical", [alert])

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result["result"] == "pass"

    def test_fails_when_alert_has_missing_created_at(self):
        """An alert without a created_at field is treated as non-compliant."""
        client = self._make_org_client()
        self._set_fixed_now()
        alert = _alert(1)
        self._setup_alert_response(client, "critical", [alert])

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result["result"] == "fail"
        assert result["details"]["total_open_alerts"] == 1
        assert result["details"]["failing_alerts"] == 1

    def test_fails_when_alert_has_invalid_created_at(self):
        """An alert with an unparseable created_at is treated as non-compliant."""
        client = self._make_org_client()
        self._set_fixed_now()
        alert = _alert(1, created_at="not-a-date")
        self._setup_alert_response(client, "critical", [alert])

        result = get_dependabot_slo(client=client, levels=["critical"])

        assert result["result"] == "fail"
        assert result["details"]["total_open_alerts"] == 1

    def test_only_exceeded_alerts_returned_in_mixed_severity_check(self):
        """Only alerts that exceed their per-severity SLO appear in failing_alerts."""
        client = self._make_org_client()
        self._set_fixed_now()

        # critical: 8 days old (SLO 5 working days) → exceeded
        critical_alert = _alert(1, created_at=_created_at(8))
        # high: 10 days old (SLO 15) → within SLO
        high_alert = _alert(2, created_at=_created_at(10))

        self._setup_alert_response(client, "critical", [critical_alert])
        self._setup_alert_response(client, "high", [high_alert])

        result = get_dependabot_slo(client=client, levels=["critical", "high"])

        assert result == {
            "result": "fail",
            "message": "Found 1 open Dependabot security alerts exceeding the policy-defined SLO.",
            "details": {
                "total_open_alerts": 2,
                "failing_alerts": 1,
                "number_exceeded_by_severity": {"critical": 1, "high": 0},
                "total_repositories_affected": 1,
                "repositories": {"my-org/my-repo": {"critical": 1, "high": 0}},
            },
        }

    def test_slo_thresholds_applied_per_severity(self):
        """Each severity level uses its own SLO threshold."""
        client = self._make_org_client()
        self._set_fixed_now()

        # 25 days old: exceeds critical/high working-day SLOs, still within medium/low.
        alert = _alert(1, created_at=_created_at(25))

        for level in ["critical", "high", "medium", "low"]:
            self._setup_alert_response(client, level, [alert])

        result = get_dependabot_slo(
            client=client,
            levels=["critical", "high", "medium", "low"],
        )

        assert result["result"] == "fail"
        counts = result["details"]["number_exceeded_by_severity"]
        assert counts["critical"] == 1  # 16d > 5d SLO
        assert counts["high"] == 1  # 16d > 15d SLO
        assert counts["medium"] == 0  # 16d < 60d SLO
        assert counts["low"] == 0  # 16d < 90d SLO
        assert result["details"]["total_open_alerts"] == 4
