import time
from assistant.system.hotkey import register_hotkey

register_hotkey("ctrl+space", lambda: print("Hotkey pressed!"))
print("Press Ctrl+Space anywhere. Press Ctrl+C in this terminal to quit.")
while True:
    time.sleep(1)