# ERC-KG Knowledge Graph Builder - 开发任务

## 项目概述

基于 PRD 文档（C:\Users\qiaoshuowen\Downloads\ERC-KG-PRD.md）构建一个完整的领域知识图谱自动构建系统。

## 设计文档位置

- 系统架构设计: `docs/SYSTEM_ARCHITECTURE.md`
- 后端 API 设计: `docs/BACKEND_API.md`
- 前端设计: `docs/FRONTEND_DESIGN.md`
- 数据库设计: `docs/DATABASE_DESIGN.md`

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy (PostgreSQL ORM)
- Neo4j Driver
- Milvus Python SDK
- Redis
- Celery (异步任务)
- Sentence-Transformers (向量化)
- OpenAI SDK (LLM 接口)

### 前端
- React 18
- TypeScript
- Ant Design 5
- D3.js (图谱可视化)
- React Flow
- Zustand (状态管理)
- Axios
- Vite

## 核心功能模块

### 1. 后端核心引擎

#### 1.1 实体语料检索器
- 特征词抽取（TF-IDF/TextRank）
- 语义检索（Sentence-BERT + Milvus）
- 相似度计算

#### 1.2 LLM 抽取引擎
- 提示模板管理
- 三元组抽取
- 结果解析

#### 1.3 验证纠错模块
- 事实检查
- 规则验证
- LLM 再审

### 2. 后端 API 服务

#### 2.1 文档管理 API
- 文档上传
- 文档列表
- 文档详情
- 文档删除

#### 2.2 图谱构建 API
- 启动构建任务
- 任务状态查询
- 任务列表

#### 2.3 图谱查询 API
- 实体搜索
- 关系查询
- Cypher 查询
- 自然语言查询

#### 2.4 图谱可视化 API
- 图谱数据获取
- 子图获取

### 3. 前端页面

#### 3.1 文档管理页面
- 文档上传（支持拖拽）
- 文档列表
- 文档详情

#### 3.2 图谱可视化页面
- 力导向图展示
- 缩放、平移
- 节点拖拽
- 点击交互

#### 3.3 查询分析页面
- Cypher 编辑器
- 自然语言查询
- 结果展示

#### 3.4 任务管理页面
- 任务列表
- 任务详情
- 进度展示（WebSocket）

## 开发步骤

### Phase 1: 项目初始化（优先）

1. **创建项目目录结构**
   ```
   erc-kg-system/
   ├── backend/
   │   ├── app/
   │   │   ├── api/
   │   │   ├── core/
   │   │   ├── models/
   │   │   ├── services/
   │   │   └── main.py
   │   ├── tests/
   │   ├── requirements.txt
   │   └── Dockerfile
   ├── frontend/
   │   ├── src/
   │   │   ├── components/
   │   │   ├── pages/
   │   │   ├── services/
   │   │   ├── stores/
   │   │   └── App.tsx
   │   ├── package.json
   │   └── Dockerfile
   ├── docs/
   └── docker-compose.yml
   ```

2. **初始化后端项目**
   - 创建 FastAPI 应用
   - 配置 SQLAlchemy + PostgreSQL
   - 配置 Neo4j 连接
   - 配置 Milvus 连接
   - 配置 Redis 连接
   - 创建基础模型

3. **初始化前端项目**
   - 使用 Vite 创建 React + TypeScript 项目
   - 安装 Ant Design
   - 配置路由
   - 配置 Axios

### Phase 2: 数据库设计与实现

1. **PostgreSQL 表结构**
   - 用户表
   - 项目表
   - 文档表
   - 实体表
   - 三元组表
   - 任务表
   - 配置表

2. **Neo4j 图模型**
   - Entity 节点
   - RELATION 关系
   - 索引创建

3. **Milvus 向量集合**
   - sentence_embeddings
   - entity_embeddings

### Phase 3: 后端核心引擎实现

1. **实体语料检索器**
   - 实现特征词抽取
   - 实现向量化
   - 实现语义检索
   - 集成 Milvus

2. **LLM 抽取引擎**
   - 实现提示模板管理
   - 集成 OpenAI API
   - 实现三元组抽取
   - 实现结果解析

3. **验证纠错模块**
   - 实现事实检查
   - 实现规则验证
   - 实现 LLM 再审

### Phase 4: 后端 API 实现

1. **认证 API**
   - 登录
   - Token 刷新
   - JWT 认证中间件

2. **文档管理 API**
   - 文档上传
   - 文档列表
   - 文档详情
   - 文档删除

3. **图谱构建 API**
   - 启动构建任务（Celery）
   - 任务状态查询
   - WebSocket 进度推送

4. **图谱查询 API**
   - 实体搜索
   - 关系查询
   - Cypher 查询
   - 自然语言查询

### Phase 5: 前端实现

1. **布局与导航**
   - 侧边栏导航
   - 顶部导航
   - 路由配置

2. **文档管理页面**
   - 文档上传组件
   - 文档列表组件
   - 文档详情组件

3. **图谱可视化页面**
   - 图谱展示组件（D3.js）
   - 节点/边渲染
   - 交互控制

4. **查询分析页面**
   - Cypher 编辑器
   - 自然语言查询
   - 结果展示

5. **任务管理页面**
   - 任务列表
   - 任务详情
   - 进度展示

### Phase 6: 集成与测试

1. **前后端集成**
   - API 调用测试
   - WebSocket 连接测试

2. **核心功能测试**
   - 文档上传与解析
   - 图谱构建流程
   - 图谱查询功能

3. **部署配置**
   - Docker Compose 配置
   - Nginx 配置

## 配置要求

### 环境变量（后端）
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/erc_kg
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
MILVUS_HOST=localhost
MILVUS_PORT=19530
REDIS_URL=redis://localhost:6379

# LLM
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 环境变量（前端）
```env
VITE_API_URL=http://localhost:8000
```

## 注意事项

1. **安全性**
   - 所有 API 需要 JWT 认证
   - 敏感数据加密存储
   - SQL 注入防护
   - CORS 配置

2. **性能优化**
   - 使用 Redis 缓存查询结果
   - 异步任务使用 Celery
   - 向量检索使用 Milvus
   - 前端使用虚拟列表

3. **错误处理**
   - 统一错误响应格式
   - 详细的错误日志
   - 用户友好的错误提示

4. **代码规范**
   - 使用 TypeScript 类型检查
   - 使用 Pydantic 数据验证
   - 编写单元测试

## 期望输出

完成一个可运行的知识图谱构建系统，包括：
1. 完整的后端 API 服务
2. 完整的前端界面
3. 核心引擎实现
4. 数据库初始化脚本
5. Docker 部署配置
6. API 文档（FastAPI 自动生成）

## 开始开发

请按照上述开发步骤，从 Phase 1 开始逐步实现所有功能。重点关注：
1. 项目结构清晰
2. 代码质量高
3. 核心功能完整
4. 可直接运行
