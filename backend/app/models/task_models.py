import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class SentimentTask(Base):
    """舆情任务表"""
    __tablename__ = "sentiment_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # search, build_graph, score
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0)
    
    config = Column(JSON, default={})
    result = Column(JSON, default={})
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
