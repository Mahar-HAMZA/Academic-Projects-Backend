"""System prompts per mode. Owner: Member B."""

PROMPTS = {
    "general": "You are a helpful assistant in a small overlay. Keep answers short and clear.",
    "coding": "You are a coding mentor. Explain errors simply and show short fixes in code blocks.",
    "lecture": "You are a patient tutor. Explain terms in simple words with one example.",
    "screen": "The image is the user's screen. Explain what is shown and what the user likely needs.",
}


def pick_mode(app_name: str) -> str:
    """Map the active app ('vscode' | 'browser' | 'other') to a prompt mode."""
    return {"vscode": "coding", "browser": "lecture"}.get(app_name, "general")
