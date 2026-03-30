from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    title: str
    format: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: UUID
    project_id: UUID
    content: Optional[str] = None
    status: str
    metadata: dict = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class EntityBase(BaseModel):
    name: str
    type: Optional[str] = None
    confidence: Optional[float] = None


class EntityCreate(EntityBase):
    project_id: UUID
    source_id: Optional[UUID] = None


class EntityResponse(EntityBase):
    id: UUID
    project_id: UUID
    properties: dict = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class TripleBase(BaseModel):
    head: str
    relation: str
    tail: str


class TripleCreate(TripleBase):
    project_id: UUID
    source_id: Optional[UUID] = None


class TripleResponse(TripleBase):
    id: UUID
    project_id: UUID
    confidence: Optional[float] = None
    valid: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobConfig(BaseModel):
    entity_types: List[str] = []
    llm_model: str = "gpt-4"
    temperature: float = 0.7
    enable_validation: bool = True


class JobCreate(BaseModel):
    project_id: UUID
    doc_ids: List[UUID]
    config: JobConfig = JobConfig()


class JobResponse(BaseModel):
    id: UUID
    project_id: UUID
    type: str
    status: str
    progress: int = 0
    current_step: Optional[str] = None
    config: dict = {}
    result: dict = {}
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    progress: int
    current_step: Optional[str] = None
    stats: dict = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class CypherQueryRequest(BaseModel):
    query: str


class NaturalQueryRequest(BaseModel):
    question: str


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class PromptTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template: str


class PromptTemplateCreate(PromptTemplateBase):
    variables: List[str] = []
    is_default: bool = False


class PromptTemplateResponse(PromptTemplateBase):
    id: UUID
    variables: List[str] = []
    is_default: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
