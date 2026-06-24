"""Tests for the secret_scanning_slo check module."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from policy_methods_library.checks.secret_scanning_slo import get_secret_scanning_slo


# ---------------------------------------------------------------------------
# get_secret_scanning_slo – client-driven path
# ---------------------------------------------------------------------------


class TestGetSecretScanningSloWithClient:
    def test_error_when_client_is_none(self):
        """No client should return an error result."""
        result = get_secret_scanning_slo(client=None)

        assert result == {
            "result": "error",
            "message": "GitHubRestClient instance is required.",
            "details": {},
        }

    def test_error_when_client_raises_exception_during_org_verification(self):
        """An exception during organisation verification should return an error result."""
        client = MagicMock()
        client.owner = "my-org"
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "error"
        assert "verifying organisation" in result["message"]

    def test_error_when_organisation_data_is_not_dict(self):
        """An API response without organisation data should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = "not-a-dict"
        client.make_request.return_value = response

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "error"
        assert "organisation data" in result["message"]

    def test_error_when_organisation_type_is_not_organization(self):
        """An API response with a non-Organisation type should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        response = MagicMock()
        response.json.return_value = {"type": "User"}
        client.make_request.return_value = response

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "error"
        assert "not authenticated as an organisation" in result["message"]

    def test_error_when_fetching_alerts_raises_exception(self):
        """An exception while fetching alerts should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        # First call succeeds (org verification)
        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization"}

        # Second call fails (alerts fetch)
        def side_effect(*args, **kwargs):
            if "secret-scanning" in args[1]:
                raise RuntimeError("connection timeout")
            return org_response

        client.make_request.side_effect = side_effect

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "error"
        assert "fetching Secret Scanning alerts" in result["message"]

    def test_error_when_alert_response_is_not_list(self):
        """An API response that is not a list should return an error result."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization"}

        alerts_response = MagicMock()
        alerts_response.json.return_value = {"alerts": "not-a-list"}
        alerts_response.links = None

        def side_effect(*args, **kwargs):
            if "secret-scanning" in args[1]:
                return alerts_response
            return org_response

        client.make_request.side_effect = side_effect

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "error"
        assert "does not contain a list of Secret Scanning alerts" in result["message"]

    def test_passes_when_no_alerts_exceed_slo(self):
        """No alerts exceeding SLO should result in a pass."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization"}

        now = datetime.now(timezone.utc)
        recent_alert = {
            "created_at": (now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "html_url": "https://github.com/my-org/my-repo/security/secret-scanning/1",
            "repository": {"name": "my-repo"},
        }

        alerts_response = MagicMock()
        alerts_response.json.return_value = [recent_alert]
        alerts_response.links = None

        def side_effect(*args, **kwargs):
            if "secret-scanning" in args[1]:
                return alerts_response
            return org_response

        client.make_request.side_effect = side_effect

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "pass"
        assert (
            "No open Secret Scanning security alerts found exceeding SLO"
            in result["message"]
        )

    def test_fails_when_alerts_exceed_slo(self):
        """Alerts exceeding SLO should result in a fail."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization"}

        now = datetime.now(timezone.utc)
        old_alert_1 = {
            "created_at": (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "html_url": "https://github.com/my-org/repo1/security/secret-scanning/1",
            "repository": {"name": "repo1"},
        }
        old_alert_2 = {
            "created_at": (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "html_url": "https://github.com/my-org/repo2/security/secret-scanning/2",
            "repository": {"name": "repo2"},
        }

        alerts_response = MagicMock()
        alerts_response.json.return_value = [old_alert_1, old_alert_2]
        alerts_response.links = None

        def side_effect(*args, **kwargs):
            if "secret-scanning" in args[1]:
                return alerts_response
            return org_response

        client.make_request.side_effect = side_effect

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "fail"
        assert (
            "2 open Secret Scanning security alerts exceeding the policy-defined SLO"
            in result["message"]
        )
        assert result["details"]["failing_alerts"] == 2
        assert result["details"]["total_open_alerts"] == 2
        assert result["details"]["total_repositories_affected"] == 2

    def test_alert_with_missing_created_at_exceeds_slo(self):
        """An alert with missing created_at should be considered as exceeding SLO."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization"}

        alert_no_created_at = {
            "html_url": "https://github.com/my-org/repo1/security/secret-scanning/1",
            "repository": {"name": "repo1"},
        }

        alerts_response = MagicMock()
        alerts_response.json.return_value = [alert_no_created_at]
        alerts_response.links = None

        def side_effect(*args, **kwargs):
            if "secret-scanning" in args[1]:
                return alerts_response
            return org_response

        client.make_request.side_effect = side_effect

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "fail"
        assert (
            "1 open Secret Scanning security alerts exceeding the policy-defined SLO"
            in result["message"]
        )

    def test_alert_with_invalid_created_at_format_exceeds_slo(self):
        """An alert with invalid created_at format should be considered as exceeding SLO."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization"}

        alert_invalid_date = {
            "created_at": "invalid-date-format",
            "html_url": "https://github.com/my-org/repo1/security/secret-scanning/1",
            "repository": {"name": "repo1"},
        }

        alerts_response = MagicMock()
        alerts_response.json.return_value = [alert_invalid_date]
        alerts_response.links = None

        def side_effect(*args, **kwargs):
            if "secret-scanning" in args[1]:
                return alerts_response
            return org_response

        client.make_request.side_effect = side_effect

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "fail"
        assert "exceeding the policy-defined SLO" in result["message"]

    def test_handles_pagination_of_alerts(self):
        """Multiple pages of alerts should be aggregated correctly."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization"}

        now = datetime.now(timezone.utc)

        # First page of alerts
        first_page_alerts = [
            {
                "created_at": (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "html_url": "https://github.com/my-org/repo1/security/secret-scanning/1",
                "repository": {"name": "repo1"},
            }
        ]

        # Second page of alerts
        second_page_alerts = [
            {
                "created_at": (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "html_url": "https://github.com/my-org/repo2/security/secret-scanning/2",
                "repository": {"name": "repo2"},
            }
        ]

        first_response = MagicMock()
        first_response.json.return_value = first_page_alerts
        first_response.links = {
            "next": {
                "url": "https://api.github.com/orgs/my-org/secret-scanning/alerts?per_page=100&state=open&page=2"
            }
        }

        second_response = MagicMock()
        second_response.json.return_value = second_page_alerts
        second_response.links = None

        responses = [org_response, first_response, second_response]
        client.make_request.side_effect = responses

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "fail"
        assert result["details"]["total_open_alerts"] == 2
        assert result["details"]["failing_alerts"] == 2

    def test_repository_tracking_aggregates_alerts_correctly(self):
        """Multiple alerts from the same repository should be aggregated."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization"}

        now = datetime.now(timezone.utc)
        alert_1 = {
            "created_at": (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "html_url": "https://github.com/my-org/same-repo/security/secret-scanning/1",
            "repository": {"name": "same-repo"},
        }
        alert_2 = {
            "created_at": (now - timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "html_url": "https://github.com/my-org/same-repo/security/secret-scanning/2",
            "repository": {"name": "same-repo"},
        }

        alerts_response = MagicMock()
        alerts_response.json.return_value = [alert_1, alert_2]
        alerts_response.links = None

        def side_effect(*args, **kwargs):
            if "secret-scanning" in args[1]:
                return alerts_response
            return org_response

        client.make_request.side_effect = side_effect

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "fail"
        assert result["details"]["total_repositories_affected"] == 1
        assert result["details"]["total_open_alerts"] == 2
        assert result["details"]["failing_alerts"] == 2
        # Repository count includes one increment per alert
        assert result["details"]["repositories"]["my-org/same-repo"] == 2

    def test_handles_mixed_alerts_within_and_exceeding_slo(self):
        """A mix of alerts within and exceeding SLO should be handled correctly."""
        client = MagicMock()
        client.owner = "my-org"

        org_response = MagicMock()
        org_response.json.return_value = {"type": "Organization"}

        now = datetime.now(timezone.utc)
        recent_alert = {
            "created_at": (now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "html_url": "https://github.com/my-org/repo1/security/secret-scanning/1",
            "repository": {"name": "repo1"},
        }
        old_alert = {
            "created_at": (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "html_url": "https://github.com/my-org/repo2/security/secret-scanning/2",
            "repository": {"name": "repo2"},
        }

        alerts_response = MagicMock()
        alerts_response.json.return_value = [recent_alert, old_alert]
        alerts_response.links = None

        def side_effect(*args, **kwargs):
            if "secret-scanning" in args[1]:
                return alerts_response
            return org_response

        client.make_request.side_effect = side_effect

        result = get_secret_scanning_slo(client=client)

        assert result["result"] == "fail"
        assert result["details"]["total_open_alerts"] == 2
        assert result["details"]["failing_alerts"] == 1
        assert result["details"]["total_repositories_affected"] == 1
        # Only exceeding alerts are tracked by repository.
        assert result["details"]["repositories"]["my-org/repo2"] == 1
