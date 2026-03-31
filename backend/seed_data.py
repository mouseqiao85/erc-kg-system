#!/usr/bin/env python3
"""Seed database with test data"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uuid import uuid4
from datetime import datetime, timedelta
import random
from passlib.context import CryptContext

from app.core.database import SessionLocal
from app.models.database import (
    User, Project, Document, Entity, Triple, Job,
    PromptTemplate, SystemConfig, Customer, SentimentArticle
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_users(db):
    users = []
    test_users = [
        {"username": "admin", "email": "admin@example.com", "role": "admin"},
        {"username": "user1", "email": "user1@example.com", "role": "user"},
        {"username": "user2", "email": "user2@example.com", "role": "user"},
    ]
    
    for u in test_users:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if existing:
            users.append(existing)
            continue
        user = User(
            id=uuid4(),
            username=u["username"],
            email=u["email"],
            password_hash=pwd_context.hash("password123"),
            role=u["role"],
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    return users


def seed_projects(db, users):
    projects = []
    for i, user in enumerate(users):
        project = Project(
            id=uuid4(),
            user_id=user.id,
            name=f"Test Project {i+1}",
            description=f"Description for test project {i+1}",
            config={"language": "zh", "entity_types": ["Person", "Organization", "Location"]},
        )
        db.add(project)
        projects.append(project)
    
    db.commit()
    return projects


def seed_documents(db, projects):
    documents = []
    sample_texts = [
        "张三是某科技公司的高级工程师，负责人工智能项目开发。",
        "李四担任某金融机构的首席信息官，推动数字化转型。",
        "王五创立了一家专注于绿色能源的初创企业。",
        "某科技公司与某银行达成战略合作协议，共同开发智能金融产品。",
        "市场研究显示，人工智能行业在2024年将保持高速增长。",
    ]
    
    for project in projects:
        for i, content in enumerate(sample_texts):
            doc = Document(
                id=uuid4(),
                project_id=project.id,
                title=f"Document {i+1}",
                format="txt",
                content=content,
                status="completed",
                metadata={"source": "test"},
            )
            db.add(doc)
            documents.append(doc)
    
    db.commit()
    return documents


def seed_entities(db, projects, documents):
    entities = []
    entity_data = [
        {"name": "张三", "type": "Person"},
        {"name": "李四", "type": "Person"},
        {"name": "王五", "type": "Person"},
        {"name": "某科技公司", "type": "Organization"},
        {"name": "某金融机构", "type": "Organization"},
        {"name": "某银行", "type": "Organization"},
        {"name": "北京", "type": "Location"},
        {"name": "上海", "type": "Location"},
    ]
    
    for project in projects:
        for data in entity_data:
            entity = Entity(
                id=uuid4(),
                project_id=project.id,
                source_id=random.choice(documents).id if documents else None,
                name=data["name"],
                type=data["type"],
                confidence=random.uniform(0.8, 0.99),
                properties={},
            )
            db.add(entity)
            entities.append(entity)
    
    db.commit()
    return entities


def seed_triples(db, projects, entities):
    triples = []
    triple_data = [
        {"head": "张三", "relation": "任职于", "tail": "某科技公司"},
        {"head": "李四", "relation": "任职于", "tail": "某金融机构"},
        {"head": "王五", "relation": "创立", "tail": "某科技公司"},
        {"head": "某科技公司", "relation": "合作", "tail": "某银行"},
    ]
    
    entity_map = {e.name: e for e in entities}
    
    for project in projects:
        for data in triple_data:
            head = entity_map.get(data["head"])
            tail = entity_map.get(data["tail"])
            if head and tail and head.project_id == project.id:
                triple = Triple(
                    id=uuid4(),
                    project_id=project.id,
                    head_id=head.id,
                    relation=data["relation"],
                    tail_id=tail.id,
                    confidence=random.uniform(0.75, 0.95),
                    valid=True,
                )
                db.add(triple)
                triples.append(triple)
    
    db.commit()
    return triples


def seed_jobs(db, projects):
    jobs = []
    
    for project in projects:
        for i, status in enumerate(["completed", "running", "pending"]):
            job = Job(
                id=uuid4(),
                project_id=project.id,
                type="extraction",
                status=status,
                progress=100 if status == "completed" else (50 if status == "running" else 0),
                current_step="Completed" if status == "completed" else ("Processing" if status == "running" else "Queued"),
                config={"model": "glm-5-openclaw"},
                result={"entities": 10, "triples": 15} if status == "completed" else {},
            )
            db.add(job)
            jobs.append(job)
    
    db.commit()
    return jobs


def seed_prompt_templates(db):
    templates = [
        {
            "name": "Entity Extraction",
            "description": "Extract entities from text",
            "template": "从以下文本中提取实体（人名、组织、地点等）：\n{text}\n\n请以JSON格式返回提取结果。",
            "variables": ["text"],
            "is_default": True,
        },
        {
            "name": "Relation Extraction",
            "description": "Extract relations between entities",
            "template": "分析以下文本中实体之间的关系：\n{text}\n\n实体列表：{entities}\n\n请以JSON格式返回关系三元组。",
            "variables": ["text", "entities"],
            "is_default": True,
        },
        {
            "name": "Sentiment Analysis",
            "description": "Analyze sentiment of text",
            "template": "分析以下文本的情感倾向：\n{text}\n\n请返回情感分数（-1到1）和情感类型。",
            "variables": ["text"],
            "is_default": False,
        },
    ]
    
    for t in templates:
        existing = db.query(PromptTemplate).filter(PromptTemplate.name == t["name"]).first()
        if not existing:
            template = PromptTemplate(
                id=uuid4(),
                name=t["name"],
                description=t["description"],
                template=t["template"],
                variables=t["variables"],
                is_default=t["is_default"],
            )
            db.add(template)
    
    db.commit()


def seed_customers(db):
    industries = ["金融", "科技", "制造", "零售", "医疗"]
    levels = ["重要", "核心", "普通"]
    
    for i in range(20):
        customer = Customer(
            id=uuid4(),
            name=f"客户{i+1}",
            industry=random.choice(industries),
            level=random.choice(levels),
            tags=[random.choice(["VIP", "新客户", "长期", "潜在"])],
            sentiment_score=random.uniform(-1, 1),
            properties={"region": random.choice(["北京", "上海", "深圳", "广州"])},
        )
        db.add(customer)
    
    db.commit()


def seed_sentiment_articles(db):
    sources = ["新浪财经", "东方财富", "证券时报", "财联社", "界面新闻"]
    
    for i in range(30):
        article = SentimentArticle(
            id=uuid4(),
            title=f"财经新闻标题 {i+1}",
            source=random.choice(sources),
            source_type="news",
            url=f"https://example.com/news/{i+1}",
            content=f"这是第{i+1}篇财经新闻的内容摘要...",
            publish_time=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            sentiment_score={
                "overall": random.uniform(-1, 1),
                "positive": random.uniform(0, 1),
                "negative": random.uniform(0, 1),
            },
        )
        db.add(article)
    
    db.commit()


def main():
    db = SessionLocal()
    try:
        print("Seeding users...")
        users = seed_users(db)
        
        print("Seeding projects...")
        projects = seed_projects(db, users)
        
        print("Seeding documents...")
        documents = seed_documents(db, projects)
        
        print("Seeding entities...")
        entities = seed_entities(db, projects, documents)
        
        print("Seeding triples...")
        triples = seed_triples(db, projects, entities)
        
        print("Seeding jobs...")
        jobs = seed_jobs(db, projects)
        
        print("Seeding prompt templates...")
        seed_prompt_templates(db)
        
        print("Seeding customers...")
        seed_customers(db)
        
        print("Seeding sentiment articles...")
        seed_sentiment_articles(db)
        
        print("Test data seeded successfully!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
