"""Selected text, screenshot, active app. Owner: Member C."""
import time

import pyperclip


def get_selected_text() -> str:
    """Return the text currently selected in any app ('' if nothing is selected).

    Trick: put a marker on the clipboard, simulate Ctrl+C, and see if it changed.
    The user's original clipboard is always restored."""
    from pynput.keyboard import Controller, Key

    kb = Controller()
    try:
        original = pyperclip.paste()
    except Exception:
        original = ""

    marker = f"__DAI_MARKER_{time.time_ns()}__"
    text = marker
    try:
        pyperclip.copy(marker)
        # Hotkey keys may still be held down; release them so we send a clean Ctrl+C
        for k in (Key.shift, Key.alt):
            kb.release(k)
        time.sleep(0.15)
        with kb.pressed(Key.ctrl):
            kb.press("c")
            kb.release("c")
        time.sleep(0.2)
        text = pyperclip.paste()
    except Exception:
        text = marker
    finally:
        try:
            pyperclip.copy(original)
        except Exception:
            pass

    return "" if text == marker else text.strip()


# ---- Dummy versions (will be replaced in later tasks) ----
def take_screenshot() -> bytes:
    """Returns PNG image bytes."""
    return b""


def get_active_app() -> str:
    """Returns 'vscode', 'browser' or 'other'."""
    return "other"