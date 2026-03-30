from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import schemas
from app.models.database import Document, Project
import uuid
import os
import aiofiles

router = APIRouter()

UPLOAD_DIR = "backend/uploads"


@router.post("", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    project_id: str = None,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    file_ext = file.filename.split(".")[-1]
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_ext}")
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    doc = Document(
        id=uuid.UUID(file_id),
        project_id=uuid.UUID(project_id),
        title=file.filename,
        format=file_ext,
        file_path=file_path,
        status="pending"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return doc


@router.get("", response_model=dict)
def get_documents(
    project_id: str = None,
    page: int = 1,
    size: int = 20,
    status: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    
    if project_id:
        query = query.filter(Document.project_id == project_id)
    if status:
        query = query.filter(Document.status == status)
    
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return {
        "total": total,
        "items": items
    }


@router.get("/{doc_id}", response_model=schemas.DocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    
    db.delete(doc)
    db.commit()
    
    return {"success": True}
