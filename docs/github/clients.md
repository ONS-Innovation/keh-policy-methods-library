# Clients

The `clients` module provides client classes for interacting with the GitHub API when making requests.
Currently, this module includes a client for the GitHub REST API, which can be used to make authenticated requests to the GitHub REST API endpoints.

Using these classes can simplify the process of making requests to the GitHub API, as they handle the authentication process and handle lots of the boilerplate code
required to make requests to the GitHub API (i.e. setting up the header).

## Benefits of Using the Clients Module

Using the REST API Client as an example, the benefits of using the client defined in this module include:

- **Simplified Authentication:** The client handles the authentication process for you, allowing you to easily authenticate requests to the GitHub API using a GitHub App's credentials.
- **Consistent Interface:** The client provides a consistent interface for making requests to the GitHub API, abstracting away the details of how requests are made and allowing you to focus on the specific API endpoints you want to interact with.
- **Reusability:** By using the client defined in this module, you can reuse the same client across different parts of your application or across different applications, ensuring consistency in how you interact with the GitHub API and reducing the amount of duplicate code you need to write when making requests to the GitHub API.

To provide a code example:

```python
## Without the module:

... Access Token Logic Here ...

import requests

headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/vnd.github.v3+json"
}

response = requests.get("https://api.github.com/orgs/your_github_organisation/repos", headers=headers)
response.raise_for_status()

repos = response.json()
print(repos)

## With the module:

from policy_methods_library.github.clients import GitHubRestClient

client = GitHubRestClient(app_id, private_key, github_organisation) # Auth logic encapsulated within the client

response = client.make_request("GET", "/orgs/your_github_organisation/repos")

repos = response.json()
print(repos)
```

This highlights the amount of boilerplate code that can be removed by using the client defined in this module, as well as the simplified authentication process and consistent interface for making requests to the GitHub API that the client provides.

## Client Module Contents

### `GitHubRestClient`

::: src.policy_methods_library.github.clients.GitHubRestClient
