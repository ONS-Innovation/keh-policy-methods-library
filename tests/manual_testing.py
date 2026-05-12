"""
This file is for manual testing of the package. This is useful for testing things during development.
A GitHub Client instance is already setup which can be used to test the checks in the policy_methods_library.

To run this file, you will need to set the following environment variables:
- GITHUB_CLIENT_ID: The client ID of your GitHub App.
- GITHUB_PRIVATE_KEY: The private key of your GitHub App. This should be the contents of the private key file, not the file path.
- GITHUB_ORGANISATION: The name of your GitHub organisation.

Note: Changes to this file should **not** be committed to the repository.
"""

from policy_methods_library.github.clients import GitHubRestClient

from os import getenv
from pprint import pprint  # noqa: F401 - Unused import, but useful to keep for testing purposes.

# Test Access Token Generation

client_id = getenv("GITHUB_CLIENT_ID")
private_key = getenv("GITHUB_PRIVATE_KEY")
organisation = getenv("GITHUB_ORGANISATION")

client = GitHubRestClient(
    owner=organisation,
    app_id=client_id,
    private_key=private_key,
)

# Space to test any methods during development. Example:

# response = client.make_request("GET", f"/orgs/{client.owner}/repos")
# pprint(response.json())

## Reminder: Do not commit any changes to this file, as it is for manual testing purposes only.
