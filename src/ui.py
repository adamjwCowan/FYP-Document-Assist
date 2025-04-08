from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QFileDialog, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from io import BytesIO
from file_processing import process_pdf, process_docx
from ai_model import get_document_answer
from PIL import Image

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Document QA Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.document_images = []  # List to hold PIL Image objects from the loaded document
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Sidebar: Chat interface
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

        # Document Viewer: Display the first page of the document
        self.file_viewer = QLabel("No document loaded.")
        self.file_viewer.setAlignment(Qt.AlignCenter)
        self.open_file_button = QPushButton("Open File")
        self.open_file_button.clicked.connect(self.open_file)

        file_layout = QVBoxLayout()
        file_layout.addWidget(QLabel("Document Viewer"))
        file_layout.addWidget(self.file_viewer)
        file_layout.addWidget(self.open_file_button)

        splitter = QSplitter(Qt.Horizontal)
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        file_widget = QWidget()
        file_widget.setLayout(file_layout)
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(file_widget)
        main_layout.addWidget(splitter)

    def handle_user_input(self):
        user_input = self.input_box.toPlainText().strip()
        if not user_input:
            return
        self.chat_box.append("You: " + user_input)
        # Use the first image for answering questions
        if self.document_images:
            answer = get_document_answer(self.document_images[0], user_input)
            self.chat_box.append("Bot: " + answer)
        else:
            self.chat_box.append("Bot: No document loaded. Please upload a document.")
        self.input_box.clear()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "PDF Files (*.pdf);;Word Documents (*.docx);;All Files (*)"
        )
        if file_path:
            if file_path.lower().endswith(".pdf"):
                self.document_images = process_pdf(file_path)
            elif file_path.lower().endswith(".docx"):
                self.document_images = process_docx(file_path)
            # Display the first page in the document viewer if available
            if self.document_images:
                self.display_image(self.document_images[0])
                self.chat_box.append("Document loaded successfully.")
            else:
                self.chat_box.append("Failed to load document.")

    def display_image(self, image):
        """
        Convert a PIL Image to QPixmap and display it in the QLabel.
        """
        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes.read(), "PNG")
        self.file_viewer.setPixmap(pixmap.scaled(
            self.file_viewer.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
