from PyPDF2 import PdfReader
from docx import Document


def process_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() for page in reader.pages])
        return text
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


def process_docx(file_path):
    """Extract text from a DOCX file."""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error processing DOCX: {str(e)}"
