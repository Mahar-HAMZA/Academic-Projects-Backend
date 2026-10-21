
"""Gemini API provider. Owner: Member B."""

from google import genai
from google.genai import types

from assistant.ai.errors import NoApiKeyError
from assistant.ai.prompts import PROMPTS
from assistant.storage.settings import get_api_key


MODEL_NAME = "gemini-3.5-flash-lite"


def ask_gemini(
    prompt: str,
    image: bytes | None = None,
    mode: str = "general",
):
    """Yield response text chunks from Gemini."""
    api_key = get_api_key()

    if not api_key:
        raise NoApiKeyError(
            "Gemini API key is not saved. Please configure your API key."
        )

    client = genai.Client(api_key=api_key)

    content = [prompt]
    if image:
        content.append(
            types.Part.from_bytes(data=image, mime_type="image/png")
        )

    stream = client.models.generate_content_stream(
        model=MODEL_NAME,
        contents=content,
        config=types.GenerateContentConfig(
            system_instruction=PROMPTS.get(
                mode, PROMPTS["general"]
            )
        ),
    )

    for chunk in stream:
        if chunk.text:
            yield chunk.text
