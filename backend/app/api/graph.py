from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import schemas
from app.models.database import Entity, Triple, Project
from app.core.neo4j_client import get_neo4j_driver
import uuid

router = APIRouter()


@router.get("", response_model=schemas.GraphResponse)
def get_graph(
    project_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    entities = db.query(Entity).filter(Entity.project_id == project_id).limit(limit).all()
    
    entity_ids = [e.id for e in entities]
    triples = db.query(Triple).filter(
        Triple.head_id.in_(entity_ids),
        Triple.tail_id.in_(entity_ids)
    ).all()
    
    entity_map = {str(e.id): e for e in entities}
    
    nodes = [
        schemas.GraphNode(
            id=str(e.id),
            label=e.name,
            type=e.type or "Entity"
        )
        for e in entities
    ]
    
    edges = []
    for t in triples:
        head = entity_map.get(str(t.head_id))
        tail = entity_map.get(str(t.tail_id))
        if head and tail:
            edges.append(schemas.GraphEdge(
                source=str(t.head_id),
                target=str(t.tail_id),
                label=t.relation
            ))
    
    return schemas.GraphResponse(nodes=nodes, edges=edges)


@router.get("/subgraph", response_model=schemas.GraphResponse)
def get_subgraph(
    entity_id: str,
    depth: int = 2,
    db: Session = Depends(get_db)
):
    return schemas.GraphResponse(nodes=[], edges=[])


@router.post("/cypher", response_model=dict)
def query_cypher(req: schemas.CypherQueryRequest):
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(req.query)
        records = [dict(record) for record in result]
    return {"results": records, "count": len(records)}
