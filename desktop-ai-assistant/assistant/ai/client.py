
"""AI client. Owner: Member B."""

from assistant.ai.errors import (
    AssistantError,
    InvalidApiKeyError,
    NetworkError,
    NoApiKeyError,
    RateLimitError,
)
from assistant.ai.gemini_provider import ask_gemini
from google.genai import errors as genai_errors
from assistant.ai.ollama_provider import ask_ollama


def ask(prompt: str, image: bytes | None = None, mode: str = "general"):
    """Yield response chunks, falling back to Ollama if Gemini is unavailable."""
    yielded_chunk = False

    try:
        for chunk in ask_gemini(prompt, image=image, mode=mode):
            yielded_chunk = True
            yield chunk
        return
    except (NoApiKeyError, NetworkError, RateLimitError):
        if yielded_chunk:
            raise
    except InvalidApiKeyError:
        raise
    except AssistantError:
        raise
    except genai_errors.APIError:
        if yielded_chunk:
            raise

    yield from ask_ollama(prompt, image=image, mode=mode)