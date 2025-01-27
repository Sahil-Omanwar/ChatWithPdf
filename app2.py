import os
import requests
from PyPDF2 import PdfReader

# Configuration
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

MISTRAL_API_KEY =   # Replace with your Mistral API key

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a single PDF file using PyPDF2.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def extract_text_from_multiple_pdfs(pdf_paths):
    """
    Extracts and combines text from multiple PDF files.
    """
    combined_text = ""
    for pdf_path in pdf_paths:
        print(f"Extracting text from {pdf_path}...")
        text = extract_text_from_pdf(pdf_path)
        if text:
            combined_text += f"\n\n--- Content from {pdf_path} ---\n\n{text}"
        else:
            print(f"Failed to extract text from {pdf_path}.")
    return combined_text

def query_mistral_api(prompt, context):
    """
    Sends a query to the Mistral API with the given prompt and combined context.
    """
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-large-latest",  # Replace with your Mistral model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context: {context} \n\n Question: {prompt}"},
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }

    try:
        response = requests.post(MISTRAL_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error querying Mistral API: {e}")
        return None

def main():
    # Get the PDF file paths from the user
    pdf_paths = input("Enter the paths to the PDF files (comma-separated): ").strip().split(",")
    pdf_paths = [path.strip() for path in pdf_paths if path.strip()]

    # Check if the provided files exist
    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            return

    # Extract text from the PDFs
    print("Extracting text from the provided PDFs...")
    combined_text = extract_text_from_multiple_pdfs(pdf_paths)
    if not combined_text:
        print("Failed to extract text from all PDFs.")
        return

    print("PDF text extracted and combined successfully.")

    # Start a loop to handle user queries
    while True:
        user_query = input("\nAsk a question (or type 'exit' to quit): ").strip()
        if user_query.lower() == "exit":
            print("Exiting... Goodbye!")
            break

        # Query the Mistral API with the user's question and combined PDF context
        response = query_mistral_api(user_query, combined_text)
        if response:
            print("\nResponse:")
            print(response)
        else:
            print("Failed to get a response from the Mistral API.")

if __name__ == "__main__":
    main()
