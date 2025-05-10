import os
import torch
import fitz                     # PyMuPDF for PDF operations
from pdf2image import convert_from_path
from transformers import pipeline
from typing import List, Tuple
from PIL import ImageDraw

# Device setup for all pipelines
device = 0 if torch.cuda.is_available() else -1

# 1) Document-QA (LayoutLMv3)
qa_pipeline = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa",
    framework="pt",
    device=device,
)

# 2) Code summarization (Salesforce CodeT5)
code_summarizer = pipeline(
    "text2text-generation",
    model="Salesforce/codet5-base-multi-sum",
    framework="pt",
    device=device,
)

# 3) Layman simplifier (Google FLAN-T5)
layman_simplifier = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    framework="pt",
    device=device,
)

def _extract_best_span(
    pdf_path: str,
    question: str
) -> Tuple[str, Tuple[float, float, float, float], int, Tuple[float, float]]:
    """
    Find the top answer span in a PDF and its bounding box.
    Returns: (span, bbox_pts, page_idx, (width_pts, height_pts))
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Render pages at 300 DPI for QA clarity
    pil_pages = convert_from_path(pdf_path, dpi=300)
    doc = fitz.open(pdf_path)

    best_span, best_score = "", 0.0
    best_bbox, best_page = None, -1
    page_dims = (0.0, 0.0)

    for idx, img in enumerate(pil_pages):
        try:
            outputs = qa_pipeline(image=img, question=question)
        except ValueError:
            # Fallback for ragged-mask bug
            outputs = qa_pipeline(image=img, question=question, doc_stride=0)

        for out in outputs:
            span = out.get("answer", "").strip()
            score = out.get("score", 0.0)
            if not span or score <= best_score:
                continue

            rects = doc[idx].search_for(span)
            if not rects:
                continue

            # Convert Fitz Rect into simple tuple
            r = rects[0]
            best_bbox = (r.x0, r.y0, r.x1, r.y1)

            best_span, best_score = span, score
            best_page = idx
            page_dims = (doc[idx].rect.width, doc[idx].rect.height)

    doc.close()
    return best_span, best_bbox, best_page, page_dims


def _is_code(span: str) -> bool:
    """
    Simple heuristic: detect code by common symbols.
    """
    tokens = [';', '{', '}', 'def ', 'class ', '->', '<', '>', '=']
    return any(tok in span for tok in tokens)


def get_document_answer_with_highlight(
    pdf_path: str,
    question: str,
    force_code: bool = False,
    simplify_layman: bool = True
) -> Tuple[str, List]:
    """
    1) Extract best span + location
    2) Summarize as code or simplify
    3) Highlight span on pages
    """
    try:
        span, bbox, page_idx, _ = _extract_best_span(pdf_path, question)
    except Exception as e:
        return f"Error: {e}", []

    if not span or page_idx < 0:
        return "No answer found.", []

    # Apply summarization or simplification
    if force_code or _is_code(span):
        span = code_summarizer(f"summarize: {span}", max_length=128, num_return_sequences=1)[0]["generated_text"]
    elif simplify_layman:
        span = layman_simplifier(f"Explain in simple terms: {span}", max_length=128, num_return_sequences=1)[0]["generated_text"]

    # Highlight on images
    pil_pages = convert_from_path(pdf_path, dpi=300)
    highlighted = []
    scale = 300 / 72.0  # points to pixels

    for idx, img in enumerate(pil_pages):
        overlay = img.convert("RGBA")
        draw = ImageDraw.Draw(overlay, "RGBA")
        if idx == page_idx and bbox:
            x0, y0, x1, y1 = bbox
            draw.rectangle([x0*scale, y0*scale, x1*scale, y1*scale], outline=(255,255,0), width=2)
        highlighted.append(overlay.convert("RGB"))

    return span, highlighted