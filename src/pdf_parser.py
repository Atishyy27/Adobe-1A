import fitz  # PyMuPDF
import os

def extract_text_blocks(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return []

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening or processing PDF {pdf_path}: {e}")
        return []

    pages_data = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")['blocks']
        page_blocks = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            page_blocks.append({
                                "text": text,
                                "font_size": round(span["size"]),
                                "font_name": span["font"],
                                "bbox": span["bbox"]
                            })

        pages_data.append({
            "page_num": page_num,
            "blocks": sorted(page_blocks, key=lambda b: (b["bbox"][0], b["bbox"][1]))
        })

    doc.close()
    return pages_data