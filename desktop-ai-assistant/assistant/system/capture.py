"""Selected text, screenshot, active app. Owner: Member C.
DUMMY version: returns fake data. Real version uses pynput, mss, pywin32."""


def get_selected_text() -> str:
    return "dummy selected text"


def take_screenshot() -> bytes:
    """Returns PNG image bytes."""
    return b""


def get_active_app() -> str:
    """Returns 'vscode', 'browser' or 'other'."""
    return "other"
