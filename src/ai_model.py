from transformers import pipeline

# Initialize the document question-answering pipeline using the fine-tuned model
document_qa = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa"
)

def get_document_answer(image, question):
    """
    Given a PIL image (a page of a document) and a question,
    returns the answer from the document.
    """
    try:
        result = document_qa(image, question)
        return result.get("answer", "No answer found.")
    except Exception as e:
        return f"Error processing document: {str(e)}" 