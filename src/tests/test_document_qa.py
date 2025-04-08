import pytest
from transformers import pipeline
from PIL import Image, ImageDraw

# Fixture to create a dummy document image
@pytest.fixture(scope="module")
def dummy_document():
    # Create a white background image
    image = Image.new("RGB", (800, 1000), color="white")
    draw = ImageDraw.Draw(image)
    text = "This is a sample document.\nIt is used to test the document question answering model."
    draw.text((50, 50), text, fill="black")
    return image

# Fixture to load the document QA pipeline
@pytest.fixture(scope="module")
def document_qa_pipeline():
    print("Loading model...")
    nlp = pipeline("document-question-answering", model="impira/layoutlm-document-qa")
    print("Model loaded successfully.")
    return nlp

# Test to check that the model returns a valid answer
def test_document_qa(document_qa_pipeline, dummy_document):
    question = "What is the document used for?"
    result = document_qa_pipeline(dummy_document, question)
    
    # Check if the result is a non-empty list
    assert isinstance(result, list) and len(result) > 0, "The result should be a non-empty list."
    
    # Access the first answer in the list
    answer_dict = result[0]
    
    # Check if the answer dictionary contains the 'answer' key
    assert "answer" in answer_dict, "The answer dictionary should contain the 'answer' key."
    
    answer = answer_dict["answer"]
    
    # Assert that the answer is non-empty
    assert answer != "", "The model should return a non-empty answer."
    print("Answer:", answer)
