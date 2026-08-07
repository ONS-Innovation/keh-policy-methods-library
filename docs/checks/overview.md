# Checks Module Overview

The checks module within the Policy Methods Library provides a collection of methods and utilities for checking compliance with various aspects of ONS' GitHub Usage Policy.
This module encapsulates the business logic for performing checks against GitHub repositories, such as checking for the presence of a CODEOWNERS file, serving as the backbone of the package.

Documentation on each component within the checks module can be found in the relevant documentation files within the `docs/checks` directory.

## Checks Module Contents

- `naming_convention.py`: Contains methods for checking that repository names adhere to ONS' naming conventions.
- `inactivity.py`: Contains methods for checking the inactivity of repositories (i.e. not updated in the last year).
- `readme.py`: Contains methods for checking whether a repository includes a `readme.md` file.
- `gitignore.py`: Contains methods for checking whether a repository includes a `.gitignore` file.
- `repository_access.py`: Contains methods for checking that repository access is managed through teams rather than individual users.
- `external_pull_request.py`: Contains methods for checking that open pull requests are authored by organisation members only.
- `security_scanning.py`: Contains methods for checking that Push Protection and Secret Scanning are enabled for public repositories.
- `dependabot.py`: Contains methods for checking that Dependabot automated security fixes are enabled for repositories.
- `dependabot_slo.py`: Contains methods for retrieving all open dependabot alerts, that breach SLO, across the whole organisation.
- `secret_scanning_slo.py`: Contains methods for retrieving all open secret scanning alerts, that breach SLO, across the whole organisation.
- `license.py`: Contains method for checking whether a repository includes a `LICENSE` file.
- `team_maintainer.py`: Contains method for checking that a GitHub team has at least one maintainer.
- `codeowners.py`: Contains method for checking whether a repository includes a `CODEOWNERS` file.
- `pirr.py`: Contains methods for checking that private and internal repositories include `pirr.md`
- `branch_protection.py`: Contains method for checking that a branch is protected.

## Importing the Checks Module

In Python, you can import the checks module as follows:

```python
from policy_methods_library.checks.<submodule> import <component>
```

For example, to import the method for checking repository naming conventions:

```python
from policy_methods_library.checks.naming_convention import check_naming_convention
```

## Check Structure

Checks within the checks module follow a consistent result structure. This includes:

- A primary, public function that serves as the entry point for a policy check. Most repository-level checks are named `check_<check_name>`, while organisation-level SLO aggregations use `get_<check_name>_slo`.
- Each check requires a GitHub Client instance and any necessary parameters for API-based operation.
- Some repository checks also support a data object input, allowing the check to run without API calls when the required metadata has already been retrieved.
- Checks will return a standardised result object containing the outcome of the check:

  ```json
  {
      "result": "pass" | "fail" | "error",
      "message": "A descriptive message providing details about the check result.",
      "details": {
          // Any additional details relevant to the check result, such as specific findings or data points.
      }
  }
  ```

  It is then up to the calling code to determine how to handle the result of the check, for example by logging the result, raising an exception, or taking some other action based on the outcome.

For further details on checks, including specific checks implemented and how to use them, please refer to the individual documentation files for each check within the `docs/checks` directory.

A guide is also available for developers on how to create new checks, which can be found in the `docs/dev_guides` directory.
