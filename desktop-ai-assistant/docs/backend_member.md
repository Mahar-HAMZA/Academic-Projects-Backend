# Member B: Backend (AI and Data)

**Goal:** Build the "brain" of the assistant: talk to Gemini (and later Ollama), stream answers, remember the conversation, store history, and keep the API key safe.

**Why this part matters:** This is the real AI part of the project. When the teacher of the AI subject asks "what AI did you use and how?", your work answers it: prompt engineering, context awareness, multimodal input (screenshots), conversation memory, local vs cloud models.

**Tools you will use:** `google-genai`, `keyring`, `ollama`, `sqlite3` (built-in), `platformdirs`, `pytest`.

**Folders you own:** `assistant/ai/`, `assistant/storage/`.

---

## Suggested File Structure

```
assistant/ai/
├── client.py            # ask(): the single function the GUI calls
├── gemini_provider.py   # Gemini implementation
├── ollama_provider.py   # local model implementation
├── prompts.py           # system prompts per mode
└── errors.py            # custom exceptions
assistant/storage/
├── settings.py          # get_api_key / save_api_key / app settings
├── database.py          # SQLite connection + table creation
└── history.py           # chats and messages
```

---

## Week 1 (19–25 Oct): Foundation

### Task B1: Dummy `ask()` on Day 1
**What:** Push a fake `ask()` immediately so Member A can build the UI.
**How:** A generator that yields a few words with small sleeps (same as in A's guide). Replace later with the real one.
**Why:** The whole team depends on this function's *shape*, not its content.

### Task B2: Gemini connection (non-streaming first)
**How:**
```python
from google import genai
client = genai.Client(api_key=get_api_key())
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain recursion in 2 lines",
)
print(response.text)
```
- Keep the model name in `config` (or settings) instead of hardcoding it everywhere. Model names change over time; the user must be able to change it.
- Test first in a plain Python file (no GUI). Get it working there, then plug it into `ask()`.

### Task B3: Secure API key storage
**How:**
```python
import keyring, os
SERVICE = "DesktopAIAssistant"

def save_api_key(key: str) -> None:
    keyring.set_password(SERVICE, "gemini_api_key", key)

def get_api_key() -> str:
    return keyring.get_password(SERVICE, "gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
```
**Why `keyring`:** it uses Windows Credential Manager, so the key is not saved in a readable text file inside the project (and cannot be accidentally pushed to GitHub).
Other app settings (model, theme, hotkey) can go in a small JSON file inside `platformdirs.user_config_dir("DesktopAIAssistant")`.

### Task B4: Clear errors
**What:** Define custom exceptions in `errors.py` so the GUI can show friendly messages:
`NoApiKeyError`, `InvalidApiKeyError`, `RateLimitError`, `NetworkError`, `ModelError`.
**How:** Wrap the Gemini call in `try/except`, inspect the exception (message/status code, e.g. 401/403 invalid key, 429 rate limit, connection errors) and raise your own. Every exception gets a short, human-readable message.

**Milestone 1 check (25 Oct):** `ask()` returns a real Gemini answer, with proper errors when the key is missing or wrong.

---

## Week 2 (26 Oct – 1 Nov): Core Features

### Task B5: Streaming
**How:**
```python
for chunk in client.models.generate_content_stream(model=MODEL, contents=contents):
    if chunk.text:
        yield chunk.text
```
Keep `ask()` as a *generator* so the GUI gets text piece by piece.

### Task B6: Conversation memory
**What:** The assistant should remember the last few messages in the chat.
**How:** Keep a list of messages, send only the last N (about 10) to the model:
```python
contents = [
    {"role": "user",  "parts": [{"text": "What is a stack?"}]},
    {"role": "model", "parts": [{"text": "A stack is..."}]},
    {"role": "user",  "parts": [{"text": "Give an example"}]},
]
```
**Why limit N:** longer context costs more tokens, runs slower, and hits the free-tier limits sooner.
Extend the interface carefully (for example an optional `chat_id` argument with a default value) and tell the team in the PR so the GUI does not break.

### Task B7: SQLite history
**Tables:**
```sql
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role TEXT NOT NULL,          -- 'user' or 'model'
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```
**How:**
- Store the database file in `platformdirs.user_data_dir("DesktopAIAssistant")`, never in the project folder.
- Always use parameterized queries: `cur.execute("INSERT ... VALUES (?, ?, ?)", (chat_id, role, content))`. Never build SQL with f-strings.
- Enable foreign keys with `PRAGMA foreign_keys = ON`.
- Implement: `create_chat`, `add_message`, `get_messages`, `list_chats`, `delete_chat`.
- Auto-title a chat with the first 40 characters of the first question.
- Each thread should open its own connection (SQLite connections should not be shared across threads).

**Milestone 2 check (1 Nov):** Streaming works, memory works, closing and reopening the app keeps history.

---

## Week 3 (2–8 Nov): Smart Features

### Task B8: Prompts and context-aware modes
**What:** The assistant behaves differently depending on what the user is doing.
**How:** In `prompts.py`:
```python
PROMPTS = {
    "general": "You are a helpful assistant in a small overlay. Keep answers short and clear.",
    "coding":  "You are a coding mentor. Explain errors simply, give a short fix, show code in code blocks.",
    "lecture": "You are a patient tutor. Explain terms in simple words with one example.",
    "screen":  "The image is the user's screen. Explain what is shown and answer what they likely need.",
}
```
Mapping from Member C's `get_active_app()`: `"vscode" → "coding"`, `"browser" → "lecture"`, otherwise `"general"`. Put this mapping in one function (`pick_mode(app_name)`) so it is easy to test.
Pass the prompt as a system instruction (Gemini's `config=types.GenerateContentConfig(system_instruction=...)`).
Also add a line such as "Reply in the same language as the user (English, Urdu, or Roman Urdu)". Good for a Pakistani student audience.

**Why this impresses:** prompt engineering plus context awareness is a clear, demonstrable AI concept.

### Task B9: Image input (screenshots)
**How:**
```python
from google.genai import types
image_part = types.Part.from_bytes(data=png_bytes, mime_type="image/png")
contents = [image_part, "Explain what is on my screen"]
```
Member C resizes screenshots (about 1600 px wide) before sending, which keeps requests fast and cheap.

### Task B10: Ollama provider (offline mode)
**What:** Run a local model, so the assistant works without internet and without API limits.
**How:**
```python
import ollama
stream = ollama.chat(model="llama3.2", messages=msgs, stream=True)
for part in stream:
    yield part["message"]["content"]
```
- Ollama itself is installed separately from [ollama.com](https://ollama.com); the Python package is only the client.
- Handle "Ollama is not running" as a clean error.
- Image input needs a vision-capable local model; if the chosen model does not support images, show a clear message instead of crashing.
- Design both providers with the same method, e.g. `stream(messages, system_prompt, image)`, so `client.ask()` can simply choose one based on settings.

**Milestone 3 check (8 Nov):** Context modes, screenshot explanation and Ollama all work.

---

## Week 4 (9–15 Nov): Polish

### Task B11: Reliability
- **Rate limit (429):** retry 2–3 times with waiting (1 s, 2 s, 4 s), then raise `RateLimitError`.
- **Timeout:** do not wait forever; fail with `NetworkError` after a reasonable time.
- **Empty response:** return a friendly message instead of an empty string.
- Never print or log the API key.

### Task B12: Tests
Write tests with `pytest` and mocks (do not call the real API in tests):
- `pick_mode()` mapping
- history functions using a temporary database
- error mapping (fake exception → correct custom error)

Coordinate with Member C, who owns the `tests/` folder (you add `tests/test_ai.py` and `tests/test_storage.py` through your own PRs).

### Task B13: Cleanup
Docstrings on all public functions, remove unused code, make sure no secrets are in the repo history.

---

## Pull Requests You Will Open (suggested)

1. `feature/ai-dummy-interface` (Day 1)
2. `feature/gemini-basic`
3. `feature/api-key-storage`
4. `feature/error-handling`
5. `feature/streaming`
6. `feature/chat-memory`
7. `feature/sqlite-history`
8. `feature/prompts-and-modes`
9. `feature/image-input`
10. `feature/ollama-provider`
11. `fix/rate-limit-retry`
12. `test/backend-tests`

## What You Need From Others

| From | What |
|---|---|
| A | The settings dialog that calls your `save_api_key()`; error messages displayed in the chat |
| C | `get_active_app()` value, screenshot bytes (resized), test setup |

## What Others Need From You

- Dummy `ask()` and dummy history functions on Day 1.
- A short list of exceptions and what each one means (put it in a docstring at the top of `errors.py`).
- A stable `ask()` signature. If you must change it, announce it in the group chat and in the PR description.

## Common Mistakes to Avoid

- Hardcoding the API key or printing it in logs.
- Returning the whole answer at once instead of yielding chunks.
- Sending the entire chat history every time (slow, costly).
- Using one SQLite connection across threads.
- Building SQL strings with f-strings (SQL injection and bugs).
- Hardcoding the model name in many places.

## Your Definition of Done

- [ ] Works with a valid key, shows a friendly error with a wrong/missing key
- [ ] Streaming, memory and history all work after restarting the app
- [ ] Works offline with Ollama (demo-ready)
- [ ] Tests pass with `pytest`
- [ ] No secrets in code or commit history