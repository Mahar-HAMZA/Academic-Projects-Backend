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
