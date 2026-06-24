"""Tests for pagination utility function."""

from unittest.mock import create_autospec

from requests import Response

from policy_methods_library.github.clients import GitHubRestClient
from policy_methods_library.utils.pagination import get_paginated_list


class TestGetPaginatedList:
    def test_error_when_client_is_invalid(self):
        """Invalid client should return error payload."""
        result = get_paginated_list(
            github_client={},
            initial_endpoint="/orgs/my-org/test",
            list_name="items",
        )

        assert result == {"error": "GitHubRestClient instance is required."}

    def test_error_when_initial_endpoint_is_empty(self):
        """Empty endpoint should return error payload."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "my-org"

        result = get_paginated_list(
            github_client=client,
            initial_endpoint="",
            list_name="items",
        )

        assert result == {"error": "Initial endpoint is required."}

    def test_error_when_list_name_is_empty(self):
        """Empty list name should return error payload."""
        client = GitHubRestClient.__new__(GitHubRestClient)
        client.owner = "my-org"

        result = get_paginated_list(
            github_client=client,
            initial_endpoint="/orgs/my-org/test",
            list_name="",
        )

        assert result == {"error": "List name is required."}

    def test_success_returns_single_page_list(self):
        """Single page list response should be returned unchanged."""
        client = create_autospec(GitHubRestClient, instance=True)

        response = create_autospec(Response, instance=True)
        response.json.return_value = [{"id": 1}, {"id": 2}]
        response.links = {}

        client.make_request.return_value = response

        result = get_paginated_list(
            github_client=client,
            initial_endpoint="/orgs/my-org/test",
            list_name="items",
        )

        assert result == [{"id": 1}, {"id": 2}]

    def test_success_aggregates_paginated_list(self):
        """Multiple pages should be aggregated into a single list."""
        client = create_autospec(GitHubRestClient, instance=True)

        page1 = create_autospec(Response, instance=True)
        page1.json.return_value = [{"id": 1}]
        page1.links = {
            "next": {"url": "https://api.github.com/orgs/my-org/test?page=2"}
        }

        page2 = create_autospec(Response, instance=True)
        page2.json.return_value = [{"id": 2}]
        page2.links = {}

        client.make_request.side_effect = [page1, page2]

        result = get_paginated_list(
            github_client=client,
            initial_endpoint="/orgs/my-org/test",
            list_name="items",
        )

        assert result == [{"id": 1}, {"id": 2}]

    def test_error_when_payload_is_not_list(self):
        """Non-list payload should return a structured validation error."""
        client = create_autospec(GitHubRestClient, instance=True)

        response = create_autospec(Response, instance=True)
        response.json.return_value = {"message": "unexpected"}
        response.links = None

        client.make_request.return_value = response

        result = get_paginated_list(
            github_client=client,
            initial_endpoint="/orgs/my-org/test",
            list_name="items",
        )

        assert result == {
            "error": "API response does not contain a list of items.",
            "response": {"message": "unexpected"},
        }

    def test_error_when_request_raises_exception(self):
        """Request exceptions should be returned as error payload."""
        client = create_autospec(GitHubRestClient, instance=True)
        client.make_request.side_effect = RuntimeError("connection timeout")

        result = get_paginated_list(
            github_client=client,
            initial_endpoint="/orgs/my-org/test",
            list_name="items",
        )

        assert result == {"error": "connection timeout"}
