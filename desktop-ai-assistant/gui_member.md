# Member A: GUI (Everything the User Sees)

**Goal:** Build the floating bubble, the chat window, the tray icon, the settings dialog, and the final installer, so the assistant looks professional and feels instant.

**Why this part matters:** The GUI is what the teacher and every user will judge first. A smooth, good-looking overlay makes the project look like a real product. It is also the "glue" that connects Member B's AI and Member C's system features.

**Tools you will use:** `PySide6`, `markdown`, `Pygments`, `pyinstaller`, Inno Setup (free installer builder).

**Folders you own:** `assistant/ui/`, `assets/`, `installer/`, plus `main.py` and `assistant/config.py`.

---

## Suggested File Structure

```
assistant/ui/
├── bubble.py            # draggable round floating button
├── chat_window.py       # main chat overlay
├── tray.py              # system tray icon + menu
├── settings_dialog.py   # API key, hotkey, model, theme
├── history_panel.py     # list of old chats
├── markdown_view.py     # Markdown -> HTML rendering helper
├── themes.py            # dark / light stylesheets
└── workers.py           # QThread workers (AI streaming, screenshot)
assets/                  # icon.ico, logo.png
installer/               # PyInstaller .spec + Inno Setup .iss
```

---

## Week 1 (19–25 Oct): Foundation

### Task A1: Project skeleton and `main.py`
**What:** Create the Qt application and show the bubble.
**How:**
- Create `QApplication`, then call `app.setQuitOnLastWindowClosed(False)`.
- **Why that line:** without it, closing the chat window quits the whole program, but we want the assistant to keep living in the tray.
- Put settings like default hotkey and window size in `assistant/config.py`.

### Task A2: Floating bubble
**What:** A small round "AI" button that stays above all windows.
**How:**
- Window flags: `WindowStaysOnTopHint | FramelessWindowHint | Tool`, plus `WA_TranslucentBackground`.
- The `Tool` flag keeps it out of the taskbar.
- Make it draggable and clickable at the same time: remember the mouse press position; if the mouse moved more than ~5 px treat it as a drag, otherwise as a click. (The prototype `floating_ai.py` already has a working `BubbleButton` class you can reuse.)
- Remember the last position (save to settings) so it reappears where the user left it, and keep it inside the screen bounds.

### Task A3: Chat window
**What:** The small window that opens from the bubble.
**How:**
- Frameless, always on top, about 360×460 px, with a header (title, close button), a response area, an input box and a Send button.
- Use `QTextBrowser` for the response area (it can render HTML, which we need for Markdown later).
- `Enter` sends, `Shift+Enter` makes a new line (use `QPlainTextEdit` with a key-press override).
- `Esc` hides the window.
- Open the window next to the bubble and keep it on screen.

### Task A4: System tray
**What:** An icon near the Windows clock with a right-click menu.
**How:** `QSystemTrayIcon` + `QMenu` with **Open**, **Settings**, **Quit**. Double-click on the icon opens the chat.
**Why:** Safety net. If the hotkey fails or the bubble is hidden, the user can still open the assistant.

### Task A5: Settings dialog (basic)
**What:** A `QDialog` with: API key (`QLineEdit` with `setEchoMode(Password)`), hotkey text field, AI model dropdown (`QComboBox`: Gemini / Ollama).
**How:** On Save, call Member B's `save_api_key()` and store the other values in the settings file. On first launch with no API key, open this dialog automatically.

### Task A6: Connect to a dummy backend
**What:** Make the whole UI testable without Members B and C.
**How:** Write a fake generator in your own folder:
```python
import time
def fake_ask(prompt, image=None, mode="general"):
    for word in f"Fake answer to: {prompt}".split():
        yield word + " "
        time.sleep(0.05)
```
Switch to the real `assistant.ai.client.ask` when Member B merges it.

**Never call the AI on the UI thread.** The window would freeze. Use a `QThread` worker (see Week 2).

---

## Week 2 (26 Oct – 1 Nov): Core Features

### Task A7: Streaming display
**What:** Text appears word by word.
**How:**
- Create `AskWorker(QThread)` with signals `chunk = Signal(str)`, `finished_ok = Signal()`, `failed = Signal(str)`.
- In `run()`: `for piece in ask(prompt, image, mode): self.chunk.emit(piece)`; catch exceptions and emit `failed`.
- In the window slot, add each piece to a text buffer and re-render. To keep it smooth, update the display at most every ~50 ms (use a `QTimer`).
- Disable the Send button while a request is running, and add a **Stop** button (set a flag the worker checks between chunks).

### Task A8: Markdown and code blocks
**What:** AI answers contain `**bold**`, lists and code blocks; show them nicely.
**How:**
- `markdown.markdown(text, extensions=["fenced_code", "codehilite", "tables"])`, then `browser.setHtml(html)`.
- Put the CSS for code blocks (dark background, monospace font) in `themes.py`.
- Note: `QTextBrowser` supports only basic HTML/CSS, so test how it looks and keep styling simple.

### Task A9: Copy buttons
**What:** Copy the whole answer and copy a single code block.
**How:**
- "Copy answer": `QApplication.clipboard().setText(last_answer)`.
- For code blocks, add a small link above each block like `<a href="copy:3">Copy</a>`, enable `setOpenLinks(False)` and handle `anchorClicked` to copy block number 3.
- Show a short "Copied!" message so the user gets feedback.

### Task A10: History panel and New Chat
**What:** A button that lists old chats; clicking one loads it.
**How:** Use Member B's `list_chats()`, `get_messages()`, `delete_chat()`. A `QListWidget` in a side panel or a separate small window. **New chat** button calls `create_chat()` and clears the view. Until Member B is ready, use fake data.

**Milestone 2 check (1 Nov):** Streaming chat with Markdown, copy buttons and history works with the real backend.

---

## Week 3 (2–8 Nov): Smart Features

### Task A11: "Explain my screen" button
**What:** One click, and the assistant explains what is on the screen (lecture slide, LeetCode problem, error message).
**How:**
1. Hide the assistant window.
2. Wait ~200 ms (`QTimer.singleShot`) so Windows finishes redrawing.
3. Call Member C's `take_screenshot()`.
4. Show the window again.
5. Run the worker with `ask("Explain what is on my screen", image=png_bytes, mode="screen")`.

**Why hide first:** otherwise our own overlay appears in the screenshot.

### Task A12: "Explain this" for selected text
**What:** Triggered by hotkey: grab the selected text and send it to the AI.
**How:** In the hotkey callback (a background thread), emit a Qt Signal. A slot on the main thread calls `get_selected_text()`, opens the window, and sends `"Explain this:\n" + text`. If no text is selected, just open the chat.

### Task A13: Dark and light themes
**How:** Two QSS stylesheets in `themes.py` using one set of color variables; apply with `app.setStyleSheet(...)`. Toggle in the Settings dialog and save the choice.
**Tip:** Avoid `box-shadow` (not supported by Qt style sheets). Use `QGraphicsDropShadowEffect` if you need a shadow.

### Task A14: Animations and polish
**How:** Fade-in using `QPropertyAnimation(window, b"windowOpacity")` (0 → 1 in ~150 ms). A "Thinking..." indicator while waiting for the first chunk. Friendly messages for errors that come from Member B (no key, no internet, rate limit).

**Milestone 3 check (8 Nov):** Every GUI feature works with real backend and system modules.

---

## Week 4 (9–15 Nov): Packaging

### Task A15: Build the `.exe`
**How:**
```powershell
pyinstaller --noconsole --name DesktopAIAssistant --icon assets/icon.ico main.py
```
- Prefer the default *one-folder* build over `--onefile`: it starts faster and triggers fewer antivirus warnings.
- Assets (icons) will not be found by relative paths after packaging. Write a helper:
  ```python
  import sys, os
  def resource_path(rel):
      base = getattr(sys, "_MEIPASS", os.path.abspath("."))
      return os.path.join(base, rel)
  ```
- Test the built app on a computer that **does not have Python**.

### Task A16: Installer
**How:** Install **Inno Setup**, create `installer/setup.iss` pointing at the `dist/DesktopAIAssistant` folder. The wizard should create a Start-menu shortcut and offer "Start with Windows". Output: `DesktopAIAssistant-Setup.exe`. Give it to Member C for the GitHub Release.

### Task A17: Final fixes
Multi-monitor positions, high-DPI scaling, very long answers (scrolling), empty input, double-click on Send.

---

## Pull Requests You Will Open (suggested)

1. `feature/project-skeleton`
2. `feature/floating-bubble`
3. `feature/chat-window`
4. `feature/tray-and-settings`
5. `feature/streaming-display`
6. `feature/markdown-copy`
7. `feature/history-panel`
8. `feature/explain-screen`
9. `feature/themes`
10. `feature/installer`

## What You Need From Others

| From | What | When |
|---|---|---|
| B | `ask()`, `save_api_key()`, history functions (dummy first, real later) | Dummy: Day 1. Real: Week 1–2 |
| C | `register_hotkey()`, `get_selected_text()`, `take_screenshot()` | Dummy: Day 1. Real: Week 1–2 |

## What Others Need From You

- Signal/slot hook for the hotkey (so Member C can test `register_hotkey` with your window).
- A clear error-display function so Member B's exceptions are shown nicely.

## Common Mistakes to Avoid

- Calling the AI on the main thread (the app freezes).
- Updating widgets from the hotkey thread (random crashes). Always use signals.
- Forgetting `setQuitOnLastWindowClosed(False)` (app quits when the chat closes).
- Hardcoding the API key (never).
- Editing `assistant/ai/` or `assistant/system/` files (they belong to B and C).

## Your Definition of Done

- [ ] Works in dark and light theme
- [ ] No freezing while the AI is answering
- [ ] Works on a second monitor and at 125%/150% Windows scaling
- [ ] Installer tested on a clean Windows machine
- [ ] Screenshots of every screen given to Member C for the README