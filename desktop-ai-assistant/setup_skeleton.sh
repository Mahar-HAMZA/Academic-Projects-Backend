#!/usr/bin/env bash
# Desktop AI Assistant - project skeleton creator
# Run this INSIDE the desktop-ai-assistant folder:
#     cd ~/Academic-Projects/desktop-ai-assistant
#     bash setup_skeleton.sh
# Existing files are never overwritten (they are skipped).

set -e

# mk <path>  : create the file from stdin, only if it does not exist yet
mk() {
  if [ -e "$1" ]; then
    echo "skip    (already exists): $1"
    cat > /dev/null
  else
    mkdir -p "$(dirname "$1")"
    cat > "$1"
    echo "created: $1"
  fi
}

# ---------------------------------------------------------------
# Folders that only need a placeholder (git ignores empty folders)
# ---------------------------------------------------------------
for d in assets installer docs; do
  mkdir -p "$d"
  [ -e "$d/.gitkeep" ] || touch "$d/.gitkeep"
done

# ---------------------------------------------------------------
# Package markers
# ---------------------------------------------------------------
for p in assistant assistant/ui assistant/ai assistant/storage assistant/system tests; do
  mkdir -p "$p"
  [ -e "$p/__init__.py" ] || { touch "$p/__init__.py"; echo "created: $p/__init__.py"; }
done

# ---------------------------------------------------------------
# main.py (only if you do not already have one)
# ---------------------------------------------------------------
mk main.py <<'EOF'
"""Entry point of the Desktop AI Assistant.
Owner: Member A. Replaced with the real app in Week 1."""


def main():
    print("Desktop AI Assistant - skeleton. Real app coming soon.")


if __name__ == "__main__":
    main()
EOF

# ---------------------------------------------------------------
# assistant/config.py  (Member A)
# ---------------------------------------------------------------
mk assistant/config.py <<'EOF'
"""Central app settings and defaults. Owner: Member A."""

APP_NAME = "DesktopAIAssistant"
DEFAULT_HOTKEY = "ctrl+shift+space"
DEFAULT_MODEL = "gemini-2.5-flash"   # change here if the model name changes
DEFAULT_PROVIDER = "gemini"          # "gemini" or "ollama"
OLLAMA_MODEL = "llama3.2"
CHAT_WINDOW_SIZE = (360, 460)
MEMORY_MESSAGES = 10                 # how many past messages are sent to the AI
EOF

# ---------------------------------------------------------------
# Member B: assistant/ai/  (DUMMY versions, replace with real code)
# ---------------------------------------------------------------
mk assistant/ai/client.py <<'EOF'
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
EOF

mk assistant/ai/prompts.py <<'EOF'
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
EOF

mk assistant/ai/errors.py <<'EOF'
"""Custom exceptions so the GUI can show friendly messages. Owner: Member B.

NoApiKeyError       - no API key saved yet
InvalidApiKeyError  - key rejected by the server
RateLimitError      - too many requests (free tier limit)
NetworkError        - no internet / timeout / Ollama not running
ModelError          - model not found or other model problem
"""


class AssistantError(Exception):
    """Base class for all assistant errors."""


class NoApiKeyError(AssistantError):
    pass


class InvalidApiKeyError(AssistantError):
    pass


class RateLimitError(AssistantError):
    pass


class NetworkError(AssistantError):
    pass


class ModelError(AssistantError):
    pass
EOF

# ---------------------------------------------------------------
# Member B: assistant/storage/  (DUMMY versions)
# ---------------------------------------------------------------
mk assistant/storage/settings.py <<'EOF'
"""Settings and API key storage. Owner: Member B.
DUMMY version: keeps the key in memory only. Real version uses keyring."""

_api_key = ""


def get_api_key() -> str:
    return _api_key


def save_api_key(key: str) -> None:
    global _api_key
    _api_key = key
EOF

mk assistant/storage/history.py <<'EOF'
"""Chat history. Owner: Member B.
DUMMY version: stores everything in memory. Real version uses SQLite."""

_chats: dict[int, dict] = {}
_next_id = 1


def create_chat(title: str = "New chat") -> int:
    global _next_id
    chat_id = _next_id
    _next_id += 1
    _chats[chat_id] = {"title": title, "messages": []}
    return chat_id


def add_message(chat_id: int, role: str, content: str) -> None:
    _chats[chat_id]["messages"].append({"role": role, "content": content})


def get_messages(chat_id: int) -> list[dict]:
    return list(_chats[chat_id]["messages"])


def list_chats() -> list[dict]:
    return [{"id": i, "title": c["title"], "created_at": ""} for i, c in _chats.items()]


def delete_chat(chat_id: int) -> None:
    _chats.pop(chat_id, None)
EOF

# ---------------------------------------------------------------
# Member C: assistant/system/  (DUMMY versions)
# ---------------------------------------------------------------
mk assistant/system/capture.py <<'EOF'
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
EOF

mk assistant/system/hotkey.py <<'EOF'
"""Global hotkey. Owner: Member C.
DUMMY version: only prints. Real version uses pynput.keyboard.GlobalHotKeys.
NOTE: the real callback runs on a background thread (GUI must use a Qt Signal)."""


def register_hotkey(combo: str, callback) -> None:
    print(f"[dummy] hotkey registered: {combo}")


def stop_hotkey() -> None:
    print("[dummy] hotkey stopped")
EOF

mk assistant/system/autostart.py <<'EOF'
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
EOF

# ---------------------------------------------------------------
# GUI placeholder (Member A)
# ---------------------------------------------------------------
mk assistant/ui/README.md <<'EOF'
# assistant/ui (Member A)
Planned files: bubble.py, chat_window.py, tray.py, settings_dialog.py,
history_panel.py, markdown_view.py, themes.py, workers.py
See docs/MEMBER_A_GUI.md
EOF

# ---------------------------------------------------------------
# Tests (Member C)
# ---------------------------------------------------------------
mk tests/test_smoke.py <<'EOF'
"""Smoke test: the dummy interfaces exist and have the agreed shape."""
from assistant.ai.client import ask
from assistant.ai.prompts import pick_mode
from assistant.storage import history
from assistant.system.capture import get_active_app


def test_ask_yields_text():
    chunks = list(ask("hello"))
    assert chunks and all(isinstance(c, str) for c in chunks)


def test_pick_mode():
    assert pick_mode("vscode") == "coding"
    assert pick_mode("browser") == "lecture"
    assert pick_mode("other") == "general"


def test_history_roundtrip():
    chat_id = history.create_chat("t")
    history.add_message(chat_id, "user", "hi")
    assert history.get_messages(chat_id) == [{"role": "user", "content": "hi"}]


def test_active_app_value():
    assert get_active_app() in {"vscode", "browser", "other"}
EOF

# ---------------------------------------------------------------
# GitHub PR template (Member C)
# ---------------------------------------------------------------
mk .github/pull_request_template.md <<'EOF'
## What changed?
<!-- Short description -->

## Related issue
Closes #

## Checklist
- [ ] Code runs without crashing
- [ ] Tested manually (how?)
- [ ] No API keys / passwords / .env committed
- [ ] Only files in my own folders were changed (or the owner was informed)
- [ ] README/docs updated if users will notice the change
EOF

echo
echo "Done. Next: git add . && git commit -m \"chore: add project skeleton\" && git push"
