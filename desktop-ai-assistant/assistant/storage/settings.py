"""Settings and API key storage. Owner: Member B.
DUMMY version: keeps the key in memory only. Real version uses keyring."""

_api_key = ""


def get_api_key() -> str:
    return _api_key


def save_api_key(key: str) -> None:
    global _api_key
    _api_key = key
