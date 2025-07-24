import fitz  # PyMuPDF

def get_document_structure(file_path: str) -> dict:
    """
    Processes a single PDF file and returns its structured outline (title + H1/H2/H3 headings).
    """
    doc = fitz.open(file_path)
    title = doc.metadata.get("title") or "Untitled"
    outline = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    text = " ".join([span["text"] for span in line["spans"]]).strip()
                    font_size = line["spans"][0]["size"]
                    font_flags = line["spans"][0]["flags"]  # Flags can tell bold/italic
                    
                    # Optional: Use flags to ensure we skip regular body text
                    is_bold = bool(font_flags & 2)

                    if not text or len(text) < 5:
                        continue
                    
                    # Heading heuristics
                    if font_size > 15:
                        outline.append({"level": "H1", "text": text, "page": page_num})
                    elif 12 < font_size <= 15 and is_bold:
                        outline.append({"level": "H2", "text": text, "page": page_num})
                    elif 10 < font_size <= 12 and is_bold:
                        outline.append({"level": "H3", "text": text, "page": page_num})

    doc.close()

    return {
        "title": title,
        "outline": outline
    }
