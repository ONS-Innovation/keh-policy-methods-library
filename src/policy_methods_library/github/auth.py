"""
This module contains functions for authenticating with the GitHub API.
The main function is `get_access_token`, which generates a JWT for the GitHub App, retrieves the installation ID for the specified organisation, and then generates an access token that can be used to authenticate API requests.
"""

import jwt
import time
import requests


def _generate_jwt(app_id: str, private_key: str) -> str:
    """Generates a JSON Web Token (JWT) for authenticating with the GitHub API as a GitHub App.

    Args:
        app_id (str): The GitHub App's identifier.
        private_key (str): The GitHub App's private key in PEM format.

    Returns:
        str: A JWT that can be used to generate an access token.

    Raises:
        ValueError: If the app_id or private_key is not provided, or if the private key is in an invalid format.
    """

    # Validate params
    if not app_id:
        raise ValueError("GitHub App ID is required.")
    if not private_key:
        raise ValueError("GitHub App private key is required.")

    # Setup JWT payload with issued at and expiration times
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),  # JWT expires after 10 minutes
        "iss": app_id,
    }

    # Create a signing key from the private key
    try:
        signing_key = jwt.jwk_from_pem(private_key.encode())
    except jwt.exceptions.UnsupportedKeyTypeError as e:
        raise ValueError(
            "Invalid private key format. Ensure the key is in PEM format."
        ) from e

    # Generate and return the JWT (RS256 algorithm)
    jwt_instance = jwt.JWT()
    return jwt_instance.encode(payload, signing_key, alg="RS256")


def _get_installation_id(organisation: str, jwt: str) -> int:
    """Retrieves the installation ID for the GitHub App in the specified organisation.

    Args:
        organisation (str): The name of the GitHub organisation.
        jwt (str): The JWT generated for authentication.

    Returns:
        int: The installation ID for the GitHub App in the organisation.

    Raises:
        ValueError: If no installations are found for the specified organisation.
    """

    # Validate params
    if not organisation:
        raise ValueError("GitHub organisation name is required.")
    if not jwt:
        raise ValueError("JWT is required to retrieve installation ID.")

    # Prepare headers for the API request
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Make API request to get the installation for the organisation
    response = requests.get(
        f"https://api.github.com/orgs/{organisation}/installation", headers=headers
    )
    response.raise_for_status()
    installation = response.json()

    # Check that an installation was found and return its ID
    installation_id = installation.get("id")
    if installation_id is None:
        raise ValueError(f"No installations found for organisation '{organisation}'")
    return installation_id


def get_access_token(app_id: str, private_key: str, organisation: str) -> str:
    """Generates an access token for the GitHub App to authenticate with the GitHub API.

    Args:
        app_id (str): The GitHub App's identifier.
        private_key (str): The GitHub App's private key in PEM format.
        organisation (str): The name of the GitHub organisation.

    Returns:
        str: An access token that can be used to authenticate API requests.

    Raises:
        ValueError: If any of the required parameters are missing or if there are issues with generating the JWT or retrieving the installation ID.
    """

    # Validate params
    if not app_id:
        raise ValueError("GitHub App ID is required.")
    if not private_key:
        raise ValueError("GitHub App private key is required.")
    if not organisation:
        raise ValueError("GitHub organisation name is required.")

    # Generate a JWT and retrieve the installation ID for the organisation
    jwt = _generate_jwt(app_id, private_key)
    installation_id = _get_installation_id(organisation, jwt)

    # Prepare headers for the API request to generate an access token
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Make API request to generate an access token for the installation and return the token
    response = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers=headers,
    )
    response.raise_for_status()
    return response.json().get("token")
