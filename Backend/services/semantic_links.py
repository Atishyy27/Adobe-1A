import fitz
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_heading_blocks(filepath: str):
    doc = fitz.open(filepath)
    sections = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    text = " ".join([span["text"] for span in line["spans"]]).strip()
                    font_size = line["spans"][0]["size"]

                    if font_size > 12 and len(text) > 5:
                        sections.append({
                            "heading": text,
                            "page": page_num
                        })

    doc.close()
    return sections


def generate_semantic_links(filepath: str, top_k=3):
    sections = extract_heading_blocks(filepath)

    embeddings = [model.encode(s["heading"], convert_to_tensor=True) for s in sections]

    links = []
    for i, sec1 in enumerate(sections):
        related = []
        for j, sec2 in enumerate(sections):
            if i == j:
                continue
            score = util.cos_sim(embeddings[i], embeddings[j]).item()
            if score > 0.5:
                related.append({
                    "source_page": sec1["page"],
                    "source_heading": sec1["heading"],
                    "target_page": sec2["page"],
                    "target_heading": sec2["heading"],
                    "score": round(score, 2)
                })

        related.sort(key=lambda x: x["score"], reverse=True)
        links.extend(related[:top_k])  # Top K related links per section

    return links
