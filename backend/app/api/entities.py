from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.models import schemas
from app.models.database import Entity
import uuid

router = APIRouter()


@router.get("", response_model=dict)
def get_entities(
    project_id: str = None,
    keyword: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Entity)
    
    if project_id:
        query = query.filter(Entity.project_id == project_id)
    if keyword:
        query = query.filter(Entity.name.ilike(f"%{keyword}%"))
    
    items = query.limit(limit).all()
    return {"items": items}


@router.post("", response_model=schemas.EntityResponse)
def create_entity(entity: schemas.EntityCreate, db: Session = Depends(get_db)):
    db_entity = Entity(
        id=uuid.uuid4(),
        project_id=entity.project_id,
        source_id=entity.source_id,
        name=entity.name,
        type=entity.type,
        confidence=entity.confidence
    )
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


@router.get("/{entity_id}", response_model=schemas.EntityResponse)
def get_entity(entity_id: str, db: Session = Depends(get_db)):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.delete("/{entity_id}")
def delete_entity(entity_id: str, db: Session = Depends(get_db)):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    db.delete(entity)
    db.commit()
    return {"success": True}
