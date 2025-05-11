import os
import tempfile
import pytest
from pathlib import Path
from ai_model import extract_best_span as _extract_best_span, \
                     get_document_answer_with_highlight, \
                     safe_convert, standardize_images


@pytest.fixture
def sample_pdf(tmp_path):
    # small test PDF in tests/resources/test_doc.pdf/ ZAP Generated Report
    src = Path(__file__).parent / "resources" / "test_doc.pdf"
    dst = tmp_path / "test_doc.pdf"
    dst.write_bytes(src.read_bytes())
    return str(dst)


def test_extract_best_span(sample_pdf):
    # prepare standardized pages for the model
    raw_pages = safe_convert(sample_pdf, dpi=300)
    std_pages = standardize_images(raw_pages)

    # simple question with a pre-defined span
    span, bbox, page_idx = _extract_best_span(std_pages, "title", sample_pdf)
    assert isinstance(span, str) and span != ""
    assert isinstance(bbox, tuple) and len(bbox) == 4
    assert isinstance(page_idx, int)


def test_get_document_answer_with_highlight(sample_pdf):
    # prepare original and standardized pages
    orig_pages = safe_convert(sample_pdf, dpi=200)
    std_pages = standardize_images(safe_convert(sample_pdf, dpi=300))

    answer, highlights, returned_orig = get_document_answer_with_highlight(
        pdf_path=sample_pdf,
        question="title",
        std_pages=std_pages,
        orig_pages=orig_pages
    )
    assert isinstance(answer, str)
    assert isinstance(highlights, list) and all(hasattr(p, "size") for p in highlights)
    assert isinstance(returned_orig, list) and all(hasattr(p, "size") for p in returned_orig)