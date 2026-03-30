# ERC-KG 后端 API 设计文档

## API 概述

- **Base URL**: `/api/v1`
- **认证**: JWT Bearer Token
- **格式**: JSON

## 核心模块

### 1. 文档管理模块

#### 1.1 上传文档
```
POST /documents
Content-Type: multipart/form-data

Response: {
  "doc_id": "uuid",
  "title": "文档标题",
  "status": "pending"
}
```

#### 1.2 获取文档列表
```
GET /documents?page=1&size=20&status=pending

Response: {
  "total": 100,
  "items": [
    {
      "doc_id": "uuid",
      "title": "文档标题",
      "format": "pdf",
      "status": "completed",
      "created_at": "2026-03-30T10:00:00Z"
    }
  ]
}
```

#### 1.3 获取文档详情
```
GET /documents/{doc_id}

Response: {
  "doc_id": "uuid",
  "title": "文档标题",
  "content": "文档内容...",
  "status": "completed",
  "metadata": {}
}
```

#### 1.4 删除文档
```
DELETE /documents/{doc_id}

Response: { "success": true }
```

### 2. 实体管理模块

#### 2.1 获取实体列表
```
GET /entities?keyword=RSA&limit=20

Response: {
  "items": [
    {
      "id": "uuid",
      "name": "RSA",
      "type": "Algorithm",
      "confidence": 0.95
    }
  ]
}
```

#### 2.2 创建实体
```
POST /entities

Request: {
  "name": "RSA",
  "type": "Algorithm",
  "source_id": "doc_uuid"
}

Response: {
  "id": "uuid",
  "name": "RSA",
  "type": "Algorithm"
}
```

### 3. 三元组管理模块

#### 3.1 获取三元组列表
```
GET /triples?head=RSA&limit=20

Response: {
  "items": [
    {
      "id": "uuid",
      "head": "RSA",
      "relation": "是一种",
      "tail": "非对称加密算法",
      "confidence": 0.95,
      "valid": true
    }
  ]
}
```

#### 3.2 创建三元组
```
POST /triples

Request: {
  "head": "RSA",
  "relation": "是一种",
  "tail": "非对称加密算法",
  "source_id": "doc_uuid"
}

Response: {
  "id": "uuid",
  "head": "RSA",
  "relation": "是一种",
  "tail": "非对称加密算法",
  "valid": true
}
```

### 4. 图谱构建模块

#### 4.1 启动构建任务
```
POST /jobs

Request: {
  "doc_ids": ["uuid1", "uuid2"],
  "config": {
    "entity_types": ["Person", "Organization"],
    "llm_model": "gpt-4",
    "temperature": 0.7,
    "enable_validation": true
  }
}

Response: {
  "job_id": "uuid",
  "status": "pending"
}
```

#### 4.2 获取任务状态
```
GET /jobs/{job_id}

Response: {
  "job_id": "uuid",
  "status": "running",
  "progress": 50,
  "current_step": "三元组抽取",
  "stats": {
    "total_docs": 2,
    "processed_docs": 1,
    "entities": 50,
    "triples": 200
  }
}
```

#### 4.3 获取任务列表
```
GET /jobs?page=1&size=20

Response: {
  "total": 10,
  "items": [...]
}
```

### 5. 图谱查询模块

#### 5.1 Cypher 查询
```
POST /query/cypher

Request: {
  "query": "MATCH (n:Entity) RETURN n LIMIT 10"
}

Response: {
  "results": [...],
  "count": 10
}
```

#### 5.2 自然语言查询
```
POST /query/natural

Request: {
  "question": "RSA是什么？"
}

Response: {
  "answer": "RSA是一种非对称加密算法...",
  "triples": [
    {
      "head": "RSA",
      "relation": "是一种",
      "tail": "非对称加密算法"
    }
  ]
}
```

#### 5.3 实体关系查询
```
GET /query/relations?entity=RSA&depth=2

Response: {
  "nodes": [...],
  "edges": [...]
}
```

### 6. 图谱可视化模块

#### 6.1 获取图谱数据
```
GET /graph?project_id=uuid&limit=100

Response: {
  "nodes": [
    {
      "id": "uuid",
      "label": "RSA",
      "type": "Algorithm"
    }
  ],
  "edges": [
    {
      "source": "uuid1",
      "target": "uuid2",
      "label": "是一种"
    }
  ]
}
```

#### 6.2 获取子图
```
GET /graph/subgraph?entity_id=uuid&depth=2

Response: {
  "nodes": [...],
  "edges": [...]
}
```

### 7. 项目管理模块

#### 7.1 创建项目
```
POST /projects

Request: {
  "name": "加密算法知识图谱",
  "description": "构建加密算法领域知识图谱"
}

Response: {
  "id": "uuid",
  "name": "加密算法知识图谱"
}
```

#### 7.2 获取项目列表
```
GET /projects

Response: {
  "items": [...]
}
```

### 8. 系统配置模块

#### 8.1 获取配置
```
GET /config

Response: {
  "llm": {
    "model": "gpt-4",
    "temperature": 0.7
  },
  "retrieval": {
    "alpha": 0.8,
    "top_k": 10
  }
}
```

#### 8.2 更新配置
```
PUT /config

Request: {
  "llm": {
    "model": "gpt-4",
    "temperature": 0.7
  }
}

Response: { "success": true }
```

## WebSocket 接口

### 任务进度推送
```
ws://host/api/v1/ws/jobs/{job_id}

Message: {
  "event": "progress",
  "data": {
    "progress": 50,
    "current_step": "三元组抽取"
  }
}
```

## 错误处理

### 错误响应格式
```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "文档不存在",
    "details": {}
  }
}
```

### 错误码
- `DOCUMENT_NOT_FOUND`: 文档不存在
- `INVALID_FILE_FORMAT`: 文件格式不支持
- `JOB_NOT_FOUND`: 任务不存在
- `VALIDATION_ERROR`: 数据验证失败
- `LLM_ERROR`: LLM 调用失败
- `DATABASE_ERROR`: 数据库错误

## 认证授权

### 登录
```
POST /auth/login

Request: {
  "username": "admin",
  "password": "password"
}

Response: {
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "expires_in": 1800
}
```

### 刷新Token
```
POST /auth/refresh

Request: {
  "refresh_token": "refresh_token"
}

Response: {
  "access_token": "new_jwt_token",
  "expires_in": 1800
}
```

## 限流策略

- **默认**: 100 请求/分钟
- **文档上传**: 10 请求/分钟
- **图谱构建**: 5 请求/分钟
- **Cypher 查询**: 30 请求/分钟
