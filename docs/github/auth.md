# Auth

The `auth` module provides functions for handling authentication to the GitHub API when making requests.
Currently, this module only supports authentication as an installation via GitHub Apps, exchanging a GitHub App's private key for an installation access token that can be used to authenticate requests to the GitHub API.

GitHub provide documentation on this process here: [Authenticating with GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app).

## Usage

Within the Policy Methods Library, the authentication methods defined in this module are used by the [Clients](./clients.md) module.
These methods often appear when initialising clients that require authentication, such as the REST API client.
GitHub App credentials can be passed to these clients, which will then use the methods defined in this module to authenticate requests to the GitHub API.

In addition to this, the methods defined in this module can also be used directly should you with to get an installation access token for a GitHub App installation and use it yourself.
You can import the methods defined in this module for isolated use as follows:

```python
from policy_methods_library.github.auth import get_access_token

# Example usage of the get_access_token method

## Get Variables from Environment (In practice, these would likely be stored in a secrets manager and accessed directly from there).

app_id = os.getenv("GITHUB_APP_ID")
private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")
github_organisation = "your_github_organisation"

## Exchange GitHub App credentials for an installation access token.

access_token = get_access_token(app_id, private_key, github_organisation)

print(access_token)  # This is the token you can use to authenticate requests to the GitHub API.
```

## GitHub App Setup

To use the authentication methods defined in this module, you will need to set up a GitHub App and install it on the relevant repositories or organisations that you want to interact with via the GitHub API.

With this GitHub App created and installed, you will need to make note of the following details, which will be required to authenticate via the methods defined in this module:

- `APP_ID`: The ID of your GitHub App.
- `PRIVATE_KEY`: The private key of your GitHub App, which can be generated in the GitHub App settings. This should be stored securely, such as in a secrets manager or environment variable (This will be a `.pem` file).

A list of permissions required for the GitHub App can be found in the [GitHub App Permissions](../github-app-permissions.md) documentation.

## Auth Module Contents

### `get_access_token()`

::: src.policy_methods_library.github.auth.get_access_token
