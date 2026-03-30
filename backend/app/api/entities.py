from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.models import schemas
from app.models.database import Entity
from app.core.milvus_client import milvus_client
from app.core.config import settings
import uuid

router = APIRouter()

embedding_model = None


def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except Exception as e:
            print(f"Failed to load embedding model: {e}")
    return embedding_model


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


@router.get("/search/semantic")
def semantic_search(
    query: str,
    project_id: str = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """语义搜索实体"""
    model = get_embedding_model()
    if not model:
        raise HTTPException(status_code=500, detail="Embedding model not available")
    
    query_embedding = model.encode([query]).tolist()[0]
    
    collection_name = f"entities_{project_id}" if project_id else "entities"
    
    try:
        if not milvus_client.connected:
            milvus_client.connect()
        
        if not milvus_client.list_collections() or collection_name not in milvus_client.list_collections():
            return {"items": [], "message": "Collection not found"}
        
        results = milvus_client.search(
            collection_name,
            query_embedding,
            top_k=limit
        )
        
        return {"items": results}
    except Exception as e:
        return {"items": [], "error": str(e)}
