from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import schemas
from app.models.database import Document, Project
from app.services.document_parser import DocumentParser
import uuid
import os
import aiofiles

router = APIRouter()

UPLOAD_DIR = "backend/uploads"


@router.post("", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    project_id: str = None,
    parse: bool = True,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    file_ext = file.filename.split(".")[-1].lower()
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_ext}")
    
    content = await file.read()
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    document_content = ""
    status = "pending"
    
    if parse:
        try:
            document_content = DocumentParser.parse_from_content(content, file_ext)
            if document_content:
                status = "completed"
            else:
                status = "failed"
        except Exception as e:
            print(f"Parse error: {e}")
            status = "failed"
    
    doc = Document(
        id=uuid.UUID(file_id),
        project_id=uuid.UUID(project_id),
        title=file.filename,
        format=file_ext,
        file_path=file_path,
        content=document_content,
        status=status
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return doc


@router.post("/{doc_id}/parse")
async def parse_document(doc_id: str, db: Session = Depends(get_db)):
    """重新解析文档"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not doc.file_path or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=400, detail="File not found")
    
    try:
        content = DocumentParser.parse(doc.file_path)
        doc.content = content
        doc.status = "completed" if content else "failed"
        db.commit()
        db.refresh(doc)
        return {"success": True, "content_length": len(content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
