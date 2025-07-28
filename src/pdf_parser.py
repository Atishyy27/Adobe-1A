# src/pdf_parser.py
import fitz  # PyMuPDF
import os
import re
from collections import Counter

def get_document_fonts(doc):
    """Get a list of unique font names and the most common font in the document."""
    all_fonts = []
    for page_num in range(len(doc)):
        all_fonts.extend(font[3] for font in doc.get_page_fonts(page_num))
    
    if not all_fonts:
        return set(), None
        
    font_counts = Counter(all_fonts)
    most_common_font = font_counts.most_common(1)[0][0]
    return set(all_fonts), most_common_font

def extract_raw_lines(pdf_path):
    """
    Extracts text lines as dictionaries from a PDF, including rich metadata.
    This is the primary data source for feature extraction.
    """
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return None, None, None, None

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ Error opening PDF {pdf_path}: {e}")
        return None, None, None, None

    toc = doc.get_toc()
    unique_fonts, body_font = get_document_fonts(doc)
    
    pages_data = []
    for page_num, page in enumerate(doc, start=1):
        page_dims = {"width": page.rect.width, "height": page.rect.height}
        
        # Using "dict" is the most reliable way to get structured data
        blocks = page.get_text("dict", sort=True)["blocks"]
        page_lines = []
        
        for block in blocks:
            if block['type'] == 0:  # This is a text block
                for line in block["lines"]:
                    # Join spans to correctly reconstruct the full line
                    full_text = " ".join(span['text'] for span in line["spans"]).strip()
                    if not full_text:
                        continue

                    # Consolidate span properties for the entire line
                    font_sizes = [s['size'] for s in line['spans']]
                    fonts = [s['font'] for s in line['spans']]
                    flags = [s['flags'] for s in line['spans']]

                    line_data = {
                        "text": full_text,
                        "font_size": round(max(font_sizes)) if font_sizes else 12,
                        "font_name": max(set(fonts), key=fonts.count) if fonts else "Unknown",
                        "is_bold": any("bold" in f.lower() for f in fonts),
                        "is_italic": any("italic" in f.lower() for f in fonts) or (4 in flags),
                        "bbox": line["bbox"],
                        "page_num": page_num,
                        "page_dims": page_dims,
                    }
                    page_lines.append(line_data)
        pages_data.append(page_lines)
    
    doc.close()
    return pages_data, toc, body_font, unique_fonts