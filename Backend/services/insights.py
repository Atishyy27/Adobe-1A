from sentence_transformers import SentenceTransformer, util
import fitz  # PyMuPDF
from datetime import datetime

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_sections_with_text(filepath: str):
    """
    Extract heading + short text chunks under headings.
    """
    doc = fitz.open(filepath)
    sections = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    text = " ".join([span["text"] for span in line["spans"]]).strip()
                    font_size = line["spans"][0]["size"]

                    if not text or len(text) < 5:
                        continue
                    
                    # Heuristic heading detection
                    if font_size > 12:
                        section_text = page.get_text().strip()
                        sections.append({
                            "section_title": text,
                            "page_number": page_num,
                            "text": section_text  # Later can slice by heading range
                        })
    doc.close()
    return sections
def compute_relevance_score(section_text: str, job_text: str):
    emb_section = model.encode(section_text, convert_to_tensor=True)
    emb_job = model.encode(job_text, convert_to_tensor=True)
    similarity = util.cos_sim(emb_section, emb_job)
    return float(similarity)

def rank_sections(sections: list, job_text: str, filename: str):
    for sec in sections:
        sec["relevance_score"] = compute_relevance_score(sec["text"], job_text)
        sec["document_id"] = filename

    sorted_sections = sorted(sections, key=lambda x: x["relevance_score"], reverse=True)

    for idx, sec in enumerate(sorted_sections, start=1):
        sec["importance_rank"] = idx
        sec.pop("text")  # Don't return full text

    return sorted_sections[:5]  # Return top 5
