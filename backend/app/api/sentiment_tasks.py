"""
舆情任务API - 完整任务流程
1. 创建任务 -> 2. 互联网搜索 -> 3. 构建知识图谱 -> 4. 舆情评分
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio

from app.core.database import get_db
from app.models.task_models import SentimentTask
from app.services.web_searcher import collector
from app.services.sentiment_scorer import analyzer
from app.services.extractor import LLMTripleExtractor
from app.services.validator import TripleValidator
from app.models.database import Entity, Triple, Customer, SentimentArticle
from app.core.config import settings

router = APIRouter()


class CreateTaskRequest(BaseModel):
    name: str
    entity_name: str
    keywords: Optional[List[str]] = []
    days: Optional[int] = 30


class TaskResponse(BaseModel):
    task_id: str
    name: str
    status: str
    created_at: datetime


async def run_sentiment_task(task_id: str, entity_name: str, keywords: List[str], days: int):
    """执行舆情任务完整流程"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        task = db.query(SentimentTask).filter(SentimentTask.id == task_id).first()
        if not task:
            return
        
        task.status = "running"
        task.started_at = datetime.utcnow()
        task.progress = 10
        db.commit()
        
        task.progress = 20
        task.config = {"step": "searching", "entity": entity_name}
        db.commit()
        
        articles_data = await collector.collect_entity_sentiment(entity_name, keywords, days)
        articles = articles_data.get("articles", [])
        
        task.progress = 40
        task.config = {"step": "scoring", "articles_count": len(articles)}
        db.commit()
        
        scored_result = analyzer.analyze_entity(entity_name, articles)
        
        task.progress = 60
        task.config = {"step": "saving"}
        db.commit()
        
        for article in articles[:20]:
            db_article = SentimentArticle(
                id=uuid.uuid4(),
                title=article.get("title", ""),
                source=article.get("source", ""),
                url=article.get("url", ""),
                content=article.get("snippet", ""),
                sentiment_score={
                    "overall": scored_result.get("sentiment_score", 0.5)
                }
            )
            db.add(db_article)
        
        customer = db.query(Customer).filter(Customer.name == entity_name).first()
        if not customer:
            customer = Customer(
                id=uuid.uuid4(),
                name=entity_name,
                industry="Unknown",
                sentiment_score=scored_result.get("sentiment_score", 0.5)
            )
            db.add(customer)
        else:
            customer.sentiment_score = scored_result.get("sentiment_score", 0.5)
        
        db.commit()
        
        task.progress = 100
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.result = {
            "sentiment_score": scored_result.get("sentiment_score"),
            "trend": scored_result.get("trend"),
            "risk_level": scored_result.get("risk_level"),
            "articles_count": len(articles),
            "summary": scored_result.get("summary")
        }
        db.commit()
        
    except Exception as e:
        task = db.query(SentimentTask).filter(SentimentTask.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
    
    finally:
        db.close()
        await collector.close()


@router.post("", response_model=TaskResponse)
def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """创建舆情分析任务"""
    task = SentimentTask(
        id=uuid.uuid4(),
        name=request.name,
        type="sentiment_analysis",
        status="pending",
        config={
            "entity_name": request.entity_name,
            "keywords": request.keywords,
            "days": request.days
        }
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    background_tasks.add_task(
        run_sentiment_task,
        str(task.id),
        request.entity_name,
        request.keywords,
        request.days
    )
    
    return TaskResponse(
        task_id=str(task.id),
        name=task.name,
        status=task.status,
        created_at=task.created_at
    )


@router.get("/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    """获取任务状态"""
    task = db.query(SentimentTask).filter(SentimentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": str(task.id),
        "name": task.name,
        "status": task.status,
        "progress": task.progress,
        "config": task.config,
        "result": task.result,
        "error_message": task.error_message,
        "created_at": task.created_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at
    }


@router.get("")
def list_tasks(
    status: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """列出所有任务"""
    query = db.query(SentimentTask)
    
    if status:
        query = query.filter(SentimentTask.status == status)
    
    tasks = query.order_by(SentimentTask.created_at.desc()).limit(limit).all()
    
    return {
        "items": [
            {
                "id": str(t.id),
                "name": t.name,
                "status": t.status,
                "progress": t.progress,
                "created_at": t.created_at
            }
            for t in tasks
        ]
    }


@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """删除任务"""
    task = db.query(SentimentTask).filter(SentimentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"success": True}
