import os
import tempfile
import pytest
from pathlib import Path
from ai_model import _extract_best_span, get_document_answer_with_highlight


@pytest.fixture
def sample_pdf(tmp_path):
    # small test PDF in tests/resources/test_doc.pdf/ ZAP Generated Report
    src = Path(__file__).parent / "resources" / "test_doc.pdf"
    dst = tmp_path / "test_doc.pdf"
    dst.write_bytes(src.read_bytes())
    return str(dst)

def test_extract_best_span(sample_pdf):
    # simple question with a pre-defined span
    span, bbox, page, dims = _extract_best_span(sample_pdf, "title")
    assert isinstance(span, str) and span != ""
    assert isinstance(bbox, tuple) and len(bbox) == 4
    assert isinstance(page, int)
    assert isinstance(dims, tuple) and len(dims) == 2

def test_get_document_answer_with_highlight(sample_pdf):
    answer, pages = get_document_answer_with_highlight(sample_pdf, "title")
    assert isinstance(answer, str)
    assert isinstance(pages, list) and all(hasattr(p, "size") for p in pages)