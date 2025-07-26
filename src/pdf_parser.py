import fitz  # PyMuPDF
import os

def extract_text_blocks(pdf_path):
    """
    Extracts all text blocks from a PDF file along with their metadata.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return []

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening or processing PDF {pdf_path}: {e}")
        return []

    pages_data = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        page_blocks = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Ignore empty or whitespace-only text
                        if span["text"].strip():
                            page_blocks.append({
                                "text": span["text"].strip(),
                                "font_size": round(span["size"]),
                                "font_name": span["font"],
                                "bbox": span["bbox"]
                            })
        
        pages_data.append({
            "page_num": page_num,
            "blocks": page_blocks
        })

    doc.close()
    return pages_data