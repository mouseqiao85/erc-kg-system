from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models import schemas
from app.models.database import Job, Project, Document, Entity, Triple
from app.services.tasks import build_knowledge_graph
import uuid

router = APIRouter()


@router.post("", response_model=dict)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == job.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_job = Job(
        id=uuid.uuid4(),
        project_id=job.project_id,
        type="graph_build",
        status="pending",
        config=job.config.model_dump()
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    build_knowledge_graph.delay(str(db_job.id), str(project.id), job.config.model_dump())
    
    return {"job_id": str(db_job.id), "status": db_job.status}


@router.get("", response_model=dict)
def get_jobs(
    project_id: str = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    if project_id:
        query = query.filter(Job.project_id == project_id)
    
    total = query.count()
    items = query.order_by(Job.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return {"total": total, "items": items}


@router.get("/{job_id}", response_model=schemas.JobStatusResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    entities_count = db.query(Entity).filter(Entity.project_id == job.project_id).count()
    triples_count = db.query(Triple).filter(Triple.project_id == job.project_id).count()
    
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step,
        "stats": {
            "entities": entities_count,
            "triples": triples_count
        }
    }
