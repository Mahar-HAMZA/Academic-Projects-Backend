"""Global hotkey. Owner: Member C.
DUMMY version: only prints. Real version uses pynput.keyboard.GlobalHotKeys.
NOTE: the real callback runs on a background thread (GUI must use a Qt Signal)."""


def register_hotkey(combo: str, callback) -> None:
    print(f"[dummy] hotkey registered: {combo}")


def stop_hotkey() -> None:
    print("[dummy] hotkey stopped")
