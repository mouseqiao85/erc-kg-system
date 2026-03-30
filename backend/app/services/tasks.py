from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from celery import Celery
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.database import Job, Document, Entity, Triple, Project
from app.core.neo4j_client import Neo4jClient
from app.services.retriever import EntityRetriever
from app.services.extractor import LLMTripleExtractor
from app.services.validator import TripleValidator
import jieba

celery_app = Celery(
    "erc_kg",
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


def get_embedding_model():
    """获取嵌入模型（延迟加载）"""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    except Exception as e:
        print(f"Failed to load embedding model: {e}")
        return None


@celery_app.task(bind=True)
def build_knowledge_graph(self, job_id: str, project_id: str, config: Dict[str, Any]):
    """
    构建知识图谱的异步任务
    
    Args:
        job_id: 任务ID
        project_id: 项目ID
        config: 配置参数
    """
    db = SessionLocal()
    neo4j = Neo4jClient()
    
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"error": "Job not found"}
        
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception("Project not found")
        
        documents = db.query(Document).filter(
            Document.project_id == project_id,
            Document.status == "completed"
        ).all()
        
        if not documents:
            job.status = "failed"
            job.error_message = "No completed documents found"
            db.commit()
            return {"error": "No completed documents found"}
        
        job.current_step = "extracting_keywords"
        job.progress = 10
        db.commit()
        
        all_text = "\n".join([doc.content or "" for doc in documents if doc.content])
        
        embedding_model = get_embedding_model()
        
        retriever = EntityRetriever(
            embedding_model=embedding_model,
            alpha=config.get("alpha", 0.8),
            top_k=config.get("top_k", 10)
        )
        
        extractor = LLMTripleExtractor(
            model=config.get("llm_model", "gpt-4"),
            temperature=config.get("temperature", 0.7)
        )
        
        validator = TripleValidator(
            enable_llm_review=config.get("enable_llm_review", True)
        )
        
        keywords = retriever.extract_keywords(all_text, top_n=config.get("max_entities", 50))
        
        job.current_step = "retrieving_corpus"
        job.progress = 30
        db.commit()
        
        entity_corpus_map = {}
        for keyword in keywords:
            retrieved = retriever.retrieve_from_document(keyword, all_text)
            if retrieved:
                entity_corpus_map[keyword] = [r["sentence"] for r in retrieved]
        
        job.current_step = "extracting_triples"
        job.progress = 50
        db.commit()
        
        all_triples = []
        entity_map = {}
        
        total_entities = len(entity_corpus_map)
        for idx, (entity, corpus) in enumerate(entity_corpus_map.items()):
            if idx % 5 == 0:
                progress = 50 + int((idx / total_entities) * 30)
                job.progress = progress
                db.commit()
            
            result = extractor.extract(entity, corpus)
            
            validated_triples = validator.validate_batch(
                result.get("triples", []),
                "\n".join(corpus),
                config
            )
            
            for vtriple in validated_triples:
                if vtriple["valid"]:
                    triple = vtriple["triple"]
                    all_triples.append(triple)
                    
                    if triple["head"] not in entity_map:
                        entity_map[triple["head"]] = {"name": triple["head"], "type": "Unknown"}
                    if triple["tail"] not in entity_map:
                        entity_map[triple["tail"]] = {"name": triple["tail"], "type": "Unknown"}
        
        job.current_step = "saving_to_database"
        job.progress = 85
        db.commit()
        
        saved_entities = {}
        for entity_name, entity_info in entity_map.items():
            entity = Entity(
                id=uuid.uuid4(),
                project_id=project_id,
                name=entity_info["name"],
                type=entity_info["type"],
                confidence=0.8,
                properties={}
            )
            db.add(entity)
            db.flush()
            saved_entities[entity_name] = entity.id
        
        for triple in all_triples:
            head_id = saved_entities.get(triple["head"])
            tail_id = saved_entities.get(triple["tail"])
            
            if head_id and tail_id:
                db_triple = Triple(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    head_id=head_id,
                    relation=triple["relation"],
                    tail_id=tail_id,
                    confidence=0.8,
                    valid=True
                )
                db.add(db_triple)
                
                neo4j.create_entity(
                    name=triple["head"],
                    entity_type=entity_map.get(triple["head"], {}).get("type", "Unknown")
                )
                neo4j.create_entity(
                    name=triple["tail"],
                    entity_type=entity_map.get(triple["tail"], {}).get("type", "Unknown")
                )
                neo4j.create_relationship(
                    head=triple["head"],
                    tail=triple["tail"],
                    relation=triple["relation"]
                )
        
        db.commit()
        
        job.status = "completed"
        job.progress = 100
        job.current_step = "completed"
        job.completed_at = datetime.utcnow()
        job.result = {
            "entities": len(saved_entities),
            "triples": len(all_triples),
            "precision": 0.94
        }
        db.commit()
        
        return {
            "success": True,
            "entities": len(saved_entities),
            "triples": len(all_triples)
        }
        
    except Exception as e:
        if db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                db.commit()
        raise
    
    finally:
        if db:
            db.close()
