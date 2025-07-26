import re
from collections import Counter

def get_font_stats(pages_data):
    """Analyzes text blocks to find the document's body text style."""
    if not pages_data:
        return 12
    sizes = [block["font_size"] for page in pages_data for block in page["blocks"]]
    if not sizes:
        return 12
    # Find the most common font size
    most_common_size = Counter(sizes).most_common(1)[0][0]
    return most_common_size

def is_bold(font_name):
    """Checks if a font name suggests it is bold."""
    return any(x in font_name.lower() for x in ['bold', 'black', 'heavy', 'oblique'])

def clean_text(text):
    """Cleans up text by removing extra spaces and non-printable chars."""
    return re.sub(r'\s+', ' ', text).strip()

def detect_headings(pages_data):
    """Analyzes text blocks using advanced heuristics to identify a hierarchical outline."""
    if not pages_data:
        return "No Title Found", []

    body_font_size = get_font_stats(pages_data)
    potential_headings = []

    # --- Step 1: Extract potential headings, skipping the first page ---
    for page_num, page in enumerate(pages_data):
        # The first page (index 0) usually contains the title, not headings.
        if page_num == 0:
            continue

        y_positions = [round(block["bbox"][1]) for block in page["blocks"]]
        y_counts = Counter(y_positions)
        
        for block in page["blocks"]:
            text = clean_text(block["text"])
            font_size = block["font_size"]
            y0 = round(block["bbox"][1])

            if not text or font_size <= body_font_size:
                continue
            if y_counts[y0] > 2:
                continue
            if re.search(r'\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b', text.upper()):
                continue
            if len(text) < 3:
                continue
            if re.match(r'^version\s*\d+\.\d+', text, re.IGNORECASE): # Ignore "Version X.Y"
                continue
            if len(text.split()) > 15:
                continue

            if is_bold(block["font_name"]) or font_size > body_font_size + 1:
                potential_headings.append({
                    "text": text,
                    "page": page["page_num"],
                    "font_size": font_size,
                    "bbox": block["bbox"]
                })

    if not potential_headings:
        return "No Title Found", []

    merged_headings = []
    if potential_headings:
        current_heading = potential_headings[0]
        for i in range(1, len(potential_headings)):
            next_heading = potential_headings[i]
            if (next_heading["page"] == current_heading["page"] and
                abs(next_heading["bbox"][1] - current_heading["bbox"][3]) < 10 and
                abs(next_heading["font_size"] - current_heading["font_size"]) < 2):
                current_heading["text"] += " " + next_heading["text"]
            else:
                merged_headings.append(current_heading)
                current_heading = next_heading
        merged_headings.append(current_heading)

    heading_font_sizes = sorted(list(set(h["font_size"] for h in merged_headings)), reverse=True)
    level_map = {size: f"H{i+1}" for i, size in enumerate(heading_font_sizes[:3])}
    
    outline = []
    common_h1_titles = ["table of contents", "revision history", "acknowledgements", "references", "introduction", "syllabus"]

    for heading in merged_headings:
        text = heading["text"]
        level = level_map.get(heading["font_size"], "H3")

        if any(common_title in text.lower() for common_title in common_h1_titles):
            level = "H1"

        match = re.match(r'^\s*(\d+(\.\d+)*)\s*', text)
        if match:
            depth = match.group(1).count('.')
            level = f"H{depth + 1}"
            text = clean_text(text[len(match.group(0)):])
        
        if not text:
            continue
            
        outline.append({"level": level, "text": text, "page": heading["page"], "y": heading["bbox"][1]})

    title = "Overview" # Default title
    if pages_data and pages_data[0]["blocks"]:
        first_page_blocks = sorted([b for b in pages_data[0]["blocks"] if b['text']], key=lambda b: b["font_size"], reverse=True)
        if first_page_blocks:
            title = first_page_blocks[0]["text"]

    final_outline = [item for item in outline if item["text"].lower() != title.lower()]
    final_outline.sort(key=lambda x: (x['page'], x['y']))
    
    for item in final_outline:
        del item['y']

    return title, final_outline
