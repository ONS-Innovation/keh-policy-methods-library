"""Tests for PIRR check module."""

from policy_methods_library.checks import pirr_checks


# ---------------------------------------------------------------------------
# pirr_checks
# ---------------------------------------------------------------------------


class TestCheckPIRR:
    def test_fails_when_repository_name_is_empty(self):
        """An empty repository name should fail with a clear message."""
        result = pirr_checks("")

        assert result == {
            "result": "fail",
            "message": "Repository name cannot be empty.",
            "details": {"repository_name": ""},
        }

  