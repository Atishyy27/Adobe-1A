import fitz  # PyMuPDF

def get_document_structure(file_path: str) -> dict:
    doc = fitz.open(file_path)
    title = doc.metadata.get("title") or "Untitled"
    outline = []

    font_sizes = set()
    all_spans = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text or len(text) < 3:
                        continue

                    font_size = span["size"]
                    font_flags = span["flags"]
                    is_bold = bool(font_flags & 2)

                    font_sizes.add(font_size)
                    all_spans.append({
                        "page": page_num,
                        "text": text,
                        "font_size": font_size,
                        "is_bold": is_bold
                    })

    doc.close()

    # Sort unique font sizes to assign H1, H2, H3 levels
    sorted_sizes = sorted(font_sizes, reverse=True)
    size_to_level = {}

    if len(sorted_sizes) >= 3:
        size_to_level = {
            sorted_sizes[0]: "H1",
            sorted_sizes[1]: "H2",
            sorted_sizes[2]: "H3"
        }
    elif len(sorted_sizes) == 2:
        size_to_level = {
            sorted_sizes[0]: "H1",
            sorted_sizes[1]: "H2"
        }
    elif len(sorted_sizes) == 1:
        size_to_level = {
            sorted_sizes[0]: "H1"
        }

    # Build outline using detected font sizes
    seen = set()
    for span in all_spans:
        size = span["font_size"]
        text = span["text"]
        page = span["page"]

        # Prevent duplicates
        key = (text.lower(), page)
        if key in seen:
            continue
        seen.add(key)

        if size in size_to_level:
            outline.append({
                "level": size_to_level[size],
                "text": text,
                "page": page
            })

    return {
        "title": title,
        "outline": outline
    }
