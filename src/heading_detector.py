import re
from collections import Counter

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def is_bold(font_name):
    return any(x in font_name.lower() for x in ['bold', 'black', 'heavy', 'medium', 'demi'])

def get_body_font_size(pages_data):
    sizes = [block["font_size"] for page in pages_data for block in page["blocks"]]
    return Counter(sizes).most_common(1)[0][0] if sizes else 12

def detect_headings(pages_data):
    if not pages_data:
        return "No Title Found", []

    body_font_size = get_body_font_size(pages_data)
    potential_headings = []

    for page in pages_data[1:]:
        y_positions = [round(b["bbox"][1]) for b in page["blocks"]]
        y_counts = Counter(y_positions)

        for block in page["blocks"]:
            text = clean_text(block["text"])
            font_size = block["font_size"]
            y0 = round(block["bbox"][1])

            is_semantic = text.endswith(":") or text.istitle()

            if not text or font_size <= body_font_size:
                continue
            if y_counts[y0] > 2:
                continue
            if re.search(r'\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b', text.upper()):
                continue
            if len(text) < 3 or len(text.split()) > 25:
                continue
            if re.match(r'^version\s*\d+\.\d+', text, re.IGNORECASE):
                continue

            if is_semantic or is_bold(block["font_name"]) or font_size > body_font_size + 1:
                potential_headings.append({
                    "text": text,
                    "page": page["page_num"],
                    "font_size": font_size,
                    "bbox": block["bbox"]
                })

    # Merge multiline headings
    merged = []
    temp = []

    def flush():
        if temp:
            merged.append({
                "text": ' '.join([x["text"] for x in temp]),
                "page": temp[0]["page"],
                "font_size": temp[0]["font_size"],
                "bbox": temp[0]["bbox"]
            })
            temp.clear()

    for heading in potential_headings:
        if not temp:
            temp.append(heading)
        else:
            prev = temp[-1]
            close = abs(heading["bbox"][1] - prev["bbox"][3]) < 25
            same_page = heading["page"] == prev["page"]
            similar_font = abs(heading["font_size"] - prev["font_size"]) <= 1
            if same_page and close and similar_font:
                temp.append(heading)
            else:
                flush()
                temp.append(heading)
    flush()

    # Assign heading levels
    font_sizes = sorted({h["font_size"] for h in merged}, reverse=True)
    level_map = {size: f"H{i+1}" for i, size in enumerate(font_sizes)}

    outline = []
    for h in merged:
        level = level_map.get(h["font_size"], "H3")
        text = h["text"]

        if re.match(r'^\s*\d+(\.\d+)*\s+', text):
            depth = text.split()[0].count('.')
            level = f"H{min(depth + 1, 3)}"
            text = clean_text(re.sub(r'^\s*\d+(\.\d+)*\s+', '', text))

        outline.append({
            "level": level,
            "text": text,
            "page": h["page"],
            "y": h["bbox"][1]
        })

    title = "Overview"
    if pages_data[0]["blocks"]:
        sorted_blocks = sorted(pages_data[0]["blocks"], key=lambda b: b["font_size"], reverse=True)
        title = clean_text(sorted_blocks[0]["text"])

    final_outline = [h for h in outline if h["text"].lower() != title.lower()]
    final_outline.sort(key=lambda x: (x["page"], x["y"]))
    for h in final_outline:
        h.pop("y", None)

    return title, final_outline