from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ERC-KG API",
    description="Knowledge Graph Builder",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "ERC-KG API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/projects")
def get_projects():
    return {"items": [], "total": 0}

@app.get("/api/v1/documents")  
def get_documents():
    return {"items": [], "total": 0}

@app.get("/api/v1/graph")
def get_graph():
    return {"nodes": [], "edges": []}

@app.get("/api/v1/entities")
def get_entities():
    return {"items": []}

@app.get("/api/v1/triples")
def get_triples():
    return {"items": []}

@app.get("/api/v1/sentiment/industry-overview")
def industry_overview():
    return {"nodes": [], "edges": [], "statistics": {}}
