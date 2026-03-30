# ERC-KG 系统架构设计文档

**项目名称**: ERC-KG Knowledge Graph Builder  
**版本**: V1.0  
**日期**: 2026-03-30  
**作者**: AI Assistant  

---

## 1. 系统概述

### 1.1 系统定位

ERC-KG Knowledge Graph Builder 是一款基于大语言模型的领域知识图谱自动构建系统，融合抽取（Extraction）、检索（Retrieval）与纠错（Error Correction）三大核心能力，实现高质量、高效率的知识图谱构建。

### 1.2 核心价值

- **高精确率**: 实验验证精确率达 94.32%
- **低人工成本**: 减少专家干预，自动化程度高
- **快速构建**: 相比传统方法大幅缩短构建周期
- **领域通用**: 可扩展至医学、金融、国防等多领域

---

## 2. 技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端展示层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 文档管理  │  │ 图谱可视化│  │ 查询分析  │  │ 系统配置  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                     React + TypeScript + Ant Design              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ REST API / WebSocket
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         API 网关层                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Nginx 反向代理                          │  │
│  │  - 负载均衡                                                │  │
│  │  - SSL 终止                                                │  │
│  │  - 静态资源服务                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         API 服务层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 文档API   │  │ 图谱API   │  │ 查询API   │  │ 配置API   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                     Python + FastAPI + Celery                    │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       ERC-KG 核心引擎                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    实体语料检索器                           │  │
│  │  - 特征词抽取 (TF-IDF/TextRank)                           │  │
│  │  - 语义检索 (Sentence-BERT + Milvus)                     │  │
│  │  - 相似度计算 (Cosine Similarity)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    LLM 抽取引擎                            │  │
│  │  - 提示模板管理                                           │  │
│  │  - 三元组抽取 (OpenAI GPT-4 / 本地大模型)                │  │
│  │  - 结果解析 (JSON)                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    验证纠错模块                            │  │
│  │  - 事实检查 (源文本比对)                                  │  │
│  │  - 规则验证 (关系一致性)                                  │  │
│  │  - LLM 再审 (二次验证)                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         数据存储层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Neo4j    │  │ Milvus   │  │ PostgreSQL│  │ Redis    │        │
│  │ 图数据库  │  │ 向量库    │  │ 关系数据库 │  │ 缓存     │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

#### 2.2.1 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.x | UI 框架 |
| TypeScript | 5.x | 类型安全 |
| Ant Design | 5.x | UI 组件库 |
| D3.js | 7.x | 图谱可视化 |
| React Flow | 11.x | 流程图组件 |
| Axios | 1.x | HTTP 客户端 |
| React Router | 6.x | 路由管理 |
| Zustand | 4.x | 状态管理 |
| Vite | 5.x | 构建工具 |

#### 2.2.2 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.109+ | Web 框架 |
| SQLAlchemy | 2.x | ORM 框架 |
| Celery | 5.x | 异步任务队列 |
| Redis | 7.x | 缓存 & 消息队列 |
| Pydantic | 2.x | 数据验证 |
| Sentence-Transformers | 2.x | 向量化 |
| OpenAI SDK | 1.x | LLM 接口 |

#### 2.2.3 数据存储

| 技术 | 版本 | 用途 |
|------|------|------|
| Neo4j | 5.x | 图数据库 |
| Milvus | 2.x | 向量数据库 |
| PostgreSQL | 15.x | 关系数据库 |
| Redis | 7.x | 缓存 |

---

## 3. 模块设计

### 3.1 核心引擎模块

#### 3.1.1 实体语料检索器

**职责**: 从文档中检索与实体相关的语料，为三元组抽取提供上下文。

**核心算法**:

```python
class EntityRetriever:
    """
    实体语料检索器
    
    流程：
    1. 特征词抽取：使用 TF-IDF/TextRank 提取高频词
    2. 向量化：使用 Sentence-BERT 对句子和实体进行向量化
    3. 语义检索：计算实体与句子的语义相似度
    4. 区间离散化：应用相似度区间系数 α 进行筛选
    5. 长度控制：自适应控制文本长度
    """
    
    def __init__(self, embedding_model, alpha=0.8, top_k=10):
        self.embedding_model = embedding_model
        self.alpha = alpha
        self.top_k = top_k
    
    def retrieve(self, entity: str, corpus: List[str]) -> List[str]:
        # 实现检索逻辑
        pass
```

**接口设计**:

```python
POST /api/v1/retrieval
{
  "entity": "RSA",
  "doc_id": "uuid",
  "config": {
    "alpha": 0.8,
    "top_k": 10,
    "max_length": 4096
  }
}

Response:
{
  "corpus": ["句子1", "句子2", ...],
  "scores": [0.95, 0.87, ...]
}
```

#### 3.1.2 LLM 抽取引擎

**职责**: 使用 LLM 从语料中抽取结构化三元组。

**提示模板设计**:

```
## 任务描述
你是一个知识图谱构建专家，请从以下文本中提取领域相关三元组。

## 输出格式
请以 JSON 格式输出三元组列表：
[
  {"head": "头实体", "relation": "关系", "tail": "尾实体"},
  ...
]

## 示例（Few-shot）
文本：RSA是一种非对称加密算法，由Ron Rivest等人于1977年提出。
输出：
[
  {"head": "RSA", "relation": "是一种", "tail": "非对称加密算法"},
  {"head": "RSA", "relation": "发明者", "tail": "Ron Rivest"},
  {"head": "RSA", "relation": "发明时间", "tail": "1977年"}
]

## 待处理文本
{context}

## 注意事项
1. 仅输出文本中明确陈述的事实
2. 不要添加文本中未提及的信息
3. 保持关系的简洁和规范
```

**接口设计**:

```python
POST /api/v1/extraction
{
  "entity": "RSA",
  "corpus": ["句子1", "句子2", ...],
  "config": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}

Response:
{
  "triples": [
    {"head": "RSA", "relation": "是一种", "tail": "非对称加密算法"},
    ...
  ],
  "confidence": 0.95
}
```

#### 3.1.3 验证纠错模块

**职责**: 验证三元组的正确性，消除 LLM 幻觉。

**验证流程**:

```python
class TripleValidator:
    """
    三元组验证器
    
    验证流程：
    1. 事实检查：三元组是否在源文本中有依据
    2. 规则验证：关系一致性、实体类型检查
    3. LLM 再审：使用 LLM 二次验证
    """
    
    def validate(self, triple: dict, source_text: str) -> dict:
        # 1. 事实检查
        if not self._fact_check(triple, source_text):
            return {"valid": False, "reason": "事实依据不足"}
        
        # 2. 规则验证
        if not self._rule_validation(triple):
            return {"valid": False, "reason": "关系不一致"}
        
        # 3. LLM 再审
        llm_judgment = self._llm_review(triple, source_text)
        if not llm_judgment["correct"]:
            return {"valid": False, "reason": llm_judgment["reason"]}
        
        return {"valid": True}
```

**接口设计**:

```python
POST /api/v1/validation
{
  "triple": {
    "head": "RSA",
    "relation": "是一种",
    "tail": "非对称加密算法"
  },
  "source_text": "RSA是一种非对称加密算法...",
  "config": {
    "enable_llm_review": true
  }
}

Response:
{
  "valid": true,
  "confidence": 0.95,
  "reasons": []
}
```

### 3.2 API 服务模块

#### 3.2.1 文档管理 API

```python
# 文档上传
POST /api/v1/documents
Request: multipart/form-data (file)
Response: { "doc_id": "uuid", "status": "pending" }

# 获取文档列表
GET /api/v1/documents?page=1&size=20&status=pending
Response: { "total": 100, "items": [...] }

# 获取文档详情
GET /api/v1/documents/{doc_id}
Response: { "doc_id": "...", "title": "...", ... }

# 删除文档
DELETE /api/v1/documents/{doc_id}
Response: { "success": true }
```

#### 3.2.2 图谱构建 API

```python
# 启动构建任务
POST /api/v1/jobs
Request: {
  "doc_ids": ["uuid1", "uuid2"],
  "config": {
    "entity_types": ["Person", "Organization"],
    "llm_model": "gpt-4",
    "temperature": 0.7
  }
}
Response: { "job_id": "uuid", "status": "running" }

# 获取任务状态
GET /api/v1/jobs/{job_id}
Response: { 
  "job_id": "...", 
  "status": "completed",
  "progress": 100,
  "stats": {
    "entities": 100,
    "triples": 500,
    "precision": 0.94
  }
}
```

#### 3.2.3 图谱查询 API

```python
# 实体搜索
GET /api/v1/entities?keyword=RSA&limit=20
Response: { "items": [{"id": "...", "name": "RSA", "type": "Algorithm"}] }

# 关系查询
GET /api/v1/relations?head=RSA&limit=20
Response: { "items": [{"relation": "是一种", "tail": "非对称加密算法"}] }

# Cypher 查询
POST /api/v1/query/cypher
Request: { "query": "MATCH (n:Entity) RETURN n LIMIT 10" }
Response: { "results": [...] }

# 自然语言查询
POST /api/v1/query/natural
Request: { "question": "RSA是什么？" }
Response: { "answer": "RSA是一种非对称加密算法...", "triples": [...] }
```

---

## 4. 数据流设计

### 4.1 知识图谱构建流程

```
文档上传
    │
    ▼
文档解析 ───────────┐
    │               │
    ▼               │
特征词抽取          │
    │               │
    ▼               │
实体识别            │
    │               │
    ▼               │
实体语料检索 ◄──────┘
    │
    ▼
三元组抽取 (LLM)
    │
    ▼
验证纠错
    │
    ├─── 验证通过 ──→ 存储到 Neo4j
    │
    └─── 验证失败 ──→ 返回修正建议
```

### 4.2 异步任务处理

```
用户请求
    │
    ▼
FastAPI 接收请求
    │
    ▼
创建异步任务 (Celery)
    │
    ├─── 返回 job_id 给用户
    │
    └─── 后台执行 ──→ WebSocket 推送进度
```

---

## 5. 部署架构

### 5.1 开发环境

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - NEO4J_URI=bolt://neo4j:7687
      - MILVUS_HOST=milvus
      - REDIS_URL=redis://redis:6379
  
  neo4j:
    image: neo4j:5.x
    ports:
      - "7474:7474"
      - "7687:7687"
  
  milvus:
    image: milvusdb/milvus:v2.x
    ports:
      - "19530:19530"
  
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

### 5.2 生产环境

```
┌─────────────────────────────────────────────────────────────────┐
│                         负载均衡层                                │
│                     Nginx / Cloud Load Balancer                  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼───────┐   ┌─────────▼─────────┐   ┌──────▼──────┐
│  Frontend 1   │   │   Frontend 2      │   │ Frontend 3  │
│   (React)     │   │    (React)        │   │  (React)    │
└───────────────┘   └───────────────────┘   └─────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼───────┐   ┌─────────▼─────────┐   ┌──────▼──────┐
│  Backend 1    │   │   Backend 2       │   │ Backend 3   │
│  (FastAPI)    │   │   (FastAPI)       │   │ (FastAPI)   │
└───────────────┘   └───────────────────┘   └─────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼───────┐   ┌─────────▼─────────┐   ┌──────▼──────┐
│   Neo4j       │   │   Milvus          │   │ PostgreSQL  │
│  (Cluster)    │   │  (Cluster)        │   │ (Cluster)   │
└───────────────┘   └───────────────────┘   └─────────────┘
```

---

## 6. 安全设计

### 6.1 认证授权

- **认证方式**: JWT Token
- **授权机制**: RBAC (基于角色的访问控制)
- **Token 过期**: 30 分钟
- **刷新机制**: Refresh Token

### 6.2 API 安全

- **HTTPS**: 强制 HTTPS
- **CORS**: 白名单域名
- **限流**: Redis 令牌桶算法
- **输入验证**: Pydantic 严格验证

### 6.3 数据安全

- **敏感数据加密**: AES-256
- **数据库访问**: 最小权限原则
- **备份策略**: 每日自动备份

---

## 7. 性能优化

### 7.1 缓存策略

```
Redis 缓存层次：
├── 会话缓存 (Session Cache)
├── 查询结果缓存 (Query Result Cache)
├── 向量缓存 (Embedding Cache)
└── 临时数据缓存 (Temp Data Cache)
```

### 7.2 异步处理

- **文档解析**: Celery 异步任务
- **三元组抽取**: Celery 异步任务
- **进度推送**: WebSocket 实时推送

### 7.3 数据库优化

- **索引设计**: 合理创建索引
- **查询优化**: 避免 N+1 查询
- **连接池**: 数据库连接池

---

## 8. 监控告警

### 8.1 监控指标

- **系统指标**: CPU、内存、磁盘、网络
- **应用指标**: 请求量、响应时间、错误率
- **业务指标**: 文档处理量、三元组数量、查询次数

### 8.2 日志管理

- **日志级别**: DEBUG、INFO、WARNING、ERROR
- **日志收集**: ELK Stack
- **日志分析**: 关键操作审计日志

---

## 9. 扩展性设计

### 9.1 水平扩展

- **无状态服务**: API 服务无状态设计
- **负载均衡**: 支持水平扩展
- **数据库分片**: 支持数据库分片

### 9.2 插件机制

- **实体识别插件**: 支持 NER 插件扩展
- **关系抽取插件**: 支持关系抽取插件
- **验证规则插件**: 支持自定义验证规则

---

**文档状态**: 初稿  
**最后更新**: 2026-03-30
