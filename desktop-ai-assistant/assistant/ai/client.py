"""AI client. Owner: Member B.
DUMMY version: yields fake text so the GUI can be built and tested.
Keep this function signature unchanged. Replace the body with Gemini/Ollama."""
import time


def ask(prompt: str, image: bytes | None = None, mode: str = "general"):
    """Generator that yields response text chunks as they arrive."""
    answer = f"[dummy {mode} answer] You asked: {prompt}"
    for word in answer.split():
        yield word + " "
        time.sleep(0.05)
