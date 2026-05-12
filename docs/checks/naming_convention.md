# Naming Convention

The naming convention check ensures that GitHub repositories adhere to ONS' naming standards, defined within the GitHub Usage Policy.

## GitHub Usage Policy Origin

Inspired by the GitHub Usage Policy, clause 5.3.2, in summary:

- Avoid Special Characters
- Avoid Spaces (use hyphens or underscores instead)
- Use Lowercase Letters

## Check Criteria

- The repository name must be in lowercase.
- The repository name must not contain spaces (hyphens or underscores are acceptable).
- The repository name must not contain special characters (only letters, numbers, hyphens, and underscores are allowed).

## Reference

::: src.policy_methods_library.checks.naming_convention.check_naming_convention

## Usage Example

```python
from policy_methods_library.checks.naming_convention import check_naming_convention

repository_name = "example-repository"

response = check_naming_convention(repository_name)

result = response.get("result")
message = response.get("message")

match result:
    case "pass":
        print(f"Check Passed: {message}")
    case "fail":
        print(f"Check Failed: {message}")
    case "error":
        print(f"Check Error: {message}")
    case _:
        print("Unexpected result returned.")
```

## GitHub Integration Used

This check does not directly integrate with GitHub APIs.
