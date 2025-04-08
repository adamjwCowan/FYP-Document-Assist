import os
from pdf2image import convert_from_path
from docx2pdf import convert as docx2pdf_convert
from PIL import Image

def process_pdf(file_path):
    """
    Convert each page of the PDF to an image.
    Returns a list of PIL Image objects.
    """
    try:
        images = convert_from_path(file_path)
        return images
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return []

def process_docx(file_path):
    """
    Convert a DOCX file to PDF using docx2pdf,
    then convert the PDF to images.
    """
    try:
        # Convert DOCX to a temporary PDF file
        output_pdf = file_path.replace(".docx", ".pdf")
        docx2pdf_convert(file_path, output_pdf)
        images = process_pdf(output_pdf)
        # Optionally remove the temporary PDF
        os.remove(output_pdf)
        return images
    except Exception as e:
        print(f"Error processing DOCX: {e}")
        return []
