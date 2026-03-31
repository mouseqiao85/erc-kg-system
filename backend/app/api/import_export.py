from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
import csv
import io
from app.core.database import get_db
from app.models.database import Entity, Triple, Project, Document
from app.models import schemas
import uuid

router = APIRouter()


@router.post("/entities/json")
async def import_entities_json(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """从JSON文件导入实体"""
    content = await file.read()
    try:
        data = json.loads(content)
        entities = data if isinstance(data, list) else data.get("entities", [])
        
        imported = 0
        for item in entities:
            entity = Entity(
                id=uuid.uuid4(),
                project_id=project_id,
                name=item.get("name", ""),
                type=item.get("type", "Unknown"),
                confidence=item.get("confidence", 0.8),
                properties=item.get("properties", {})
            )
            db.add(entity)
            imported += 1
        
        db.commit()
        return {"success": True, "imported": imported}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/triples/json")
async def import_triples_json(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """从JSON文件导入三元组"""
    content = await file.read()
    try:
        data = json.loads(content)
        triples = data if isinstance(data, list) else data.get("triples", [])
        
        entity_map = {}
        entities = db.query(Entity).filter(Entity.project_id == project_id).all()
        for e in entities:
            entity_map[e.name] = e.id
        
        imported = 0
        for item in triples:
            head_name = item.get("head", "")
            tail_name = item.get("tail", "")
            
            if head_name not in entity_map:
                head_entity = Entity(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    name=head_name,
                    type="Unknown"
                )
                db.add(head_entity)
                db.flush()
                entity_map[head_name] = head_entity.id
            
            if tail_name not in entity_map:
                tail_entity = Entity(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    name=tail_name,
                    type="Unknown"
                )
                db.add(tail_entity)
                db.flush()
                entity_map[tail_name] = tail_entity.id
            
            triple = Triple(
                id=uuid.uuid4(),
                project_id=project_id,
                head_id=entity_map[head_name],
                relation=item.get("relation", ""),
                tail_id=entity_map[tail_name],
                confidence=item.get("confidence", 0.8)
            )
            db.add(triple)
            imported += 1
        
        db.commit()
        return {"success": True, "imported": imported}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/entities/{project_id}/json")
def export_entities_json(project_id: str, db: Session = Depends(get_db)):
    """导出实体为JSON"""
    entities = db.query(Entity).filter(Entity.project_id == project_id).all()
    
    data = [{
        "id": str(e.id),
        "name": e.name,
        "type": e.type,
        "confidence": e.confidence,
        "properties": e.properties
    } for e in entities]
    
    return {"entities": data, "count": len(data)}


@router.get("/triples/{project_id}/json")
def export_triples_json(project_id: str, db: Session = Depends(get_db)):
    """导出三元组为JSON"""
    triples = db.query(Triple).filter(Triple.project_id == project_id).all()
    
    entity_map = {}
    entities = db.query(Entity).filter(Entity.project_id == project_id).all()
    for e in entities:
        entity_map[str(e.id)] = e.name
    
    data = [{
        "id": str(t.id),
        "head": entity_map.get(str(t.head_id), ""),
        "relation": t.relation,
        "tail": entity_map.get(str(t.tail_id), ""),
        "confidence": t.confidence
    } for t in triples]
    
    return {"triples": data, "count": len(data)}


@router.get("/entities/{project_id}/csv")
def export_entities_csv(project_id: str, db: Session = Depends(get_db)):
    """导出实体为CSV"""
    entities = db.query(Entity).filter(Entity.project_id == project_id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "type", "confidence"])
    
    for e in entities:
        writer.writerow([str(e.id), e.name, e.type or "", e.confidence or ""])
    
    return {"data": output.getvalue(), "format": "csv"}


@router.get("/triples/{project_id}/csv")
def export_triples_csv(project_id: str, db: Session = Depends(get_db)):
    """导出三元组为CSV"""
    triples = db.query(Triple).filter(Triple.project_id == project_id).all()
    
    entity_map = {}
    entities = db.query(Entity).filter(Entity.project_id == project_id).all()
    for e in entities:
        entity_map[str(e.id)] = e.name
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["head", "relation", "tail", "confidence"])
    
    for t in triples:
        writer.writerow([
            entity_map.get(str(t.head_id), ""),
            t.relation,
            entity_map.get(str(t.tail_id), ""),
            t.confidence or ""
        ])
    
    return {"data": output.getvalue(), "format": "csv"}
