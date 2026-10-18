"""Start with Windows. Owner: Member C.
DUMMY version. Real version edits HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run."""

_enabled = False


def enable_autostart() -> None:
    global _enabled
    _enabled = True


def disable_autostart() -> None:
    global _enabled
    _enabled = False


def is_autostart_enabled() -> bool:
    return _enabled
