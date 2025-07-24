# backend/services/structuring.py
import fitz # Or your preferred PDF library from Round 1
import re

# Your existing logic for identifying headings goes here
# ...

def get_document_structure(file_path: str) -> dict:
    """
    Processes a single PDF file and returns its structured outline.
    This function contains your core logic from Round 1A.
    """
    doc = fitz.open(file_path)
    title = doc.metadata.get("title") or "Untitled"
    outline = []

    # Your loop to go through pages and extract headings
    for page_num, page in enumerate(doc, start=1):
        # ... your heading extraction logic ...
        # Example:
        # if is_heading(text):
        #     outline.append({"level": "H1", "text": "...", "page": page_num})
        pass # Replace with your actual implementation

    # The output must match the required JSON format from the challenge [cite: 43]
    return {
        "title": title,
        "outline": outline
    }