from transformers import pipeline

# Load the CodeBERT model for text generation
print("Loading model...")
model = pipeline("text-generation", model="microsoft/codebert-base", device=-1)

def get_response(user_input):
    """Generate a response using the CodeBERT model."""
    try:
        response = model(user_input, max_length=50, num_return_sequences=1)
        return response[0]['generated_text']
    except Exception as e:
        return f"Error: {str(e)}"
