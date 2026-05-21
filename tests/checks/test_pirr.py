"""Tests for PIRR check module."""

from policy_methods_library.checks import pirr_checks


# ---------------------------------------------------------------------------
# pirr_checks
# ---------------------------------------------------------------------------


class TestCheckPIRR:
    def test_check_repo_details_is_empty(self):
        """Test that the check fails when the repository details are empty."""
        result = pirr_checks.check_repo_visibility({}, {})
        assert result["result"] == "fail"
        assert result["message"] == "Repository details cannot be empty."
        assert result["details"] == {"repo_details": {}}

    def test_check_repo_contents_is_empty(self):
        """Test that the check fails when the repository contents are empty."""
        result = pirr_checks.check_repo_visibility(
            {"private": True, "visibility": "internal"}, {}
        )
        assert result["result"] == "fail"
        assert result["message"] == "Repository contents cannot be empty."
        assert result["details"] == {"repo_contents": {}}

    def test_check_repo_details_missing_keys(self):
        """Test that the check fails when the repository details are missing required keys."""
        repo_details = {"private": True}
        repo_contents = {"entires": []}
        result = pirr_checks.check_repo_visibility(repo_details, repo_contents)
        assert result["result"] == "fail"
        assert (
            result["message"]
            == "Repository details must include 'private' and 'visibility' keys."
        )
        assert result["details"] == {"repo_details": repo_details}

    def test_check_repo_contents_missing_entries_key(self):
        """Test that the check fails when the repository contents are missing the 'entries' key."""
        result = pirr_checks.check_repo_visibility(
            {"private": False, "visibility": "public"}, {"non_entries": []}
        )
        assert result["result"] == "fail"
        assert result["message"] == "Repository contents must include 'entries' key."
        assert result["details"] == {"repo_contents": {"non_entries": []}}

    def test_check_repo_is_public(self):
        """Test that the check passes when the repository is public."""
        result = pirr_checks.check_repo_visibility(
            {"private": False, "visibility": "public"}, {"entries": []}
        )
        assert result["result"] == "pass"
        assert result["message"] == "Repository is public."
        assert result["details"] == {
            "repo_details": {"private": False, "visibility": "public"}
        }

    def test_check_repo_is_private_with_pirr_file(self):
        """Test that the check passes when the repository is private but contains a PIRR.md file."""
        result = pirr_checks.check_repo_visibility(
            {"private": True, "visibility": "private"},
            {"entries": [{"name": "PIRR.md"}]},
        )
        assert result["result"] == "pass"
        assert result["message"] == "Repository is private but contains a PIRR.md file."
        assert result["details"] == {
            "repo_details": {"private": True, "visibility": "private"},
            "repo_contents": {"entries": [{"name": "PIRR.md"}]},
        }

    def test_check_repo_is_private_without_pirr_file(self):
        """Test that the check fails when the repository is private and does not contain a PIRR.md file."""
        result = pirr_checks.check_repo_visibility(
            {"private": True, "visibility": "private"},
            {"entries": [{"name": "README.md"}]},
        )
        assert result["result"] == "fail"
        assert (
            result["message"]
            == "Repository is private and does not contain a PIRR.md file."
        )
        assert result["details"] == {
            "repo_details": {"private": True, "visibility": "private"},
            "repo_contents": {"entries": [{"name": "README.md"}]},
        }
