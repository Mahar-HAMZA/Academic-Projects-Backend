"""Custom exceptions so the GUI can show friendly messages. Owner: Member B.

NoApiKeyError       - no API key saved yet
InvalidApiKeyError  - key rejected by the server
RateLimitError      - too many requests (free tier limit)
NetworkError        - no internet / timeout / Ollama not running
ModelError          - model not found or other model problem
"""


class AssistantError(Exception):
    """Base class for all assistant errors."""


class NoApiKeyError(AssistantError):
    pass


class InvalidApiKeyError(AssistantError):
    pass


class RateLimitError(AssistantError):
    pass


class NetworkError(AssistantError):
    pass


class ModelError(AssistantError):
    pass
