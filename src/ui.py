from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QFileDialog, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QImageReader, QPixmap
from PyPDF2 import PdfReader
from docx import Document
import os


class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat and Document Viewer")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        # Central widget setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Sidebar (chat)
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(50)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_user_input)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(QLabel("Chat"))
        sidebar_layout.addWidget(self.chat_box)
        sidebar_layout.addWidget(self.input_box)
        sidebar_layout.addWidget(self.send_button)

        # File viewer
        self.file_viewer = QTextEdit()
        self.file_viewer.setReadOnly(True)

        self.open_file_button = QPushButton("Open File")
        self.open_file_button.clicked.connect(self.open_file)

        file_layout = QVBoxLayout()
        file_layout.addWidget(QLabel("Document Viewer"))
        file_layout.addWidget(self.file_viewer)
        file_layout.addWidget(self.open_file_button)

        # Combine layouts with splitter
        splitter = QSplitter(Qt.Horizontal)
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)

        file_viewer_widget = QWidget()
        file_viewer_widget.setLayout(file_layout)

        splitter.addWidget(sidebar_widget)
        splitter.addWidget(file_viewer_widget)

        main_layout.addWidget(splitter)

    def handle_user_input(self):
        """Handle user input and display response."""
        user_input = self.input_box.toPlainText().strip()
        if not user_input:
            return

        self.chat_box.append(f"You: {user_input}")
        response = self.get_response(user_input)
        self.chat_box.append(f"Bot: {response}")
        self.input_box.clear()

    def get_response(self, user_input):
        """Get AI-generated response (to be implemented in ai_model)."""
        from ai_model import get_response
        return get_response(user_input)

    def open_file(self):
        """Open and display PDF or DOCX files."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "PDF Files (*.pdf);;Word Documents (*.docx);;All Files (*)"
        )
        if file_path:
            if file_path.endswith(".pdf"):
                self.display_pdf(file_path)
            elif file_path.endswith(".docx"):
                self.display_docx(file_path)

    def display_pdf(self, file_path):
        """Render and display PDF file content."""
        reader = PdfReader(file_path)
        content = ""
        for page in reader.pages:
            content += page.extract_text() + "\n"

        self.file_viewer.setPlainText(content)

    def display_docx(self, file_path):
        """Render and display DOCX file content."""
        doc = Document(file_path)
        content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        self.file_viewer.setPlainText(content)
