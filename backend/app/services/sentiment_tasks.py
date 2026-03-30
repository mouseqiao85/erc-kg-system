from celery import Celery
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.database import Customer, SentimentArticle, SentimentEvent
from app.services.data_collector import collector, announcement_collector
from app.services.sentiment_analyzer import sentiment_analyzer, keyword_extractor, event_detector, alert_generator
import uuid
from datetime import datetime
import asyncio

celery_app = Celery(
    "erc_kg_sentiment",
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


@celery_app.task(bind=True)
def collect_and_analyze(self, source: str = "rss"):
    """采集数据并分析"""
    db = SessionLocal()
    
    try:
        self.update_state(state="PROGRESS", meta={"progress": 10, "message": "采集数据中..."})
        
        articles = []
        
        if source == "rss":
            articles = asyncio.run(collector.collect_all_sources())
        elif source == "announcement":
            articles = []
            for exchange in ["sse", "szse"]:
                ann = asyncio.run(announcement_collector.fetch_announcements(exchange))
                articles.extend(ann)
        
        self.update_state(state="PROGRESS", meta={"progress": 40, "message": f"获取 {len(articles)} 篇文章"})
        
        saved_count = 0
        for i, article in enumerate(articles):
            if i % 5 == 0:
                progress = 40 + int((i / len(articles)) * 30)
                self.update_state(state="PROGRESS", meta={"progress": progress, "message": f"分析文章 {i+1}/{len(articles)}"})
            
            content = article.get("content", "")
            title = article.get("title", "")
            
            if not content and not title:
                continue
            
            text_to_analyze = f"{title} {content}"
            
            sentiment = sentiment_analyzer.analyze_sentiment(text_to_analyze)
            
            db_article = SentimentArticle(
                id=uuid.uuid4(),
                title=title[:500],
                source=article.get("source", "unknown"),
                source_type=article.get("source_type", "news"),
                url=article.get("url", ""),
                content=content[:5000] if content else "",
                publish_time=datetime.utcnow(),
                sentiment_score=sentiment
            )
            db.add(db_article)
            saved_count += 1
        
        db.commit()
        
        self.update_state(state="PROGRESS", meta={"progress": 75, "message": "检测舆情事件..."})
        
        recent_articles = db.query(SentimentArticle).order_by(
            SentimentArticle.created_at.desc()
        ).limit(50).all()
        
        article_dicts = [
            {"title": a.title, "content": a.content, "sentiment_score": a.sentiment_score}
            for a in recent_articles
        ]
        
        events = event_detector.detect_events(article_dicts)
        
        for event_data in events:
            existing = db.query(SentimentEvent).filter(
                SentimentEvent.title == event_data.get("title")
            ).first()
            
            if not existing:
                db_event = SentimentEvent(
                    id=uuid.uuid4(),
                    title=event_data.get("title", "")[:500],
                    type=event_data.get("type", "trend"),
                    severity=event_data.get("severity", "medium"),
                    status="active",
                    start_time=datetime.utcnow()
                )
                db.add(db_event)
        
        db.commit()
        
        self.update_state(state="PROGRESS", meta={"progress": 90, "message": "生成预警..."})
        
        customers = db.query(Customer).all()
        customer_list = [{"id": str(c.id), "name": c.name, "sentiment_score": c.sentiment_score} for c in customers]
        
        events = db.query(SentimentEvent).filter(SentimentEvent.status == "active").all()
        event_list = [{"title": e.title, "severity": e.severity} for e in events]
        
        alerts = alert_generator.check_alerts(customer_list, event_list, article_dicts)
        
        db.commit()
        
        return {
            "success": True,
            "articles_collected": len(articles),
            "articles_saved": saved_count,
            "events_detected": len(events),
            "alerts_generated": len(alerts)
        }
        
    except Exception as e:
        db.rollback()
        raise
        
    finally:
        db.close()


@celery_app.task(bind=True)
def analyze_article_sentiment(self, article_id: str):
    """分析单篇文章情感"""
    db = SessionLocal()
    
    try:
        article = db.query(SentimentArticle).filter(SentimentArticle.id == article_id).first()
        if not article:
            return {"error": "Article not found"}
        
        text_to_analyze = f"{article.title} {article.content}"
        sentiment = sentiment_analyzer.analyze_sentiment(text_to_analyze)
        
        article.sentiment_score = sentiment
        db.commit()
        
        return {"success": True, "sentiment": sentiment}
        
    finally:
        db.close()


@celery_app.task(bind=True)
def update_customer_sentiment(self, customer_id: str):
    """更新客户情感评分"""
    db = SessionLocal()
    
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"error": "Customer not found"}
        
        articles = db.query(SentimentArticle).filter(
            SentimentArticle.content.ilike(f"%{customer.name}%")
        ).all()
        
        if not articles:
            return {"message": "No related articles found"}
        
        sentiments = [a.sentiment_score.get("overall", 0.5) if a.sentiment_score else 0.5 for a in articles]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
        
        customer.sentiment_score = avg_sentiment
        db.commit()
        
        return {
            "success": True,
            "sentiment_score": avg_sentiment,
            "article_count": len(articles)
        }
        
    finally:
        db.close()
