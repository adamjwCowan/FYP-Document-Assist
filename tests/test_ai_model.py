import pytest
from ai_model import get_document_answer

# Test that get_document_answer handles non-existent PDF paths gracefully
def test_get_document_answer_nonexistent(tmp_path):
    # Dummy path that does not exist
    fake_pdf = tmp_path / "does_not_exist.pdf"
    # Call the function with the fake path
    answer = get_document_answer(str(fake_pdf), "What is X?")
    # The function returns an error message indicating processing failure
    assert "Error processing document" in answer