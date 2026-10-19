"""Global hotkey. Owner: Member C.
The callback runs on a BACKGROUND thread (the GUI must use a Qt Signal)."""

_listener = None


def to_pynput_combo(combo: str) -> str:
    """'ctrl+space' -> '<ctrl>+<space>'"""
    parts = [p.strip().lower() for p in combo.split("+") if p.strip()]
    return "+".join(f"<{p}>" if len(p) > 1 else p for p in parts)


def register_hotkey(combo: str, callback) -> None:
    """Start listening for the hotkey. Calling it again replaces the old hotkey."""
    global _listener
    from pynput import keyboard          # imported here so tests work without a display

    stop_hotkey()
    _listener = keyboard.GlobalHotKeys({to_pynput_combo(combo): callback})
    _listener.start()                    # runs in its own thread


def stop_hotkey() -> None:
    global _listener
    if _listener is not None:
        _listener.stop()
        _listener = None