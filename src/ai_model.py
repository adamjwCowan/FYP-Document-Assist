import os
import torch
from pdf2image import convert_from_path
from transformers import pipeline

# Load the Impira DocumentQA pipeline once
device = 0 if torch.cuda.is_available() else -1
document_qa = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa",
    framework="pt",
    device=device
)

def get_document_answer(pdf_path: str, question: str) -> str:
    """
    - Converts PDF → list of PIL Images (one per page).
    - Feeds each image into the Impira DocQA pipeline as `image=...`.
    - Automatically runs OCR, normalizes boxes (0–1000), and returns extractive answers.
    - Returns the highest-confidence answer across all pages.
    """
    if not os.path.exists(pdf_path):
        return "Error processing document: File not found."

    try:
        # PDF → PIL images via pdf2image
        images = convert_from_path(pdf_path)

        best_answer, best_score = None, 0.0
        for img in images:
            # Invoke pipeline on each page-image
            outputs = document_qa(image=img, question=question)

            # Extract top-scoring answer from this page
            if isinstance(outputs, list):
                for out in outputs:
                    score = out.get("score", 0.0)
                    if score > best_score:
                        best_score = score
                        best_answer = out.get("answer", "")

        return best_answer or "No answer found."

    except Exception as e:
        # Catch pdf2image, pipeline, or IO errors
        return f"Error processing document: {e}"