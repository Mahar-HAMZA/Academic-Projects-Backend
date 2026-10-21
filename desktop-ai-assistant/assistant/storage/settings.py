
"""Settings and secure API key storage. Owner: Member B."""

import keyring

_SERVICE_NAME = "DesktopAIAssistant"
_USERNAME = "gemini_api_key"


def get_api_key() -> str:
    """Return the saved Gemini API key, or an empty string if absent."""
    return keyring.get_password(_SERVICE_NAME, _USERNAME) or ""


def save_api_key(key: str) -> None:
    """Save the Gemini API key in the operating system's credential store."""
    key = key.strip()
    if not key:
        raise ValueError("API key cannot be empty.")
    keyring.set_password(_SERVICE_NAME, _USERNAME, key)
