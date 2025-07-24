# backend/main.py

# --- Standard Library Imports ---
import shutil
from pathlib import Path

# --- Third-party Imports ---
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session

# --- Local Application Imports ---
# Make sure your folder structure is:
# Backend/
#  |- main.py
#  |- __init__.py
#  |
#  └───services/
#  |    |- structuring.py
#  |    |- __init__.py
#  |
#  └───db/
#       |- models.py
#       |- session.py
#       |- __init__.py
#
# The imports below assume this structure.

# from .services import structuring
# from .db import models, session as db_session
# Corrected absolute imports
from Backend.services import structuring
from Backend.db import models, session as db_session

# This line creates the database tables if they don't exist
# It should be run once when the application starts
models.Base.metadata.create_all(bind=db_session.engine)

# --- FastAPI App Initialization ---
app = FastAPI(title="Insight Nexus API")

# Define the directory to store uploaded files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# --- API Endpoints ---

@app.post("/docs/upload")
def upload_pdf(file: UploadFile = File(...), db: Session = Depends(db_session.get_db)):
    """
    Handles uploading a PDF file, saving it to the server,
    and creating a record in the database.
    """
    filepath = UPLOAD_DIR / file.filename
    
    with filepath.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_document = models.Document(filename=file.filename, filepath=str(filepath))
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return {"doc_id": db_document.id, "filename": db_document.filename}


@app.get("/docs/{doc_id}/structure")
def get_structure(doc_id: int, db: Session = Depends(db_session.get_db)):
    """
    Retrieves the structured outline of a specific document
    by its ID.
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