# GitHub Module Overview

The GitHub module within the Policy Methods Library provides a collection of methods and utilities for interacting with the GitHub API.
Currently, this module includes methods for authenticating with the GitHub API, as well as clients for making requests to GitHub's APIs (currently REST only).

Documentation on each component within the GitHub module can be found in the relevant documentation files within the `docs/github` directory.

## GitHub Module Contents

- `auth.py`: Contains methods for authenticating with the GitHub API, including methods for generating authentication tokens.
- `clients.py`: Contains clients for making requests to the GitHub API. Currently includes a client for the REST API. This client supports authentication via the methods defined in `auth.py` or via personal access tokens (PATs).

## Importing the GitHub Module

In Python, you can import the GitHub module as follows:

```python
from policy_methods_library.github.<submodule> import <component>
```

For example, to import the REST API client:

```python
from policy_methods_library.github.clients import GitHubRestClient
```
