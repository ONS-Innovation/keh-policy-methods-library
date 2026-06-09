"""Tests for the dependabot_slo get module."""

from unittest.mock import MagicMock, call

from policy_methods_library.checks.dependabot_slo import (
    get_dependabot_slo,
)

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
        client = MagicMock()
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
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
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
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
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
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
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
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        response = MagicMock()
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
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        response = MagicMock()
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
            "message": "No open Dependabot security alerts found.",
            "details": {
                "total_open_alerts": 0,
                "number_alerts_by_severity": {"critical": 0},
            },
        }

    def test_fails_when_open_dependabot_alerts_exist(self):
        """Open dependabot alerts should fail."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        fake_open_alert = {
            "number": 101,
            "state": "open",
            "html_url": "https://github.com/orgs/my-org/security/dependabot/101",
        }

        response = MagicMock()
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
            "message": "Found 1 open Dependabot security alerts. Please resolve these alerts within the policy-defined SLO timeline.",
            "details": {
                "total_open_alerts": 1,
                "number_alerts_by_severity": {"critical": 1},
                "failing_alerts": {"critical": [fake_open_alert]},
            },
        }

    def test_sorts_dependabot_alerts_correctly(self):
        """No open dependabot alerts should pass."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        fake_open_critical_alert = {
            "number": 101,
            "state": "open",
            "html_url": "https://github.com/orgs/my-org/security/dependabot/101",
        }

        fake_open_low_alert = {
            "number": 102,
            "state": "open",
            "html_url": "https://github.com/orgs/my-org/security/dependabot/102",
        }

        critical_response = MagicMock()
        critical_response.json.return_value = [fake_open_critical_alert]
        critical_response.links = {}

        low_response = MagicMock()
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
            "message": "Found 2 open Dependabot security alerts. Please resolve these alerts within the policy-defined SLO timeline.",
            "details": {
                "total_open_alerts": 2,
                "number_alerts_by_severity": {"critical": 1, "low": 1},
                "failing_alerts": {
                    "critical": [fake_open_critical_alert],
                    "low": [fake_open_low_alert],
                },
            },
        }

    def test_calls_expected_dependabot_alert_endpoint(self):
        """The check should call the dependabot alerts endpoint for the repository."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        response = MagicMock()
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
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        page1_alerts = [
            {
                "number": 101,
                "state": "open",
                "html_url": "https://github.com/orgs/my-org/security/dependabot/101",
            },
        ]
        page2_alerts = [
            {
                "number": 102,
                "state": "open",
                "html_url": "https://github.com/orgs/my-org/security/dependabot/102",
            },
        ]

        # First page response with a next link
        page1_response = MagicMock()
        page1_response.json.return_value = page1_alerts
        page1_response.links = {
            "next": {
                "url": "https://api.github.com/orgs/my-org/dependabot/alerts?per_page=100&state=open&severity=critical&page=2"
            },
        }

        # Second page response without a next link
        page2_response = MagicMock()
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
            "message": "Found 2 open Dependabot security alerts. Please resolve these alerts within the policy-defined SLO timeline.",
            "details": {
                "total_open_alerts": 2,
                "number_alerts_by_severity": {"critical": 2},
                "failing_alerts": {"critical": page1_alerts + page2_alerts},
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
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization", "login": "my-org"}

        open_critical_alert = (
            {
                "number": 101,
                "state": "open",
                "html_url": "https://github.com/orgs/my-org/security/dependabot/101",
            },
        )

        response = MagicMock()
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
            "message": "Found 1 open Dependabot security alerts. Please resolve these alerts within the policy-defined SLO timeline.",
            "details": {
                "total_open_alerts": 1,
                "number_alerts_by_severity": {"critical": 1},
                "failing_alerts": {"critical": [open_critical_alert]},
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
