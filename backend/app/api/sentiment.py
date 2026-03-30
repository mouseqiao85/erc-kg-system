from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models import schemas
from app.models.database import Customer, SentimentArticle, SentimentEvent, SentimentScore, Person
from app.core.neo4j_client import Neo4jClient
import uuid

router = APIRouter()


@router.get("/industry-overview", response_model=schemas.IndustryOverviewResponse)
def get_industry_overview(
    industries: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Customer)
    
    if industries:
        query = query.filter(Customer.industry.in_(industries))
    
    customers = query.all()
    
    nodes = []
    edges = []
    
    industry_stats = {}
    
    for c in customers:
        sentiment = c.sentiment_score or 0.5
        color = '#52c41a' if sentiment > 0.6 else '#ff4d4f' if sentiment < 0.4 else '#d9d9d9'
        
        nodes.append({
            "id": str(c.id),
            "type": "Customer",
            "name": c.name,
            "industry": c.industry,
            "sentiment_score": sentiment,
            "influence_level": c.level or "regular",
            "color": color
        })
        
        if c.industry not in industry_stats:
            industry_stats[c.industry] = {"count": 0, "positive": 0, "negative": 0, "neutral": 0}
        industry_stats[c.industry]["count"] += 1
        if sentiment > 0.6:
            industry_stats[c.industry]["positive"] += 1
        elif sentiment < 0.4:
            industry_stats[c.industry]["negative"] += 1
        else:
            industry_stats[c.industry]["neutral"] += 1
    
    industry_nodes = {}
    for industry, stats in industry_stats.items():
        industry_id = f"industry_{industry}"
        nodes.append({
            "id": industry_id,
            "type": "Industry",
            "name": industry,
            "sentiment_score": stats["positive"] / max(stats["count"], 1),
            "color": "#1890ff"
        })
        edges.append({
            "id": f"edge_{industry_id}",
            "source": industry_id,
            "target": industry_id,
            "type": "CONTAINS",
            "weight": stats["count"]
        })
    
    total_nodes = len(nodes)
    total_edges = len(edges)
    
    sentiment_dist = {"positive": sum(s["positive"] for s in industry_stats.values()),
                     "negative": sum(s["negative"] for s in industry_stats.values()),
                     "neutral": sum(s["neutral"] for s in industry_stats.values())}
    
    return {
        "nodes": nodes,
        "edges": edges,
        "statistics": {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "sentiment_distribution": sentiment_dist,
            "industry_distribution": industry_stats
        }
    }


@router.get("/customer-network/{customer_id}")
def get_customer_network(
    customer_id: str,
    depth: int = Query(2, ge=1, le=3),
    relation_types: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    neo4j = Neo4jClient()
    
    nodes = [{
        "id": str(customer.id),
        "type": "Customer",
        "name": customer.name,
        "industry": customer.industry,
        "sentiment_score": customer.sentiment_score or 0.5
    }]
    edges = []
    
    articles = db.query(SentimentArticle).filter(
        SentimentArticle.content.ilike(f"%{customer.name}%")
    ).limit(10).all()
    
    for article in articles:
        nodes.append({
            "id": str(article.id),
            "type": "Article",
            "name": article.title[:50],
            "source": article.source,
            "sentiment_score": article.sentiment_score.get("overall", 0.5) if article.sentiment_score else 0.5
        })
        edges.append({
            "id": f"edge_{customer.id}_{article.id}",
            "source": str(customer.id),
            "target": str(article.id),
            "type": "MENTIONED_IN",
            "weight": 0.8
        })
    
    events = db.query(SentimentEvent).filter(
        SentimentEvent.status == "active"
    ).limit(10).all()
    
    for event in events:
        nodes.append({
            "id": str(event.id),
            "type": "Event",
            "name": event.title[:50],
            "severity": event.severity,
            "sentiment_score": event.sentiment_impact.get("overall", 0.5) if event.sentiment_impact else 0.5
        })
        edges.append({
            "id": f"edge_{customer.id}_{event.id}",
            "source": str(customer.id),
            "target": str(event.id),
            "type": "INVOLVED_IN",
            "weight": 0.9
        })
    
    return {"nodes": nodes, "edges": edges}


@router.get("/event-evolution/{event_id}")
def get_event_evolution(
    event_id: str,
    include_articles: bool = True,
    db: Session = Depends(get_db)
):
    event = db.query(SentimentEvent).filter(SentimentEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    nodes = [{
        "id": str(event.id),
        "type": "Event",
        "name": event.title,
        "severity": event.severity,
        "status": event.status,
        "start_time": event.start_time.isoformat() if event.start_time else None,
        "sentiment_score": event.sentiment_impact.get("overall", 0.5) if event.sentiment_impact else 0.5
    }]
    edges = []
    
    if include_articles:
        articles = db.query(SentimentArticle).filter(
            SentimentArticle.content.ilike(f"%{event.title[:20]}%")
        ).order_by(SentimentArticle.publish_time.desc()).limit(20).all()
        
        for i, article in enumerate(articles):
            nodes.append({
                "id": str(article.id),
                "type": "Article",
                "name": article.title[:50],
                "source": article.source,
                "publish_time": article.publish_time.isoformat() if article.publish_time else None,
                "sentiment_score": article.sentiment_score.get("overall", 0.5) if article.sentiment_score else 0.5
            })
            edges.append({
                "id": f"edge_{event.id}_{article.id}",
                "source": str(article.id),
                "target": str(event.id),
                "type": "TRIGGERED_BY",
                "weight": 1.0 - (i * 0.05)
            })
    
    return {"nodes": nodes, "edges": edges}


@router.get("/hotspot-clusters")
def get_hotspot_clusters(
    industry: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(SentimentArticle)
    
    if industry:
        query = query.filter(SentimentArticle.content.ilike(f"%{industry}%"))
    
    articles = query.order_by(SentimentArticle.publish_time.desc()).limit(100).all()
    
    keywords = {}
    for article in articles:
        if article.content:
            words = article.content.split()[:10]
            for word in words:
                if len(word) > 2:
                    keywords[word] = keywords.get(word, 0) + 1
    
    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    nodes = []
    edges = []
    
    for i, (word, freq) in enumerate(sorted_keywords):
        nodes.append({
            "id": f"keyword_{i}",
            "type": "Keyword",
            "name": word,
            "frequency": freq,
            "sentiment_score": 0.5
        })
    
    return {"nodes": nodes, "edges": edges, "keywords": dict(sorted_keywords)}


@router.get("/entity/{entity_id}/sentiment")
def get_entity_sentiment(
    entity_id: str,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == entity_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    scores = db.query(SentimentScore).filter(
        SentimentScore.entity_id == entity_id
    ).order_by(SentimentScore.calculated_at.desc()).limit(30).all()
    
    recent_articles = db.query(SentimentArticle).filter(
        SentimentArticle.content.ilike(f"%{customer.name}%")
    ).order_by(SentimentArticle.publish_time.desc()).limit(10).all()
    
    trend = [
        {
            "date": s.calculated_at.strftime("%Y-%m-%d") if s.calculated_at else "",
            "score": s.score_overall or 0.5,
            "count": 1
        }
        for s in scores
    ]
    
    return {
        "entity_id": str(customer.id),
        "entity_name": customer.name,
        "sentiment_score": {
            "overall": customer.sentiment_score or 0.5,
            "dimensions": {
                "emotion": {"value": customer.sentiment_score or 0.5, "label": "neutral"},
                "influence": {"value": 0.6, "level": "medium"},
                "timeliness": {"value": 0.7, "label": "fresh"},
                "credibility": {"value": 0.8, "label": "high"}
            }
        },
        "trend": trend,
        "recent_articles": [
            {
                "id": str(a.id),
                "title": a.title,
                "source": a.source,
                "publish_time": a.publish_time.isoformat() if a.publish_time else None,
                "sentiment_score": a.sentiment_score.get("overall", 0.5) if a.sentiment_score else 0.5
            }
            for a in recent_articles
        ]
    }


@router.get("/industry/{industry}/trend")
def get_industry_trend(
    industry: str,
    period: str = "week",
    db: Session = Depends(get_db)
):
    customers = db.query(Customer).filter(Customer.industry == industry).all()
    
    days = 7 if period == "week" else 30
    
    trend = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - i - 1)
        trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "score": 0.5 + (i * 0.01) % 0.3,
            "count": len(customers)
        })
    
    return {
        "industry": industry,
        "period": period,
        "trend": trend
    }


@router.get("/alerts")
def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(SentimentEvent)
    
    if severity:
        query = query.filter(SentimentEvent.severity == severity)
    if status:
        query = query.filter(SentimentEvent.status == status)
    else:
        query = query.filter(SentimentEvent.status == "active")
    
    events = query.order_by(SentimentEvent.created_at.desc()).limit(limit).all()
    
    return {
        "items": [
            {
                "id": str(e.id),
                "title": e.title,
                "type": e.type,
                "severity": e.severity,
                "status": e.status,
                "sentiment_score": e.sentiment_impact.get("overall", 0.5) if e.sentiment_impact else 0.5,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in events
        ]
    }


router_customers = APIRouter()


@router_customers.get("", response_model=dict)
def get_customers(
    industry: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Customer)
    
    if industry:
        query = query.filter(Customer.industry == industry)
    if keyword:
        query = query.filter(Customer.name.ilike(f"%{keyword}%"))
    
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return {"total": total, "items": items}


@router_customers.post("", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = Customer(
        id=uuid.uuid4(),
        name=customer.name,
        industry=customer.industry,
        level=customer.level,
        tags=customer.tags,
        sentiment_score=customer.sentiment_score
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


router_articles = APIRouter()


@router_articles.get("", response_model=dict)
def get_articles(
    source: Optional[str] = None,
    source_type: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(SentimentArticle)
    
    if source:
        query = query.filter(SentimentArticle.source == source)
    if source_type:
        query = query.filter(SentimentArticle.source_type == source_type)
    
    total = query.count()
    items = query.order_by(SentimentArticle.publish_time.desc()).offset((page - 1) * size).limit(size).all()
    
    return {"total": total, "items": items}


@router_articles.post("", response_model=schemas.SentimentArticleResponse)
def create_article(article: schemas.SentimentArticleCreate, db: Session = Depends(get_db)):
    db_article = SentimentArticle(
        id=uuid.uuid4(),
        title=article.title,
        source=article.source,
        source_type=article.source_type,
        url=article.url,
        content=article.content,
        publish_time=article.publish_time
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


router_events = APIRouter()


@router_events.get("", response_model=dict)
def get_events(
    type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(SentimentEvent)
    
    if type:
        query = query.filter(SentimentEvent.type == type)
    if severity:
        query = query.filter(SentimentEvent.severity == severity)
    if status:
        query = query.filter(SentimentEvent.status == status)
    
    total = query.count()
    items = query.order_by(SentimentEvent.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return {"total": total, "items": items}


@router_events.post("", response_model=schemas.SentimentEventResponse)
def create_event(event: schemas.SentimentEventCreate, db: Session = Depends(get_db)):
    db_event = SentimentEvent(
        id=uuid.uuid4(),
        title=event.title,
        type=event.type,
        severity=event.severity,
        status=event.status,
        start_time=event.start_time,
        end_time=event.end_time
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


router_tasks = APIRouter()


@router_tasks.post("/collect")
def start_collection_task(source: str = "rss"):
    """启动数据采集任务"""
    try:
        from app.services.sentiment_tasks import collect_and_analyze
        task = collect_and_analyze.delay(source)
        return {"task_id": task.id, "status": "started", "source": source}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_tasks.get("/collect/{task_id}")
def get_collection_status(task_id: str):
    """获取采集任务状态"""
    try:
        from app.services.sentiment_tasks import collect_and_analyze
        task = collect_and_analyze.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": task.state,
            "result": task.result if task.ready() else None,
            "info": task.info if task.info else None
        }
    except Exception as e:
        return {"task_id": task_id, "status": "ERROR", "error": str(e)}


@router_tasks.post("/analyze-article/{article_id}")
def analyze_article_task(article_id: str):
    """分析单篇文章"""
    try:
        from app.services.sentiment_tasks import analyze_article_sentiment
        task = analyze_article_sentiment.delay(article_id)
        return {"task_id": task.id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_tasks.post("/update-customer/{customer_id}")
def update_customer_sentiment_task(customer_id: str):
    """更新客户情感评分"""
    try:
        from app.services.sentiment_tasks import update_customer_sentiment
        task = update_customer_sentiment.delay(customer_id)
        return {"task_id": task.id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


router_export = APIRouter()


@router_export.get("/export/customers")
def export_customers(
    format: str = "json",
    industry: str = None,
    db: Session = Depends(get_db)
):
    """导出客户数据"""
    query = db.query(Customer)
    if industry:
        query = query.filter(Customer.industry == industry)
    
    customers = query.all()
    
    data = [{
        "id": str(c.id),
        "name": c.name,
        "industry": c.industry,
        "level": c.level,
        "sentiment_score": c.sentiment_score,
        "tags": c.tags,
        "created_at": c.created_at.isoformat() if c.created_at else None
    } for c in customers]
    
    if format == "csv":
        csv_lines = ["id,name,industry,level,sentiment_score"]
        for c in data:
            csv_lines.append(f"{c['id']},{c['name']},{c['industry']},{c.get('level','')},{c.get('sentiment_score','')}")
        return {"data": "\n".join(csv_lines), "content_type": "text/csv"}
    
    return {"data": data, "count": len(data)}


@router_export.get("/export/articles")
def export_articles(
    format: str = "json",
    source: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """导出文章数据"""
    query = db.query(SentimentArticle)
    if source:
        query = query.filter(SentimentArticle.source == source)
    
    articles = query.order_by(SentimentArticle.publish_time.desc()).limit(limit).all()
    
    data = [{
        "id": str(a.id),
        "title": a.title,
        "source": a.source,
        "source_type": a.source_type,
        "url": a.url,
        "publish_time": a.publish_time.isoformat() if a.publish_time else None,
        "sentiment_score": a.sentiment_score,
    } for a in articles]
    
    if format == "csv":
        csv_lines = ["id,title,source,source_type,sentiment"]
        for a in data:
            sentiment = a.get('sentiment_score', {}).get('overall', '') if a.get('sentiment_score') else ''
            csv_lines.append(f"{a['id']},{a['title']},{a['source']},{a['source_type']},{sentiment}")
        return {"data": "\n".join(csv_lines), "content_type": "text/csv"}
    
    return {"data": data, "count": len(data)}


@router_export.get("/export/events")
def export_events(
    format: str = "json",
    status: str = "active",
    db: Session = Depends(get_db)
):
    """导出事件数据"""
    query = db.query(SentimentEvent)
    if status:
        query = query.filter(SentimentEvent.status == status)
    
    events = query.order_by(SentimentEvent.created_at.desc()).all()
    
    data = [{
        "id": str(e.id),
        "title": e.title,
        "type": e.type,
        "severity": e.severity,
        "status": e.status,
        "start_time": e.start_time.isoformat() if e.start_time else None,
        "created_at": e.created_at.isoformat() if e.created_at else None
    } for e in events]
    
    return {"data": data, "count": len(data)}


@router_export.get("/export/graph")
def export_graph(
    project_id: str = None,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """导出知识图谱"""
    if project_id:
        from app.models.database import Entity, Triple
        entities = db.query(Entity).filter(Entity.project_id == project_id).all()
        entity_map = {str(e.id): e for e in entities}
        
        triples = db.query(Triple).filter(Triple.project_id == project_id).all()
        
        nodes = [{"id": str(e.id), "name": e.name, "type": e.type} for e in entities]
        edges = []
        for t in triples:
            head = entity_map.get(str(t.head_id))
            tail = entity_map.get(str(t.tail_id))
            if head and tail:
                edges.append({
                    "head": head.name,
                    "relation": t.relation,
                    "tail": tail.name
                })
    else:
        from app.models.database import Entity, Triple
        entities = db.query(Entity).limit(1000).all()
        triples = db.query(Triple).limit(1000).all()
        
        nodes = [{"id": str(e.id), "name": e.name, "type": e.type} for e in entities]
        edges = [{"head": t.head_id, "relation": t.relation, "tail": t.tail_id} for t in triples]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "count": {"nodes": len(nodes), "edges": len(edges)}
    }