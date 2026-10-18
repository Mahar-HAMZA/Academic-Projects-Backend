import os
import sys

import pyperclip
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel
)
from google import genai

# ==========================================
# Settings
# ==========================================
# API key code mein MAT likhein. Terminal mein set karein:
#   Windows (CMD):        set GEMINI_API_KEY=your_new_key
#   Windows (PowerShell): $env:GEMINI_API_KEY="your_new_key"
#   Linux / Mac:          export GEMINI_API_KEY=your_new_key
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")


# ==========================================
# 1. Background Thread for Gemini API Request
# ==========================================
class AIWorkerThread(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        if not API_KEY:
            self.response_ready.emit(
                "Error: GEMINI_API_KEY set nahi hai.\n"
                "Pehle environment variable set karein, phir program dobara chalayein."
            )
            return
        try:
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=(
                    "Give a short, precise answer suitable for a small overlay "
                    f"screen:\n{self.prompt}"
                ),
            )
            self.response_ready.emit(response.text or "(Khali jawab aaya)")
        except Exception as e:
            self.response_ready.emit(f"Error: {e}")


# ==========================================
# 2. Draggable round bubble button
#    (click = chat kholo, drag = window hilao)
# ==========================================
class BubbleButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._press_pos = None
        self._origin = None
        self._moved = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.globalPosition().toPoint()
            self._origin = self.window().frameGeometry().topLeft()
            self._moved = False
            event.accept()

    def mouseMoveEvent(self, event):
        if self._press_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._press_pos
            if delta.manhattanLength() > 5:
                self._moved = True
            if self._moved:
                self.window().move(self._origin + delta)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._press_pos is not None:
            if not self._moved:
                self.clicked.emit()
            self._press_pos = None
            event.accept()


# ==========================================
# 3. Main Floating AI Overlay Widget UI
# ==========================================
class FloatingAIAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.is_expanded = False
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # ---------------- Floating Bubble Button ----------------
        self.bubble_btn = BubbleButton("AI", self)
        self.bubble_btn.setFixedSize(50, 50)
        self.bubble_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.bubble_btn.clicked.connect(self.toggle_chat_window)
        self.main_layout.addWidget(self.bubble_btn)

        # ---------------- Chat Container Box ----------------
        self.chat_container = QWidget(self)
        self.chat_container.setObjectName("chatBox")
        self.chat_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.chat_container.setStyleSheet("""
            QWidget#chatBox {
                background-color: #111827;
                border-radius: 12px;
            }
        """)
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(8)

        # Header (title pe click karke drag kar sakte hain)
        header_layout = QHBoxLayout()
        title = QLabel("<b>AI Assistant</b>")
        title.setStyleSheet("color: #f3f4f6; background: transparent;")

        close_btn = QPushButton("X")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                color: #9ca3af; background: transparent;
                border: none; font-weight: bold;
            }
            QPushButton:hover { color: #ffffff; }
        """)
        close_btn.clicked.connect(self.toggle_chat_window)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)

        # Response Display Box
        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)
        self.response_box.setPlaceholderText("Answers will appear here...")
        self.response_box.setStyleSheet("""
            QTextEdit {
                background-color: #1f2937;
                color: #e5e7eb;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 6px;
            }
        """)

        # Input Prompt Field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask anything, ya khali chhor kar Enter dabayen (clipboard use hoga)...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #1f2937;
                color: #ffffff;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self.input_field.returnPressed.connect(self.send_query)

        # Send Button
        self.send_btn = QPushButton("Send")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #059669; }
            QPushButton:disabled { background-color: #374151; color: #9ca3af; }
        """)
        self.send_btn.clicked.connect(self.send_query)

        self.chat_layout.addLayout(header_layout)
        self.chat_layout.addWidget(self.response_box)
        self.chat_layout.addWidget(self.input_field)
        self.chat_layout.addWidget(self.send_btn)

        self.chat_container.setFixedSize(320, 380)
        self.chat_container.hide()
        self.main_layout.addWidget(self.chat_container)

        # Screen ke top-right mein shuru karo
        screen = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()
        self.move(screen.right() - 100, screen.top() + 80)

    # ---------------- Toggle Expanded Chat Window ----------------
    def toggle_chat_window(self):
        if self.is_expanded:
            self.chat_container.hide()
            self.bubble_btn.show()
            self.is_expanded = False
        else:
            self.bubble_btn.hide()
            self.chat_container.show()
            self.is_expanded = True
            self.input_field.setFocus()

        # Layout dobara hisaab lagaye, phir window ka size theek karo
        self.layout().activate()
        self.adjustSize()
        self._keep_on_screen()

    def _keep_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        geo = self.frameGeometry()
        x = min(max(geo.left(), screen.left()), screen.right() - geo.width())
        y = min(max(geo.top(), screen.top()), screen.bottom() - geo.height())
        self.move(x, y)

    # ---------------- Window Dragging (title/khali jagah se) ----------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and hasattr(self, "drag_position"):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if hasattr(self, "drag_position"):
            del self.drag_position

    # ---------------- Send Query ----------------
    def send_query(self):
        if self.worker is not None and self.worker.isRunning():
            return

        user_text = self.input_field.text().strip()

        # Input khali ho to clipboard se text lo
        if not user_text:
            try:
                copied_text = pyperclip.paste().strip()
            except Exception:
                copied_text = ""
            if not copied_text:
                return
            self.input_field.setText(copied_text)
            prompt = f"Explain this:\n{copied_text}"
        else:
            prompt = user_text

        self.response_box.setPlainText("Thinking...")
        self.send_btn.setEnabled(False)

        self.worker = AIWorkerThread(prompt)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.finished.connect(lambda: self.send_btn.setEnabled(True))
        self.worker.start()

    def handle_response(self, text):
        self.response_box.setPlainText(text)


# ==========================================
# 4. Entry Point
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = FloatingAIAssistant()
    assistant.show()
    sys.exit(app.exec())