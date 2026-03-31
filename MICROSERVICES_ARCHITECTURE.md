# 微服务架构设计

## 架构概述

ERC-KG系统采用**微服务架构**，将系统分为两个独立的后端服务：

1. **Golang Backend** - 主要业务服务
2. **Python Backend** - AI/ML服务

## 服务架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (React)                          │
│                      Port: 3000                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Golang Backend                             │
│                      Port: 8000                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 用户管理      │  │ 项目管理      │  │ 文档管理      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 认证授权      │  │ 实体管理      │  │ 知识图谱      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/gRPC
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Python Backend                             │
│                      Port: 8001                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 情感分析      │  │ LLM调用       │  │ 百度搜索      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ 数据采集      │  │ 舆情分析      │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │PostgreSQL│  │  Neo4j   │  │  Milvus  │  │  Redis   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 服务职责

### Golang Backend (Port 8000)

**主要职责：** 业务逻辑处理

**核心功能：**
- 用户管理（注册、登录、权限管理）
- 认证授权（JWT Token管理）
- 项目管理（项目CRUD、任务管理）
- 文档管理（文档上传、解析、存储）
- 实体管理（实体识别、实体关系管理）
- 知识图谱管理（图谱构建、查询、可视化）
- API Gateway（转发AI/ML请求到Python服务）

**技术栈：**
- 框架：Gin / Echo / Fiber
- ORM：GORM
- 认证：JWT
- 日志：zap / logrus
- 配置：viper

### Python Backend (Port 8001)

**主要职责：** AI/ML任务处理

**核心功能：**
- 情感分析（文本情感识别、情感维度分析）
- LLM调用（集成百度内部API）
- 百度搜索（舆情信息获取）
- 数据采集（RSS、新闻API、网页抓取）
- 舆情分析（舆情监控、预警）
- 向量检索（Milvus集成）

**技术栈：**
- 框架：FastAPI
- LLM：百度内部API
- 向量数据库：Milvus
- NLP：transformers、jieba

## 服务通信

### 同步通信

- **协议：** HTTP/REST
- **格式：** JSON
- **场景：** 实时请求（如情感分析、LLM调用）

**示例：**
```go
// Golang Backend调用Python Backend
func AnalyzeSentiment(text string) (*SentimentResult, error) {
    resp, err := http.Post("http://python-backend:8001/api/v1/analyze/sentiment", 
        "application/json", bytes.NewBuffer(payload))
    // ...
}
```

### 异步通信（可选）

- **协议：** Redis Pub/Sub / RabbitMQ / Kafka
- **场景：** 批量处理任务（如批量数据采集、异步分析）

## 数据库架构

### PostgreSQL

**用途：** 关系型数据存储

**存储内容：**
- 用户信息
- 项目信息
- 文档元数据
- 实体信息
- 任务信息

**访问服务：** Golang Backend

### Neo4j

**用途：** 图数据库

**存储内容：**
- 实体关系
- 知识图谱
- 事件关系

**访问服务：** Golang Backend, Python Backend

### Milvus

**用途：** 向量数据库

**存储内容：**
- 文档向量
- 实体向量
- 相似度索引

**访问服务：** Python Backend

### Redis

**用途：** 缓存、会话、消息队列

**存储内容：**
- 用户会话
- 缓存数据
- 任务队列

**访问服务：** Golang Backend, Python Backend

## API设计

### Golang Backend API

```
/api/v1
├── /auth
│   ├── POST /register
│   ├── POST /login
│   ├── POST /logout
│   └── POST /refresh
├── /users
│   ├── GET /
│   ├── GET /:id
│   ├── PUT /:id
│   └── DELETE /:id
├── /projects
│   ├── GET /
│   ├── POST /
│   ├── GET /:id
│   ├── PUT /:id
│   └── DELETE /:id
├── /documents
│   ├── GET /
│   ├── POST /
│   ├── GET /:id
│   └── DELETE /:id
├── /entities
│   ├── GET /
│   ├── POST /
│   ├── GET /:id
│   └── DELETE /:id
└── /graph
    ├── GET /nodes
    ├── GET /edges
    └── POST /query
```

### Python Backend API

```
/api/v1
├── /analyze
│   ├── POST /sentiment
│   ├── POST /entities
│   └── POST /relations
├── /search
│   ├── POST /baidu
│   └── POST /entities
├── /llm
│   ├── POST /generate
│   ├── POST /refactor
│   └── POST /explain
└── /collect
    ├── POST /rss
    ├── POST /news
    └── POST /url
```

## 部署架构

### 开发环境

```bash
# Golang Backend
cd backend-go
go run main.go

# Python Backend
cd backend
uvicorn app.main:app --port 8001

# Frontend
cd frontend
npm run dev
```

### 生产环境

```yaml
# docker-compose.yml
version: '3.8'
services:
  golang-backend:
    build: ./backend-go
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - neo4j
      - redis

  python-backend:
    build: ./backend
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - neo4j
      - milvus
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - golang-backend
```

## 开发优先级

### Phase 1: Golang Backend基础
1. ✅ 项目结构创建
2. ✅ 数据库连接配置
3. ✅ 用户认证API
4. ✅ 项目管理API
5. ✅ 文档管理API

### Phase 2: Python Backend优化
1. ✅ 百度搜索集成
2. ✅ LLM API集成
3. ✅ 情感分析优化
4. ✅ 数据采集功能

### Phase 3: 服务集成
1. ✅ Golang调用Python API
2. ✅ 统一错误处理
3. ✅ 日志聚合
4. ✅ 监控告警

### Phase 4: 前端开发
1. ✅ 用户认证页面
2. ✅ 项目管理页面
3. ✅ 文档管理页面
4. ✅ 知识图谱可视化

## 技术选型理由

### Golang优势
- ✅ 高性能、高并发
- ✅ 编译型语言，部署简单
- ✅ 内存占用低
- ✅ 适合API服务

### Python优势
- ✅ AI/ML生态丰富
- ✅ 快速开发
- ✅ NLP库完善
- ✅ 适合数据处理

## 服务监控

### 健康检查
- Golang Backend: `GET /health`
- Python Backend: `GET /health`

### 日志
- Golang: zap (结构化日志)
- Python: logging (JSON格式)

### 监控指标
- Prometheus + Grafana
- 服务响应时间
- 错误率
- 并发数

## 总结

微服务架构将系统分为两个独立的后端服务：
- **Golang Backend** 负责业务逻辑，高性能、高并发
- **Python Backend** 负责AI/ML任务，生态丰富、开发快速

这种架构充分发挥了两种语言的优势，实现了服务的解耦和独立扩展。
