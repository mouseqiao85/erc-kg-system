# ERC-KG 数据库设计文档

## 数据库选型

| 数据库 | 用途 | 说明 |
|--------|------|------|
| PostgreSQL | 关系数据 | 元数据、配置、用户数据 |
| Neo4j | 图数据 | 知识图谱存储 |
| Milvus | 向量数据 | 语义检索向量存储 |
| Redis | 缓存 | 会话、临时数据缓存 |

## PostgreSQL 表结构

### 1. 用户表 (users)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) DEFAULT 'user',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### 2. 项目表 (projects)
```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  config JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_projects_user_id ON projects(user_id);
```

### 3. 文档表 (documents)
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  format VARCHAR(20) NOT NULL,
  file_path VARCHAR(1000),
  content TEXT,
  status VARCHAR(20) DEFAULT 'pending',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_documents_status ON documents(status);
```

### 4. 实体表 (entities)
```sql
CREATE TABLE entities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  source_id UUID REFERENCES documents(id) ON DELETE SET NULL,
  name VARCHAR(500) NOT NULL,
  type VARCHAR(100),
  confidence FLOAT,
  properties JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_entities_project_id ON entities(project_id);
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_entities_type ON entities(type);
```

### 5. 三元组表 (triples)
```sql
CREATE TABLE triples (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  source_id UUID REFERENCES documents(id) ON DELETE SET NULL,
  head_id UUID REFERENCES entities(id) ON DELETE CASCADE,
  relation VARCHAR(200) NOT NULL,
  tail_id UUID REFERENCES entities(id) ON DELETE CASCADE,
  confidence FLOAT,
  valid BOOLEAN DEFAULT true,
  validation_result JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_triples_project_id ON triples(project_id);
CREATE INDEX idx_triples_head_id ON triples(head_id);
CREATE INDEX idx_triples_tail_id ON triples(tail_id);
CREATE INDEX idx_triples_relation ON triples(relation);
```

### 6. 任务表 (jobs)
```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  progress INT DEFAULT 0,
  current_step VARCHAR(100),
  config JSONB DEFAULT '{}',
  result JSONB DEFAULT '{}',
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);

CREATE INDEX idx_jobs_project_id ON jobs(project_id);
CREATE INDEX idx_jobs_status ON jobs(status);
```

### 7. 提示模板表 (prompt_templates)
```sql
CREATE TABLE prompt_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  description TEXT,
  template TEXT NOT NULL,
  variables JSONB DEFAULT '[]',
  is_default BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 8. 验证规则表 (validation_rules)
```sql
CREATE TABLE validation_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  description TEXT,
  rule_type VARCHAR(50) NOT NULL,
  rule_config JSONB NOT NULL,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 9. 系统配置表 (system_configs)
```sql
CREATE TABLE system_configs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key VARCHAR(100) UNIQUE NOT NULL,
  value JSONB NOT NULL,
  description TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 10. 审计日志表 (audit_logs)
```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(50),
  resource_id UUID,
  details JSONB DEFAULT '{}',
  ip_address VARCHAR(50),
  user_agent VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

## Neo4j 图数据模型

### 节点标签

#### Entity 节点
```cypher
CREATE (e:Entity {
  id: "uuid",
  name: "实体名称",
  type: "实体类型",
  confidence: 0.95,
  source: "来源文档ID",
  properties: {},
  created_at: datetime()
})
```

### 关系类型

#### RELATION 关系
```cypher
CREATE (h:Entity {id: "head_id"})
CREATE (t:Entity {id: "tail_id"})
CREATE (h)-[r:RELATION {
  id: "uuid",
  name: "关系名称",
  confidence: 0.95,
  source: "来源文档ID",
  valid: true,
  created_at: datetime()
}]->(t)
```

### 索引

```cypher
// 实体名称索引
CREATE INDEX entity_name_index FOR (e:Entity) ON (e.name)

// 实体类型索引
CREATE INDEX entity_type_index FOR (e:Entity) ON (e.type)

// 实体ID索引
CREATE CONSTRAINT entity_id_unique FOR (e:Entity) REQUIRE e.id IS UNIQUE
```

## Milvus 向量集合

### sentence_embeddings 集合
```python
collection_schema = {
  "name": "sentence_embeddings",
  "description": "句子语义向量",
  "fields": [
    {
      "name": "id",
      "dtype": "VARCHAR",
      "max_length": 36,
      "is_primary": True
    },
    {
      "name": "doc_id",
      "dtype": "VARCHAR",
      "max_length": 36
    },
    {
      "name": "sentence",
      "dtype": "VARCHAR",
      "max_length": 1000
    },
    {
      "name": "embedding",
      "dtype": "FLOAT_VECTOR",
      "dim": 768  # Sentence-BERT 维度
    }
  ],
  "index_params": {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
  }
}
```

### entity_embeddings 集合
```python
collection_schema = {
  "name": "entity_embeddings",
  "description": "实体语义向量",
  "fields": [
    {
      "name": "id",
      "dtype": "VARCHAR",
      "max_length": 36,
      "is_primary": True
    },
    {
      "name": "entity_id",
      "dtype": "VARCHAR",
      "max_length": 36
    },
    {
      "name": "entity_name",
      "dtype": "VARCHAR",
      "max_length": 500
    },
    {
      "name": "embedding",
      "dtype": "FLOAT_VECTOR",
      "dim": 768
    }
  ],
  "index_params": {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
  }
}
```

## Redis 缓存设计

### 键命名规范

```
# 会话缓存
session:{user_id}:{session_id}

# 查询结果缓存
query:cypher:{hash(query)}
query:natural:{hash(question)}

# 向量缓存
embedding:sentence:{hash(sentence)}
embedding:entity:{hash(entity_name)}

# 任务进度
job:progress:{job_id}

# 限流
ratelimit:{user_id}:{endpoint}
```

### 数据结构

```redis
# 会话 (String, TTL: 30分钟)
session:123:abc = '{"user_id": "123", "username": "admin", "role": "admin"}'

# 查询结果 (String, TTL: 10分钟)
query:cypher:hash123 = '{"results": [...], "count": 10}'

# 任务进度 (Hash, TTL: 24小时)
job:progress:uuid = {
  "status": "running",
  "progress": "50",
  "current_step": "三元组抽取"
}

# 限流 (String, TTL: 1分钟)
ratelimit:123:/api/v1/documents = "5"
```

## 数据迁移

### 初始化脚本

```sql
-- 创建默认管理员
INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@example.com', '$2b$12$...', 'admin');

-- 创建默认配置
INSERT INTO system_configs (key, value, description)
VALUES 
  ('llm.model', '"gpt-4"', 'LLM 模型'),
  ('llm.temperature', '0.7', 'LLM 温度'),
  ('retrieval.alpha', '0.8', '检索相似度系数'),
  ('retrieval.top_k', '10', '检索Top K');

-- 创建默认提示模板
INSERT INTO prompt_templates (name, description, template, is_default)
VALUES (
  '三元组抽取模板',
  '用于从文本中抽取三元组',
  '...',
  true
);
```

## 备份策略

- **PostgreSQL**: 每日全量备份，增量备份每小时
- **Neo4j**: 每日全量备份
- **Milvus**: 每日全量备份
- **Redis**: RDB 持久化，AOF 日志
