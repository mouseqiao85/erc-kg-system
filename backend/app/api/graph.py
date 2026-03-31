from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import schemas
from app.models.database import Entity, Triple, Project
from app.core.neo4j_client import get_neo4j_driver
from app.core.config import settings
from openai import OpenAI
import uuid

router = APIRouter()

llm_client = None


def get_llm_client():
    global llm_client
    if llm_client is None and settings.llm_api_key:
        llm_client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url
        )
    return llm_client


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


@router.post("/natural", response_model=dict)
def natural_query(req: schemas.NaturalQueryRequest, db: Session = Depends(get_db)):
    """自然语言查询"""
    client = get_llm_client()
    if not client:
        raise HTTPException(status_code=500, detail="LLM not configured")
    
    project_id = req.question.get("project_id") if isinstance(req.question, dict) else None
    question = req.question.get("question") if isinstance(req.question, dict) else req.question
    
    if project_id:
        entities = db.query(Entity).filter(Entity.project_id == project_id).limit(50).all()
    else:
        entities = db.query(Entity).limit(50).all()
    
    entity_list = [{"name": e.name, "type": e.type} for e in entities]
    
    if project_id:
        triples = db.query(Triple).filter(Triple.project_id == project_id).limit(100).all()
    else:
        triples = db.query(Triple).limit(100).all()
    
    entity_map = {str(e.id): e for e in entities}
    
    triple_list = []
    for t in triples:
        head = entity_map.get(str(t.head_id))
        tail = entity_map.get(str(t.tail_id))
        if head and tail:
            triple_list.append({
                "head": head.name,
                "relation": t.relation,
                "tail": tail.name
            })
    
    prompt = f"""你是一个知识图谱问答助手。根据以下知识图谱信息，回答用户的问题。

知识图谱实体：{entity_list[:20]}
知识图谱关系：{triple_list[:30]}

用户问题：{question}

请根据以上知识图谱信息回答问题。如果知识图谱中没有相关信息，请说明"知识图谱中没有相关信息"。

回答："""

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "你是一个专业的知识图谱问答助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "triples": triple_list[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
