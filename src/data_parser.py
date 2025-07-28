# src/data_parser.py

import fitz  # PyMuPDF
from typing import List, Dict, Any

def get_document_title(doc: fitz.Document, scan_pages: int) -> str:
    """
    Extracts the document title using heuristics on the first few pages.
    """
    title = doc.metadata.get('title', '')
    max_font_size = 0
    
    # Heuristic: Largest font size on the first few pages is likely the title
    for page_num in range(min(len(doc), scan_pages)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict", sort=True)["blocks"]
        for block in blocks:
            if block['type'] == 0: # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span['size'] > max_font_size:
                            max_font_size = span['size']
                            title = span['text'].strip()
    
    # Clean up title
    if title:
        title = ' '.join(title.split())
    else:
        title = "Untitled Document" # Fallback
        
    return title

def extract_text_blocks(pdf_path: str) -> List]:
    """
    Parses a PDF and extracts a list of structured text blocks.
    Each block contains its text, font properties, and location.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening or processing {pdf_path}: {e}")
        return, "Untitled Document"

    all_blocks =
    
    # First, get the document title
    doc_title = get_document_title(doc, 2)

    for page_num, page in enumerate(doc):
        page_width = page.rect.width
        page_height = page.rect.height
        
        blocks = page.get_text("dict", sort=True)["blocks"]
        for block_idx, block in enumerate(blocks):
            if block['type'] == 0 and 'lines' in block: # It's a text block
                # Consolidate block properties
                block_text =
                span_sizes =
                span_fonts =
                
                for line in block['lines']:
                    line_text = " ".join(span['text'] for span in line['spans']).strip()
                    block_text.append(line_text)
                    for span in line['spans']:
                        span_sizes.append(span['size'])
                        span_fonts.append(span['font'])
                
                if not block_text or not span_sizes:
                    continue

                full_block_text = " ".join(block_text)
                
                # Use the most frequent (mode) font size and name for the block
                mode_size = max(set(span_sizes), key=span_sizes.count)
                mode_font = max(set(span_fonts), key=span_fonts.count)

                all_blocks.append({
                    'block_id': f"{page_num+1}_{block_idx}",
                    'text': full_block_text,
                    'font_size': mode_size,
                    'font_name': mode_font,
                    'bbox': block['bbox'],
                    'page_num': page_num + 1,
                    'page_width': page_width,
                    'page_height': page_height
                })

    doc.close()
    return all_blocks, doc_title