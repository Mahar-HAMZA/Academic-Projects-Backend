import time
from assistant.system.capture import get_selected_text

print("Select some text in any app. Capturing in 4 seconds...")
time.sleep(4)
print("Selected:", repr(get_selected_text()))