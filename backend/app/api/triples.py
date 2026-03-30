from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import schemas
from app.models.database import Triple, Entity
import uuid

router = APIRouter()


@router.get("", response_model=dict)
def get_triples(
    project_id: str = None,
    head: str = None,
    relation: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Triple).join(Entity, Triple.head_id == Entity.id)
    
    if project_id:
        query = query.filter(Triple.project_id == project_id)
    if head:
        query = query.filter(Entity.name == head)
    if relation:
        query = query.filter(Triple.relation == relation)
    
    items = query.limit(limit).all()
    
    result = []
    for t in items:
        head_entity = db.query(Entity).filter(Entity.id == t.head_id).first()
        tail_entity = db.query(Entity).filter(Entity.id == t.tail_id).first()
        result.append({
            "id": str(t.id),
            "head": head_entity.name if head_entity else "",
            "relation": t.relation,
            "tail": tail_entity.name if tail_entity else "",
            "confidence": t.confidence,
            "valid": t.valid,
            "project_id": str(t.project_id),
            "created_at": t.created_at.isoformat() if t.created_at else None
        })
    
    return {"items": result}


@router.post("", response_model=schemas.TripleResponse)
def create_triple(triple: schemas.TripleCreate, db: Session = Depends(get_db)):
    head_entity = db.query(Entity).filter(Entity.name == triple.head, Entity.project_id == triple.project_id).first()
    tail_entity = db.query(Entity).filter(Entity.name == triple.tail, Entity.project_id == triple.project_id).first()
    
    if not head_entity:
        head_entity = Entity(
            id=uuid.uuid4(),
            project_id=triple.project_id,
            name=triple.head
        )
        db.add(head_entity)
    
    if not tail_entity:
        tail_entity = Entity(
            id=uuid.uuid4(),
            project_id=triple.project_id,
            name=triple.tail
        )
        db.add(tail_entity)
    
    db.commit()
    db.refresh(head_entity)
    db.refresh(tail_entity)
    
    db_triple = Triple(
        id=uuid.uuid4(),
        project_id=triple.project_id,
        source_id=triple.source_id,
        head_id=head_entity.id,
        relation=triple.relation,
        tail_id=tail_entity.id,
        valid=True
    )
    db.add(db_triple)
    db.commit()
    db.refresh(db_triple)
    
    db_triple.head = head_entity.name
    db_triple.tail = tail_entity.name
    return db_triple


@router.delete("/{triple_id}")
def delete_triple(triple_id: str, db: Session = Depends(get_db)):
    triple = db.query(Triple).filter(Triple.id == triple_id).first()
    if not triple:
        raise HTTPException(status_code=404, detail="Triple not found")
    db.delete(triple)
    db.commit()
    return {"success": True}
