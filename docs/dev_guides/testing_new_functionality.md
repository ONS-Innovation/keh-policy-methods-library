# Testing New Functionality

## Setup

When developing/reviewing new functionality for the package, you can use the `tests/manual_testing.py` file for manual testing of the package during development. This file has a GitHub Client instance already setup which can be used to test the checks in the `policy_methods_library`.

To use the latest version of the package in the `manual_testing.py` file, you can install the package into your virtual environment:

```bash
pip install .
```

**Note:** This should be done from the root directory of the repository, and you should have your virtual environment activated.

Whenever you make changes to the package, you will need to reinstall it for the changes to be reflected in the `manual_testing.py` file.

## Example: Naming Convention Check

As an example, if you were developing a new check for repository naming conventions, you could implement the check in the `policy_methods_library/checks/naming_convention.py` file and then test it using the `manual_testing.py` file.

In the `manual_testing.py` file, you would import the new check and then call it, following the documentation for the check to understand what parameters it requires and how to interpret the results.

In manual_testing.py:

```python
<... Existing Boilerplate Code ...>

from policy_methods_library.checks.naming_convention import check_naming_convention

response = check_naming_convention(repository_name="example-repository-name")
pprint(response)
```

Something like the above can be used to test the functionality of a new check for repository naming conventions. You would replace the `repository_name` parameter with the name of a repository you want to test against, and then interpret the response according to the documentation for the `check_naming_convention` method.

You can then run the `manual_testing.py` file to see the results of the check and verify that it is working as expected.

```bash
python3 tests/manual_testing.py
```
