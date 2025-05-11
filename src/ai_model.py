import os
import torch
import fitz                     # PyMuPDF for PDF operations
from transformers import pipeline
from typing import List, Tuple
from PIL import ImageDraw, Image
import contextlib, io
from pdf2image import convert_from_path

# Device setup
DEVICE = 0 if torch.cuda.is_available() else -1

# Target image canvas size (pixels)
TARGET_SIZE = (800, 600)

def safe_convert(pdf_path: str, dpi: int = 300) -> List[Image.Image]:
    """
    Convert PDF pages to PIL images without printing the Poppler banner.
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        pages = convert_from_path(pdf_path, dpi=dpi)
    return pages

def standardize_images(pil_images: List[Image.Image]) -> List[Image.Image]:
    """
    Resize-and-letterbox every PIL image to TARGET_SIZE,
    returning uniformly-shaped PIL.Image objects.
    """
    standardized = []
    for img in pil_images:
        thumb = img.copy()
        thumb.thumbnail(TARGET_SIZE, Image.LANCZOS)
        canvas = Image.new("RGB", TARGET_SIZE, (0, 0, 0))
        x = (TARGET_SIZE[0] - thumb.width) // 2
        y = (TARGET_SIZE[1] - thumb.height) // 2
        canvas.paste(thumb, (x, y))
        standardized.append(canvas)
    return standardized

# 1) Document-QA (LayoutLMv3)
qa_pipeline = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa",
    framework="pt",
    device=DEVICE,
)

# 2) Code summarization (Salesforce CodeT5)
code_summarizer = pipeline(
    "text2text-generation",
    model="Salesforce/codet5-base-multi-sum",
    framework="pt",
    device=DEVICE,
)

# 3) Layman simplifier (Google FLAN-T5)
layman_simplifier = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    framework="pt",
    device=DEVICE,
)

def extract_best_span(
    std_pages: List[Image.Image],
    question: str,
    pdf_path: str
) -> Tuple[str, Tuple[float, float, float, float], int]:
    """
    Find the best answer span and bbox among standardized pages.
    """
    doc = fitz.open(pdf_path)
    best_span, best_score = "", 0.0
    best_bbox, best_page = None, -1

    for idx, img in enumerate(std_pages):
        try:
            outputs = qa_pipeline(image=img, question=question)
        except ValueError:
            outputs = qa_pipeline(image=img, question=question, doc_stride=0)

        for out in outputs:
            span = out.get("answer", "").strip()
            score = out.get("score", 0.0)
            if not span or score <= best_score:
                continue

            rects = doc[idx].search_for(span)
            if not rects:
                continue

            r = rects[0]
            best_bbox = (r.x0, r.y0, r.x1, r.y1)
            best_span, best_score, best_page = span, score, idx

    doc.close()
    return best_span, best_bbox, best_page

def _is_code(span: str) -> bool:
    tokens = [';', '{', '}', 'def ', 'class ', '->', '<', '>', '=']
    return any(tok in span for tok in tokens)

def get_document_answer_with_highlight(
    pdf_path: str,
    question: str,
    std_pages: List[Image.Image],
    orig_pages: List[Image.Image],
    force_code: bool = False,
    simplify_layman: bool = True
) -> Tuple[str, List[Image.Image], List[Image.Image]]:
    """
    Returns (answer_text, highlighted_images, original_images).
    Uses preloaded std_pages for QA and orig_pages for display.
    """
    span, bbox, page_idx = extract_best_span(std_pages, question, pdf_path)
    if not span or page_idx < 0:
        return "No answer found.", [], orig_pages

    # Refine answer
    if force_code or _is_code(span):
        span = code_summarizer(f"summarize: {span}", max_length=128, num_return_sequences=1)[0]["generated_text"]
    elif simplify_layman:
        span = layman_simplifier(f"Explain in simple terms: {span}", max_length=128, num_return_sequences=1)[0]["generated_text"]

    # Highlight on standardized pages
    highlighted = []
    for idx, img in enumerate(std_pages):
        overlay = img.convert("RGBA")
        draw = ImageDraw.Draw(overlay, "RGBA")
        if idx == page_idx and bbox:
            x0, y0, x1, y1 = bbox
            draw.rectangle([x0, y0, x1, y1], outline=(255,255,0), width=2)
        highlighted.append(overlay.convert("RGB"))

    return span, highlighted, orig_pages