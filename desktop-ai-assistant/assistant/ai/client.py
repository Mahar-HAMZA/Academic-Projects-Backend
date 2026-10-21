
"""AI client. Owner: Member B."""

from assistant.ai.gemini_provider import ask_gemini


def ask(prompt: str, image: bytes | None = None, mode: str = "general"):
    """Yield response text chunks as they arrive."""
    yield from ask_gemini(prompt, image=image, mode=mode)
