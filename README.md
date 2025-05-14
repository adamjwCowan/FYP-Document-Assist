Document QA Assistant

A web application built with Streamlit that allows users to upload PDF documents and interactively ask questions about the content. The assistant utilizes AI models to provide answers and highlights relevant sections within the document.

 Features

    PDF Upload: Drag and drop PDF files for analysis.

    Interactive Q&A: Ask questions about the document's content.

    AI-Powered Responses: Get answers with highlighted sections for context.

    Layman Mode: Option to simplify technical responses.

    Code Mode: Option to focus on code-related explanations.

 Technologies Used

    Frontend: Streamlit

    PDF Processing: PyMuPDF, pdf2image

    Image Processing: Pillow, pytesseract

    AI Models: transformers, torch, torchvision

    Testing: pytest

    Web Interaction: selenium

    Utilities: requests, streamlit-pdf-viewer, streamlit-float, file_validator

 Installation

Clone this repository and install the required dependencies:

git clone https://github.com/adamjwCowan/FYP-Document-Assist.git
cd FYP-Documnet-Assist
pip install -r requirements.txt

Ensure that poppler and tesseract-OCR are installed and that the system paths are set for both. Ensure that the env python interpreter is using Python 3.8.3.

    Running the Application

To start the application locally:

Either run the main.py class or use python -m streamlit run src/app.py in the terminal

Visit http://localhost:8501 in your browser to interact with the app.
     File Upload Limit

The application supports PDF uploads up to 10 MB. Ensure your file does not exceed this size to avoid upload errors.
     Running Tests

To run the test suite:

pytest
