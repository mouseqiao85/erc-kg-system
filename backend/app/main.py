from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api import documents, projects, entities, triples, jobs, graph, auth, websocket, sentiment, import_export, sentiment_tasks

app = FastAPI(
    title="ERC-KG API",
    description="Knowledge Graph Builder API with Sentiment Analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
app.include_router(triples.router, prefix="/api/v1/triples", tags=["triples"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["websocket"])
app.include_router(sentiment.router, prefix="/api/v1/sentiment", tags=["sentiment"])
app.include_router(sentiment.router_customers, prefix="/api/v1/customers", tags=["customers"])
app.include_router(sentiment.router_articles, prefix="/api/v1/sentiment/articles", tags=["sentiment-articles"])
app.include_router(sentiment.router_events, prefix="/api/v1/sentiment/events", tags=["sentiment-events"])
app.include_router(sentiment.router_tasks, prefix="/api/v1/sentiment/tasks", tags=["sentiment-tasks"])
app.include_router(sentiment.router_export, prefix="/api/v1/export", tags=["export"])
app.include_router(import_export.router, prefix="/api/v1/io", tags=["import-export"])
app.include_router(sentiment_tasks.router, prefix="/api/v1/tasks", tags=["tasks"])


@app.get("/")
def root():
    return {"message": "ERC-KG API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
