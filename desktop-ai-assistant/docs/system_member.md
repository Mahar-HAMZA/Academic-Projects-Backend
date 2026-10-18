# Member C: System Integration, Repository Owner, Testing and Documentation

**Goal:** Make the assistant "live inside Windows" (hotkey, selected text, screenshot, active app, auto-start), keep the team organized on GitHub, test everything, and deliver the final documentation, demo and release.

**Why this part matters:** This is what makes the project *different* from a normal chatbot website: it works on top of any app the user is using. You also hold the project together: without the repo setup, testing and release, the other two parts cannot be delivered as a product.

**Tools you will use:** `pynput`, `pyperclip`, `mss`, `Pillow`, `psutil`, `pywin32`, `winreg` (built-in), `pytest`, GitHub.

**Folders you own:** `assistant/system/`, `tests/`, `docs/`, `README.md`, `requirements.txt`, `.github/`.

You have **two jobs**: (1) system features, (2) repository owner / release manager.

---

## Suggested File Structure

```
assistant/system/
├── hotkey.py        # global keyboard shortcut
├── capture.py       # selected text, screenshot, active app
└── autostart.py     # start with Windows
tests/
├── test_hotkey.py
├── test_capture.py
└── test_autostart.py
docs/                # guides, architecture diagram, screenshots
.github/
└── pull_request_template.md
```

---

## Week 1 (19–25 Oct): Foundation

### Task C1 (Day 1, most important): Project skeleton and GitHub setup
**Why first:** Everyone is blocked until this is done. Do it on Day 1.

**Repository setup (you are the owner):**
1. Invite Member A and Member B as collaborators (**Settings → Collaborators**, Write access). Already sent. Confirm they accepted.
2. **Branch protection** for `main` (Settings → Branches → Add rule): require a Pull Request, require 1 approval.
3. **Labels:** `ui`, `ai`, `system`, `bug`, `docs`.
4. **Issues:** one per task from the three guides, with an assignee and a label (title example: "A: Floating bubble", "B: SQLite history", "C: Global hotkey").
5. **Project board:** Projects → New project → Board with columns `To Do`, `In Progress`, `Review`, `Done`; add all issues.
6. `.gitignore` (done), `requirements.txt` (done), `README.md` (first version: project name, one-paragraph idea, team, how to install).
7. `.github/pull_request_template.md` with a short checklist: *What changed? Related issue? Tested? No secrets?*

**Code skeleton (push to `main` on Day 1):**
```
assistant/__init__.py
assistant/ui/__init__.py
assistant/ai/__init__.py
assistant/storage/__init__.py
assistant/system/__init__.py
main.py                      # placeholder
```
Add **dummy versions** of the shared interface functions (see `ROADMAP.md`, section 3) in the right files, returning fake data, so every member can import them from Day 1:
```python
# assistant/system/capture.py (dummy)
def get_selected_text() -> str:
    return "dummy selected text"
def take_screenshot() -> bytes:
    return b""
def get_active_app() -> str:
    return "other"
```
Since only you can merge during the first hours, you can push this skeleton directly before enabling branch protection.

### Task C2: Global hotkey
**What:** A shortcut that works in any app and opens the assistant.
**How:**
```python
from pynput import keyboard

_listener = None

def register_hotkey(combo: str, callback) -> None:
    """combo like 'ctrl+shift+space'."""
    global _listener
    stop_hotkey()
    pynput_combo = "+".join(f"<{p}>" if len(p) > 1 else p for p in combo.lower().split("+"))
    _listener = keyboard.GlobalHotKeys({pynput_combo: callback})
    _listener.start()          # runs in its own thread

def stop_hotkey() -> None:
    global _listener
    if _listener:
        _listener.stop()
        _listener = None
```
Notes:
- The callback runs on a **background thread**. Member A connects it to a Qt Signal. Test it with A's window.
- Default hotkey: use `ctrl+shift+space`. `Ctrl+Space` can clash with Windows input-language switching and some editors.
- Write the combo conversion as a small separate function (`to_pynput_combo`) so it can be unit tested.
- Keep the combo configurable (from the Settings dialog).

### Task C3: Selected text capture
**What:** Get the text the user has highlighted in any app.
**How (the clipboard trick):**
1. Save the current clipboard content.
2. Put a unique marker string on the clipboard.
3. Simulate `Ctrl+C` using `pynput.keyboard.Controller`.
4. Wait ~150 ms, read the clipboard.
5. If it still equals the marker, nothing was selected, so return `""`.
6. Restore the original clipboard content.

**Pitfalls:**
- If the hotkey itself contains Shift/Ctrl and the user is still holding them, the simulated `Ctrl+C` can behave wrongly. Wait briefly (~100–200 ms) after the hotkey fires before simulating the copy.
- Always restore the user's old clipboard, otherwise the assistant would silently destroy what they copied.
- Wrap `pyperclip` calls in `try/except`.

### Task C4: Requirements and onboarding
Keep `requirements.txt` correct. Verify a *fresh* virtual environment installs it without errors. Help A and B if their setup fails (you are the "setup support" person in Week 1).

**Milestone 1 check (25 Oct):** Hotkey opens the assistant, selected text is captured, Gemini answers, and all issues/boards are live.

---

## Week 2 (26 Oct – 1 Nov): Core Features

### Task C5: Active application detection
**How:**
```python
import win32gui, win32process, psutil

def _active_process_name() -> str:
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return psutil.Process(pid).name().lower()

def classify_app(process_name: str) -> str:
    if process_name in {"code.exe", "code - insiders.exe"}:
        return "vscode"
    if process_name in {"chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"}:
        return "browser"
    return "other"

def get_active_app() -> str:
    try:
        return classify_app(_active_process_name())
    except Exception:
        return "other"
```
Keeping `classify_app()` separate makes it easy to unit test without needing real windows.
**Why it matters:** Member B uses this value to pick the prompt mode (coding / lecture / general).

### Task C6: Screenshot capture
**How:**
```python
import io, mss
from PIL import Image

def take_screenshot(max_width: int = 1600) -> bytes:
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[1])          # primary monitor
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
```
**Why resize:** A 4K screenshot is large; resizing keeps the AI request fast and within free limits.
Member A hides the window before calling this function.

### Task C7: First unit tests
Start the `tests/` folder:
- `test_hotkey.py`: `to_pynput_combo("ctrl+shift+space")` equals `"<ctrl>+<shift>+<space>"`.
- `test_capture.py`: `classify_app("code.exe") == "vscode"`, `classify_app("chrome.exe") == "browser"`, unknown → `"other"`.
- Run with `pytest`.

### Task C8: Weekly owner duties
Review and merge PRs (A and B review each other; you do the final merge), keep the board updated, fix conflicts, run the Sunday meeting.

**Milestone 2 check (1 Nov):** Active app + screenshot work; streaming chat and "Explain this" work end-to-end.

---

## Week 3 (2–8 Nov): Smart Features

### Task C9: Start with Windows
**How:** Add a value under the registry key `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`:
```python
import sys, winreg
KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
NAME = "DesktopAIAssistant"

def _command() -> str:
    if getattr(sys, "frozen", False):            # packaged .exe
        return f'"{sys.executable}"'
    return f'"{sys.executable}" "{__import__("os").path.abspath("main.py")}"'

def enable_autostart():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, NAME, 0, winreg.REG_SZ, _command())

def disable_autostart():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_SET_VALUE) as k:
        try: winreg.DeleteValue(k, NAME)
        except FileNotFoundError: pass

def is_autostart_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY) as k:
            winreg.QueryValueEx(k, NAME); return True
    except FileNotFoundError:
        return False
```
**Why HKCU:** it needs no administrator rights and affects only the current user.
Member A shows a checkbox in Settings that calls these functions.

### Task C10: Integration testing
Create a manual checklist in `docs/TESTING.md` and run it every week:
- [ ] Hotkey opens the assistant while VS Code / Edge / Notepad is focused
- [ ] Selected text → "Explain this" works in VS Code and in a browser
- [ ] Screenshot explanation works and our window is not in the screenshot
- [ ] Wrong API key and no-internet show friendly errors
- [ ] History survives an app restart
- [ ] Works on a second monitor
- [ ] Ollama mode works with Wi-Fi off

Report every bug as a GitHub Issue with *steps to reproduce*, *expected*, *actual*, and a screenshot, with the label `bug` and an assignee.

### Task C11: Documentation start
- **README.md:** overview, features, tech stack, install steps, usage, hotkeys, team.
- **Architecture diagram:** draw the flow (hotkey → capture → GUI → AI → answer → history). Use Mermaid in Markdown or draw.io, and save into `docs/`.

**Milestone 3 check (8 Nov):** Feature complete; bug list created and triaged.

---

## Week 4 (9–15 Nov): Test, Document, Release

### Task C12: Multi-laptop testing
Test the installer from Member A on 2–3 *different* laptops, ideally one with no Python installed. Record Windows version, result and issues. Check: install, first-run API key flow, hotkey, screenshot, auto-start after reboot, uninstall.

### Task C13: Final README
Add: screenshots (ask A), install guide (installer and from source), Gemini API key guide, Ollama guide, known limitations (internet needed for Gemini, free-tier limits, antivirus warnings), future work (voice input, macOS/Linux).

### Task C14: Demo video (2–3 minutes)
Record with OBS Studio or Xbox Game Bar (`Win+G`). Suggested script:
1. (0:00) The problem: switching to Google/ChatGPT breaks focus.
2. (0:20) Working in VS Code, hit an error, press the hotkey, the assistant explains it.
3. (0:50) Lecture or LeetCode: select a confusing word, press the hotkey, get an explanation.
4. (1:20) "Explain my screen" on a slide or problem.
5. (1:50) History, themes, tray icon.
6. (2:15) Offline mode with Ollama.
7. (2:40) Team and GitHub.

### Task C15: Presentation slides
Suggested outline (8–10 slides): Problem → Solution/Idea → Demo → Architecture diagram → AI concepts used (LLM, streaming, prompt engineering, context awareness, multimodal input, local models) → Tech stack → Team contributions (use GitHub Insights → Contributors) → Challenges and solutions → Limitations and future work → Q&A.

### Task C16: Release v1.0.0
1. Make sure `main` is stable and all PRs are merged.
2. Create a tag: `git tag v1.0.0` then `git push origin v1.0.0`.
3. GitHub → **Releases → Draft a new release**, choose the tag, write release notes, upload `DesktopAIAssistant-Setup.exe` from Member A.
4. Download it from GitHub once and test it as a user would.

**Milestone 4 check (15 Nov):** Release is published, README is final, video and slides are ready.

---

## Pull Requests You Will Open (suggested)

1. `feature/project-skeleton` (Day 1)
2. `feature/global-hotkey`
3. `feature/selected-text-capture`
4. `feature/active-window-detection`
5. `feature/screenshot-capture`
6. `test/system-tests`
7. `feature/autostart`
8. `docs/readme-and-architecture`
9. `docs/testing-checklist`
10. `docs/final-readme`

## Owner Checklist (every week)

- [ ] All issues have an assignee and a label; the board is current
- [ ] Open PRs reviewed within 24 hours
- [ ] `main` always runs (no broken code merged)
- [ ] Nobody committed a secret (if yes: revoke the key immediately, deleting the file is not enough)
- [ ] Sunday meeting held; next week's tasks assigned
- [ ] Milestone reached or the plan adjusted

## What You Need From Others

| From | What |
|---|---|
| A | Hotkey signal hook, screenshots for README, installer `.exe` |
| B | Docs on errors and modes, backend tests |

## What Others Need From You

- Dummy functions and the repo skeleton on Day 1.
- Working `register_hotkey`, `get_selected_text`, `take_screenshot`, `get_active_app` by the end of Week 2.
- Quick help with Git problems and merge conflicts.

## Common Mistakes to Avoid

- Forgetting to restore the clipboard after capturing selected text.
- Updating the UI from the hotkey thread (tell A to use signals).
- Using `Ctrl+Space` as the default hotkey (conflicts).
- Merging PRs without reviewing them.
- Leaving documentation and the demo video until the last day.
- Testing only on your own laptop.

## Your Definition of Done

- [ ] Hotkey, selection, screenshot, active app and auto-start work reliably
- [ ] Tests pass with `pytest`
- [ ] README, architecture diagram, demo video and slides are complete
- [ ] v1.0.0 is published on GitHub Releases and verified by downloading it