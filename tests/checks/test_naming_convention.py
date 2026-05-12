"""Tests for the naming_convention check module."""

from policy_methods_library.checks.naming_convention import check_naming_convention


# ---------------------------------------------------------------------------
# check_naming_convention
# ---------------------------------------------------------------------------


class TestCheckNamingConvention:
    def test_fails_when_repository_name_is_empty(self):
        """An empty repository name should fail with a clear message."""
        result = check_naming_convention("")

        assert result == {
            "result": "fail",
            "message": "Repository name cannot be empty.",
            "details": {"repository_name": ""},
        }

    def test_fails_when_repo_name_has_uppercase(self):
        """Repository names containing uppercase letters should fail."""
        result = check_naming_convention("My-repo")

        assert result == {
            "result": "fail",
            "message": "Repository name should be in lowercase.",
            "details": {"repository_name": "My-repo"},
        }

    def test_fails_when_repo_name_has_spaces(self):
        """Repository names containing spaces should fail."""
        result = check_naming_convention("my repo")

        assert result == {
            "result": "fail",
            "message": "Repository name should not contain spaces.",
            "details": {"repository_name": "my repo"},
        }

    def test_fails_when_repo_name_has_special_characters(self):
        """Repository names containing special characters should fail."""
        result = check_naming_convention("my_repo!")

        assert result == {
            "result": "fail",
            "message": "Repository name should only contain letters, numbers, hyphens, and underscores.",
            "details": {"repository_name": "my_repo!"},
        }

    def test_passes_for_valid_repo_name(self):
        """A lowercase repository name with no spaces/special characters should pass."""
        result = check_naming_convention("my-repo_123")

        assert result == {
            "result": "pass",
            "message": "Repository name follows GitHub Usage Policy Naming Conventions.",
            "details": {"repository_name": "my-repo_123"},
        }
