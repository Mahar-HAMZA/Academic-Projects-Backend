"""Central app settings and defaults. Owner: Member A."""

APP_NAME = "DesktopAIAssistant"
DEFAULT_HOTKEY = "ctrl+space"
DEFAULT_MODEL = "gemini-2.5-flash"   # change here if the model name changes
DEFAULT_PROVIDER = "gemini"          # "gemini" or "ollama"
OLLAMA_MODEL = "llama3.2"
CHAT_WINDOW_SIZE = (360, 460)
MEMORY_MESSAGES = 10                 # how many past messages are sent to the AI
