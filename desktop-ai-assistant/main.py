import sys
import pyperclip
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QLabel, QHBoxLayout
)
from google import genai

# ==========================================
# 1. Background Thread for Gemini API Request
# ==========================================
class AIWorkerThread(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            # Initialize Gemini API Client
            client = genai.Client(api_key="AQ.Ab8RN6Inh-kcYt2yShemoZ9EtnzWlXBuk2rV3JAUkmvgW2B61Q")
            
            # Send prompt to Gemini API
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=f"Give a short, precise answer suitable for a small overlay screen:\n{self.prompt}"
            )
            self.response_ready.emit(response.text)
        except Exception as e:
            self.response_ready.emit(f"Error: {str(e)}")

# ==========================================
# 2. Main Floating AI Overlay Widget UI
# ==========================================
class FloatingAIAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.old_position = QPoint()
        self.is_expanded = False
        self.initUI()

    def initUI(self):
        # Window Flags: Always on Top, Frameless Border, Tool Window Style
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        
        # Transparent Background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main Layout Setup
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # ---------------- Floating Bubble Button ----------------
        self.bubble_btn = QPushButton("🤖 AI", self)
        self.bubble_btn.setFixedSize(50, 50)
        self.bubble_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border-radius: 25px;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.bubble_btn.clicked.connect(self.toggle_chat_window)
        self.main_layout.addWidget(self.bubble_btn)

        # ---------------- Chat Container Box ----------------
        self.chat_container = QWidget(self)
        self.chat_layout = QVBoxLayout()

        # Header Title Bar
        header_layout = QHBoxLayout()
        title = QLabel("<b>AI Assistant</b>")
        title.setStyleSheet("color: #f3f4f6;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("color: #9ca3af; border: none; font-weight: bold;")
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
        self.input_field.setPlaceholderText("Ask anything or select text & press Enter...")
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
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.send_btn.clicked.connect(self.send_query)

        self.chat_layout.addLayout(header_layout)
        self.chat_layout.addWidget(self.response_box)
        self.chat_layout.addWidget(self.input_field)
        self.chat_layout.addWidget(self.send_btn)

        self.chat_container.setLayout(self.chat_layout)
        self.chat_container.setStyleSheet("""
            QWidget {
                background-color: #111827;
                border-radius: 12px;
            }
        """)
        self.chat_container.setFixedSize(320, 380)
        self.chat_container.hide()

        self.main_layout.addWidget(self.chat_container)
        self.setLayout(self.main_layout)

        # Initial Screen Position
        self.move(1200, 100)

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

    # ---------------- Mouse Events for Smooth Window Dragging ----------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Store the initial click position relative to the window frame
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            # Move the window dynamically as mouse cursor drags
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        # Reset drag state on mouse release
        if hasattr(self, 'drag_position'):
            del self.drag_position

    # ---------------- Send Query ----------------
    def send_query(self):
        user_text = self.input_field.text().strip()
        
        # Clipboard text auto-capture if input field is empty
        if not user_text and pyperclip:
            copied_text = pyperclip.paste().strip()
            if copied_text:
                user_text = f"Explain this:\n{copied_text}"
                self.input_field.setText(copied_text)
            else:
                return

        if not user_text:
            return

        self.response_box.setText("Thinking...")
        self.worker = AIWorkerThread(user_text)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, text):
        self.response_box.setText(text)

# ==========================================
# 3. Entry Point
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = FloatingAIAssistant()
    assistant.show()
    sys.exit(app.exec())