# Desktop AI Assistant: 1-Month Roadmap and Team Workflow

**Duration:** 19 October 2026 – 15 November 2026 (4 Weeks)  
**Team:** 3 Members (A, B, and C)  
**Platform:** Windows  
**Technology:** Python 3.11+ and PySide6

---

## 1. Team Roles and Responsibilities

Each team member is responsible for a specific part of the project. This will help everyone work independently and reduce merge conflicts.

| Member | Role | Responsible Folders |
|---|---|---|
| **A** | UI and App Shell (Team Lead) | `assistant/ui/`, `assets/`, `installer/` |
| **B** | AI and Data | `assistant/ai/`, `assistant/storage/` |
| **C** | System Integration, Testing, and Documentation | `assistant/system/`, `tests/`, `README.md`, `docs/` |

**Important:** Only Member A can directly edit `main.py` and `assistant/config.py`. Other members must request changes through a Pull Request (PR).

### Member A: UI and App Shell

- Create a floating assistant bubble and chat window.
- Make the chat window frameless, always on top, and draggable.
- Add a system tray icon with Open, Settings, and Quit options.
- Create a settings window for the API key, keyboard shortcut, and AI model.
- Display Markdown text and code blocks.
- Add a button to copy responses.
- Implement dark and light themes.
- Build the Windows `.exe` using PyInstaller.
- Create an installer using Inno Setup.

### Member B: AI and Data

- Connect Gemini using the `google-genai` library.
- Implement streaming responses so text appears as it is generated.
- Create prompts for general questions, coding, lectures, and screen explanations.
- Store recent conversation messages as context.
- Save chat history in an SQLite database.
- Add Ollama support for running local AI models.
- Handle errors such as no internet, invalid API keys, and rate limits.

### Member C: System Integration, Testing, and Documentation

- Implement global keyboard shortcuts using `pynput`.
- Capture selected text by simulating `Ctrl+C` and restoring the clipboard afterward.
- Capture screenshots using `mss` and `Pillow`.
- Detect the active application, such as VS Code, a browser, or another application.
- Add an option to start the assistant automatically when Windows starts.
- Write unit and integration tests.
- Report bugs and maintain project documentation.
- Prepare the README, demo video, and presentation slides.

---

## 2. Shared Interfaces

**Week 1, Day 1: All team members must agree on these interfaces.**

Before working separately, the team should decide on the function names, parameters, and return types. This will allow each member to develop their part without waiting for the others.

### AI Client — Member B

File: `assistant/ai/client.py`

```python
def ask(
    prompt: str,
    image: bytes | None = None,
    mode: str = "general"
):
    """Generate a response and yield text chunks."""
```

This function sends a prompt to the AI and returns the response in small chunks as it is generated.

### System Capture — Member C

File: `assistant/system/capture.py`

```python
def get_selected_text() -> str:
    ...

def take_screenshot() -> bytes:
    ...  # Returns PNG image bytes

def get_active_app() -> str:
    ...  # Returns "vscode", "browser", or "other"
```

These functions capture selected text, take screenshots, and identify the currently active application.

### Global Hotkey — Member C

File: `assistant/system/hotkey.py`

```python
def register_hotkey(combo: str, callback) -> None:
    ...
```

This function registers a keyboard shortcut and runs the callback when the shortcut is pressed.

### Settings Storage — Member B

File: `assistant/storage/settings.py`

```python
def get_api_key() -> str:
    ...

def save_api_key(key: str) -> None:
    ...
```

These functions retrieve and save the user's API key securely.

**Development rule:** Until the actual functions are ready, use temporary dummy functions that return sample data. This allows Member A to build and test the UI without waiting for Members B and C.

---

## 3. Week-by-Week Development Plan

### Week 1: Foundation (19–25 October)

| Member | Tasks |
|---|---|
| **A** | Set up the project structure, create the floating bubble and chat window, add the system tray icon, and build a basic settings window. |
| **B** | Connect Gemini without streaming first, store the API key securely using `keyring`, and implement basic error messages. |
| **C** | Set up GitHub branches, issues, and a project board. Implement the global hotkey, selected-text capture, and `requirements.txt`. |

**Milestone 1 — 25 October:** Pressing the hotkey opens the assistant, and users can ask questions and receive Gemini responses.

### Week 2: Core Features (26 October–1 November)

| Member | Tasks |
|---|---|
| **A** | Display streaming responses, support Markdown and code blocks, add a copy button, and improve the chat interface. |
| **B** | Implement streaming responses, conversation memory, SQLite chat history, and New Chat and History features. |
| **C** | Add active-window detection and screenshot capture, and write the first unit tests. |

**Milestone 2 — 1 November:** Streaming chat, chat history, and the Explain This feature for selected text are working.

### Week 3: Smart Features (2–8 November)

| Member | Tasks |
|---|---|
| **A** | Add an Explain My Screen button, dark and light themes, animations, and UI improvements. |
| **B** | Add context-aware prompts for coding, lectures, and general questions. Implement screenshot input for Gemini and add the Ollama provider. |
| **C** | Add Windows startup support, perform integration testing, create a bug list, and begin the README and architecture diagram. |

**Milestone 3 — 8 November:** All major features are complete, including screen explanation, different context modes, and Ollama support.

### Week 4: Packaging and Presentation (9–15 November)

| Member | Tasks |
|---|---|
| **A** | Build the Windows `.exe` using PyInstaller, create the installer using Inno Setup, and fix the remaining UI issues. |
| **B** | Improve error handling, handle API rate limits, clean up the code, and add comments. |
| **C** | Test the application on 2–3 different laptops, finalize the README, record a demo video, and prepare presentation slides. |

**Milestone 4 — 15 November:** Release version 1.0 on GitHub Releases and prepare the final demo.

> **Important:** Keep the last two days of Week 4 for bug fixing and presentation practice. Do not add any new features during this time.

---

## 4. GitHub Workflow

Use GitHub to organize tasks, track progress, review code, and manage teamwork.

### 4.1 Initial Setup

Member A or C should complete the following steps:

1. The repository owner must add the other two members through **Settings → Collaborators**, granting them write access.
2. Create a GitHub Issue for each task, such as "Add Global Hotkey" or "Implement Streaming Responses." Assign each issue to a team member and set a milestone.
3. Create a Kanban board in the Projects tab with these columns:

   `To Do → In Progress → Review → Done`

4. Create labels for organizing tasks:

   - `ui`
   - `ai`
   - `system`
   - `bug`
   - `docs`

5. Enable branch protection for `main` by requiring Pull Requests before merging. This prevents team members from pushing changes directly to `main`.
6. Create a `.gitignore` file to exclude unnecessary files.

Example `.gitignore`:

```gitignore
venv/
__pycache__/
*.py[cod]
.env
*.db
dist/
build/
```

### 4.2 Daily Git Workflow

Every team member should follow these steps when starting a task.

**Step 1: Get the latest code**

```bash
git checkout main
git pull origin main
```

**Step 2: Create a new branch for your task**

```bash
git checkout -b feature/hotkey-support
```

**Step 3: Make changes and commit them**

```bash
git add .
git commit -m "feat(system): add global hotkey listener"
```

**Step 4: Push your branch to GitHub**

```bash
git push -u origin feature/hotkey-support
```

**Step 5: Open a Pull Request**

- Open a Pull Request on GitHub.
- Link the related issue, for example, `Closes #5`.
- Ask at least one other team member to review your code.
- After approval, use **Squash and merge**.

**Step 6: Update your local main branch**

After the Pull Request has been merged:

```bash
git checkout main
git pull origin main
```

Then create a new branch for your next task.

### 4.3 Naming Rules

| Item | Format | Example |
|---|---|---|
| Branch | `feature/<name>` or `fix/<name>` | `feature/streaming-response` |
| Commit | `type(area): message` | `fix(ui): overlay position on second monitor` |

Use these commit types:

- `feat` — Add a new feature.
- `fix` — Fix a bug.
- `docs` — Update documentation.
- `test` — Add or update tests.
- `refactor` — Improve code structure without changing its behavior.

### 4.4 How to Track Team Progress

Use the following GitHub features to see who is doing what:

- **Commits / `git log`:** See who made each change and when.
- **Pull Requests:** Review changes and see who merged them.
- **Projects board:** Check the status and owner of each task.
- **Insights → Contributors:** See contribution statistics for the team. These can also help during the final presentation.
- **Optional:** Connect the GitHub repository to a WhatsApp or Discord group, or share daily progress updates there.

### 4.5 How to Avoid Merge Conflicts

- Work only in your assigned folders. If another file needs changes, coordinate with its owner.
- Pull the latest changes from `main` regularly.
- Keep branches short-lived, ideally no longer than 2–3 days.
- Keep each Pull Request focused on one task.
- Agree on shared interfaces before developing features in parallel.

### 4.6 Team Communication

- **Daily check-in (10 minutes):** Each member shares what they did yesterday, what they will do today, and whether they have any blockers.
- **Weekly meeting (Sunday, 30 minutes):** Review the current milestone and assign tasks for the next week.
- **Bug tracking:** Report bugs and new ideas through GitHub Issues so that important information is not lost in chat messages.

---

## 5. Development Environment

All team members should use the same development environment.

### Requirements

- Windows 10 or Windows 11.
- Python 3.11 or newer.
- Git installed and configured.
- A code editor such as VS Code.
- A Gemini API key for each member.

**Important:** Develop directly on Windows rather than WSL because the floating window, global hotkeys, and screenshot features need to interact with Windows applications.

### Project Setup

Open PowerShell and run:

```powershell
cd desktop-ai-assistant

python -m venv venv

venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

If PowerShell blocks virtual environment activation, use Command Prompt and run:

```bat
venv\Scripts\activate.bat
```

### API Key Security

- Each member should use their own Gemini API key.
- Never upload API keys, passwords, or other secrets to GitHub.
- Store API keys securely using `keyring` or another appropriate secure storage method.
- If a new package is installed, update `requirements.txt` and mention the change in the Pull Request.

---

## 6. Definition of Done

A task is complete only when all applicable requirements below are satisfied.

- [ ] The code runs correctly without unexpected crashes.
- [ ] No API keys or passwords are hardcoded in the source code.
- [ ] Important functions have comments or docstrings where needed.
- [ ] The changes have been reviewed through a Pull Request.
- [ ] Relevant tests pass.
- [ ] The README or documentation is updated if the feature affects users.
- [ ] The changes have been merged into `main`.

---

## 7. Project Risks and Solutions

| Risk | Solution |
|---|---|
| Gemini free-tier limit is reached. | Use Ollama as a local alternative and reduce unnecessary API requests. |
| The global hotkey does not work in some applications. | Allow users to open the assistant through the system tray icon as well. |
| Antivirus software warns about the `.exe`. | Test the installer properly and document any warnings in the README. |
| A team member becomes unavailable. | Discuss task reassignment during the weekly meeting and update the GitHub Projects board. |
| Merge conflicts occur. | Follow folder ownership rules, use shared interfaces, and keep Pull Requests small. |

---

## 8. Final Deliverables

By 15 November 2026, the team should prepare the following:

- [ ] A GitHub repository with clean commit history, issues, and Pull Requests.
- [ ] A Windows `.exe` installer published through GitHub Releases.
- [ ] A complete README with features, installation instructions, and screenshots.
- [ ] An architecture diagram explaining the application's structure.
- [ ] A 2–3 minute demo video showing the main features.
- [ ] Presentation slides explaining the project, its features, and team contributions.

---

## Final Goal

By the end of this four-week roadmap, the team should have a working Windows Desktop AI Assistant that supports AI chat, streaming responses, chat history, selected-text explanations, screenshot-based screen explanations, keyboard shortcuts, and local AI models through Ollama.

The project should also be tested, documented, packaged as a Windows application, and ready for its final demonstration on 15 November 2026.