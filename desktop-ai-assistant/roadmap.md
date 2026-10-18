# Desktop AI Assistant: Team Roadmap (Overview)

**Duration:** 19 October 2026 – 15 November 2026 (4 Weeks)
**Platform:** Windows 10/11 | **Language:** Python 3.11+ | **GUI:** PySide6
**Repository owner:** Member C

This file is the shared overview for the whole team. Each member also has a detailed personal guide:

| Member | Part | Detailed guide |
|---|---|---|
| **A** | GUI (everything the user sees) | [docs/gui_member.md](docs/gui_member.md) |
| **B** | Backend (AI + data) | [docs/backend_member.md](docs/backend_member.md) |
| **C** | System integration, repo owner, testing, docs, release | [docs/system_member.md](docs/system_member.md) |

---

## 1. What We Are Building

A small AI assistant that lives on the screen as a floating bubble. The user is working in VS Code, a browser lecture, LeetCode, etc. They press a hotkey or click the bubble, a small chat window opens, and they can ask anything (or let the assistant explain their selected text or their whole screen) without switching apps.

```
 Hotkey / Bubble click
        |
        v
 [C] capture selected text / screenshot / active app
        |
        v
 [A] GUI window  --->  [B] AI client (Gemini / Ollama) + history
        ^                          |
        |__________ streamed answer _|
```

---

## 2. Roles and Folder Ownership

Each member owns specific folders. Do not edit files outside your folders without telling the owner (reason: this avoids merge conflicts).

| Member | Role | Folders owned |
|---|---|---|
| **A** | GUI | `assistant/ui/`, `assets/`, `installer/`, `main.py`, `assistant/config.py` |
| **B** | Backend | `assistant/ai/`, `assistant/storage/` |
| **C** | System, Owner, Tests, Docs | `assistant/system/`, `tests/`, `docs/`, `README.md`, `requirements.txt`, `.github/` |

---

## 3. Shared Interfaces (Contracts)

**Week 1, Day 1:** all three members agree on these. Until the real code exists, each owner pushes a *dummy version* that returns fake data, so nobody waits for anybody.

```python
# assistant/ai/client.py                       (Member B)
def ask(prompt: str, image: bytes | None = None, mode: str = "general"):
    """Generator. Yields response text chunks as they arrive."""

# assistant/storage/settings.py                (Member B)
def get_api_key() -> str: ...
def save_api_key(key: str) -> None: ...

# assistant/storage/history.py                 (Member B)
def create_chat(title: str = "New chat") -> int: ...
def add_message(chat_id: int, role: str, content: str) -> None: ...
def get_messages(chat_id: int) -> list[dict]: ...    # [{"role": "user", "content": "..."}]
def list_chats() -> list[dict]: ...                  # [{"id": 1, "title": "...", "created_at": "..."}]
def delete_chat(chat_id: int) -> None: ...

# assistant/system/capture.py                  (Member C)
def get_selected_text() -> str: ...
def take_screenshot() -> bytes: ...            # PNG bytes
def get_active_app() -> str: ...               # "vscode" | "browser" | "other"

# assistant/system/hotkey.py                   (Member C)
def register_hotkey(combo: str, callback) -> None: ...   # e.g. "ctrl+shift+space"
def stop_hotkey() -> None: ...

# assistant/system/autostart.py                (Member C)
def enable_autostart() -> None: ...
def disable_autostart() -> None: ...
def is_autostart_enabled() -> bool: ...
```

**Important threading rule:** the hotkey callback runs on a *background thread*. Member A must never touch widgets directly from it; use a Qt Signal to show the window. Same for streaming: `ask()` runs in a worker thread, the UI updates through signals.

---

## 4. Week-by-Week Plan

### Week 1: Foundation (19–25 Oct)
| Member | Goal |
|---|---|
| **A** | Project skeleton in `main.py`, bubble, chat window, tray icon, settings dialog (using dummy backend) |
| **B** | Gemini connection (non-streaming), API key storage with `keyring`, clear error messages |
| **C** | GitHub setup + project skeleton with dummy functions (Day 1), global hotkey, selected-text capture |

**Milestone 1 (25 Oct):** Hotkey opens the assistant, user asks a question, Gemini answers.

### Week 2: Core Features (26 Oct – 1 Nov)
| Member | Goal |
|---|---|
| **A** | Streaming display, Markdown + code blocks, copy buttons, history panel |
| **B** | Streaming, conversation memory, SQLite history |
| **C** | Active-window detection, screenshot capture, first unit tests |

**Milestone 2 (1 Nov):** Streaming chat + history + "Explain this" for selected text.

### Week 3: Smart Features (2–8 Nov)
| Member | Goal |
|---|---|
| **A** | "Explain my screen" button, dark/light themes, animations |
| **B** | Context-aware prompts, image input, Ollama provider |
| **C** | Windows auto-start, integration testing, bug list, README + architecture diagram |

**Milestone 3 (8 Nov):** Feature complete (screen explain, context modes, Ollama).

### Week 4: Packaging and Presentation (9–15 Nov)
| Member | Goal |
|---|---|
| **A** | PyInstaller build, Inno Setup installer, UI fixes |
| **B** | Error handling polish, rate limits, cleanup, docstrings |
| **C** | Test on 2–3 laptops, final README, demo video, slides, GitHub Release v1.0.0 |

**Milestone 4 (15 Nov):** Release v1.0.0 and final demo.

> The last 2 days of Week 4 are only for bug fixing and presentation practice. **No new features.**

---

## 5. GitHub Workflow (summary)

Repo owner: **Member C**. Full details are in Member C's guide; every member follows the same daily flow:

```bash
git checkout main
git pull origin main
git checkout -b feature/<short-name>
# ...work...
git add .
git commit -m "feat(ui): add settings dialog"
git push -u origin feature/<short-name>
# open a Pull Request on GitHub, link the issue ("Closes #5"), request a review
```

Rules:
1. Never push directly to `main` (branch protection is on).
2. Every PR needs at least 1 review from another member. Reviewers: A and B review each other's work; C reviews both and merges.
3. One PR = one task. Keep branches alive for at most 2–3 days.
4. Branch names: `feature/<name>`, `fix/<name>`. Commit format: `type(area): message` with types `feat`, `fix`, `docs`, `test`, `refactor`.
5. Never commit API keys, `.env`, `venv/`, or `*.db`.
6. Pull `main` every morning.

Communication: 10-minute daily check-in in the group chat (yesterday / today / blockers) and a 30-minute meeting every Sunday.

---

## 6. Environment Setup (everyone, on Windows, not WSL)

```powershell
git clone https://github.com/<owner-username>/AcademicProjects.git
cd AcademicProjects\desktop-ai-assistant
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use `venv\Scripts\activate.bat` in CMD.

Each member uses their **own** Gemini API key (free from Google AI Studio). Keys are never committed.

---

## 7. Definition of Done (for every task)

- [ ] Code runs without crashing
- [ ] No API keys or passwords in the code
- [ ] Functions have docstrings/comments where needed
- [ ] Reviewed and approved via Pull Request
- [ ] Relevant tests pass
- [ ] README/docs updated if users will notice the change
- [ ] Merged into `main` and the issue is closed

---

## 8. Risks and Solutions

| Risk | Solution |
|---|---|
| Gemini free-tier limit reached | Ollama fallback, fewer requests, short answers |
| Hotkey conflicts with another app | Configurable hotkey + tray icon and bubble as alternatives |
| Antivirus flags the `.exe` | Use one-folder build, test the installer, note it in README |
| A member is unavailable | Reassign tasks in the weekly meeting, update the board |
| Merge conflicts | Folder ownership, shared interfaces, small PRs |
| Real code not ready for others | Everyone pushes dummy versions on Day 1 |

---

## 9. Final Deliverables (15 Nov 2026)

- [ ] GitHub repo with clean history, issues and PRs
- [ ] Windows installer published on GitHub Releases (v1.0.0)
- [ ] Complete README (features, install guide, screenshots)
- [ ] Architecture diagram
- [ ] 2–3 minute demo video
- [ ] Presentation slides with each member's contribution