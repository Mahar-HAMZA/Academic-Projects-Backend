
"""Ollama local AI provider. Owner: Member B."""

import os

import ollama

from assistant.ai.errors import ModelError, NetworkError
from assistant.ai.prompts import PROMPTS


MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:1b")


def ask_ollama(
    prompt: str,
    image: bytes | None = None,
    mode: str = "general",
):
    """Yield response text chunks from the local Ollama model."""
    if image:
        raise ModelError(
            "The configured Ollama provider does not support image input "
            "in this implementation. Use Gemini for screenshot questions."
        )

    try:
        stream = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": PROMPTS.get(mode, PROMPTS["general"]),
                },
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )

        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content

    except ollama.ResponseError as exc:
        raise ModelError(
            f"Ollama model error ({MODEL_NAME}): {exc}"
        ) from exc
    except (ollama.RequestError, ConnectionError, OSError) as exc:
        raise NetworkError(
            "Ollama is unavailable. Check that Ollama is running."
        ) from exc
