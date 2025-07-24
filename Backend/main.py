# --- Standard Library Imports ---
import shutil
from pathlib import Path
from datetime import datetime
from typing import List

# --- Third-party Imports ---
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Body
from sqlalchemy.orm import Session

# --- Local Application Imports ---
from Backend.services import structuring, insights
from Backend.db import models, session as db_session
from Backend.services import semantic_links


# --- DB Initialization ---
models.Base.metadata.create_all(bind=db_session.engine)

# --- FastAPI App Initialization ---
app = FastAPI(title="Insight Nexus API")

# Directory to store uploaded files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# --- Route: Upload PDF ---
@app.post("/docs/upload")
def upload_pdf(file: UploadFile = File(...), db: Session = Depends(db_session.get_db)):
    """
    Uploads a PDF, stores it on disk, and saves metadata to the database.
    """
    filepath = UPLOAD_DIR / file.filename

    with filepath.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_document = models.Document(filename=file.filename, filepath=str(filepath))
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return {"doc_id": db_document.id, "filename": db_document.filename}


# --- Route: Get PDF Structure ---
@app.get("/docs/{doc_id}/structure")
def get_structure(doc_id: int, db: Session = Depends(db_session.get_db)):
    """
    Returns structured outline (title, H1/H2/H3) of a document by its ID.
    """
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    try:
        structure_data = structuring.get_document_structure(document.filepath)
        return structure_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PDF file not found on server.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# --- Route: Persona-Based Insight Search ---
@app.post("/insights/search")
def search_insights(
    doc_ids: List[int] = Body(...),
    persona: str = Body(...),
    job_to_be_done: str = Body(...),
    db: Session = Depends(db_session.get_db)
):
    """
    Extracts and ranks relevant sections from documents based on persona and job.
    """
    all_ranked = []

    for doc_id in doc_ids:
        document = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if not document:
            continue

        sections = insights.extract_sections_with_text(document.filepath)
        ranked = insights.rank_sections(sections, job_to_be_done, document.filename)
        all_ranked.extend(ranked)

    all_ranked = sorted(all_ranked, key=lambda x: x["relevance_score"], reverse=True)

    return {
        "metadata": {
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "query_time": datetime.utcnow().isoformat()
        },
        "results": all_ranked[:10]  # Return top 10 insights
    }
# Route to generate semantic links between sections of a document
@app.get("/docs/{doc_id}/semantic-links")
def get_semantic_links(doc_id: int, db: Session = Depends(db_session.get_db)):
    """
    Generates semantically related sections for a document.
    """
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    try:
        links = semantic_links.generate_semantic_links(document.filepath)
        return {
            "document_id": document.filename,
            "links": links
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

