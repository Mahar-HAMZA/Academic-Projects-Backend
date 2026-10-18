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
