# ERC-KG 前端设计文档

## 技术栈

- **框架**: React 18 + TypeScript
- **UI 库**: Ant Design 5
- **图谱可视化**: D3.js + React Flow
- **状态管理**: Zustand
- **路由**: React Router 6
- **HTTP**: Axios
- **构建**: Vite 5

## 页面结构

```
/
├── /login                 # 登录页
├── /dashboard             # 仪表盘
├── /projects              # 项目管理
│   ├── /projects/list     # 项目列表
│   └── /projects/:id      # 项目详情
├── /documents             # 文档管理
│   ├── /documents/list    # 文档列表
│   └── /documents/:id     # 文档详情
├── /graph                 # 图谱管理
│   ├── /graph/view        # 图谱可视化
│   ├── /graph/entities    # 实体管理
│   └── /graph/triples     # 三元组管理
├── /jobs                  # 任务管理
│   ├── /jobs/list         # 任务列表
│   └── /jobs/:id          # 任务详情
├── /query                 # 查询分析
│   ├── /query/cypher      # Cypher 查询
│   └── /query/natural     # 自然语言查询
└── /settings              # 系统设置
    ├── /settings/config   # 配置管理
    └── /settings/users    # 用户管理
```

## 核心组件

### 1. 文档管理组件

#### DocumentUpload
- 文件上传（支持拖拽）
- 格式校验（PDF、Word、TXT、Markdown）
- 批量上传
- 进度显示

#### DocumentList
- 文档列表展示（表格）
- 状态筛选
- 分页
- 搜索

#### DocumentDetail
- 文档预览
- 处理状态
- 相关实体/三元组

### 2. 图谱可视化组件

#### GraphViewer
- 力导向图展示
- 缩放、平移
- 节点拖拽
- 点击交互

#### EntityNode
- 实体节点展示
- 类型颜色区分
- Hover 提示

#### RelationEdge
- 关系边展示
- 关系标签
- 点击交互

#### GraphControls
- 缩放控制
- 布局切换
- 筛选控制

### 3. 查询组件

#### CypherEditor
- Cypher 编辑器
- 语法高亮
- 自动补全
- 执行按钮

#### QueryResult
- 结果展示（表格/JSON）
- 导出功能

#### NaturalLanguageQuery
- 自然语言输入框
- 结果展示
- 相关三元组展示

### 4. 任务管理组件

#### JobList
- 任务列表展示
- 状态筛选
- 进度显示

#### JobDetail
- 任务详情
- 进度条
- 日志展示
- 统计信息

### 5. 通用组件

#### Layout
- 侧边栏导航
- 顶部导航
- 内容区域

#### Breadcrumb
- 面包屑导航

#### StatusBadge
- 状态徽章（颜色区分）

#### ProgressIndicator
- 进度指示器

## 状态管理

### stores/documentStore
```typescript
interface DocumentStore {
  documents: Document[]
  currentDocument: Document | null
  loading: boolean
  
  fetchDocuments: (params: QueryParams) => Promise<void>
  uploadDocument: (file: File) => Promise<void>
  deleteDocument: (id: string) => Promise<void>
}
```

### stores/graphStore
```typescript
interface GraphStore {
  nodes: Node[]
  edges: Edge[]
  selectedNode: Node | null
  
  fetchGraph: (projectId: string) => Promise<void>
  fetchSubgraph: (entityId: string, depth: number) => Promise<void>
  searchEntity: (keyword: string) => Promise<void>
}
```

### stores/jobStore
```typescript
interface JobStore {
  jobs: Job[]
  currentJob: Job | null
  
  fetchJobs: () => Promise<void>
  createJob: (config: JobConfig) => Promise<void>
  subscribeToJob: (jobId: string) => void
}
```

## API 服务

### services/documentService
```typescript
export const documentService = {
  getDocuments: (params) => api.get('/documents', { params }),
  getDocument: (id) => api.get(`/documents/${id}`),
  uploadDocument: (file) => api.post('/documents', file),
  deleteDocument: (id) => api.delete(`/documents/${id}`)
}
```

### services/graphService
```typescript
export const graphService = {
  getGraph: (projectId) => api.get('/graph', { params: { project_id: projectId } }),
  getSubgraph: (entityId, depth) => api.get('/graph/subgraph', { params: { entity_id: entityId, depth } }),
  searchEntity: (keyword) => api.get('/entities', { params: { keyword } }),
  queryCypher: (query) => api.post('/query/cypher', { query }),
  queryNatural: (question) => api.post('/query/natural', { question })
}
```

### services/jobService
```typescript
export const jobService = {
  getJobs: () => api.get('/jobs'),
  getJob: (id) => api.get(`/jobs/${id}`),
  createJob: (config) => api.post('/jobs', config)
}
```

## 样式设计

### 主题配置
```typescript
const theme = {
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    borderRadius: 6
  }
}
```

### 图谱节点颜色
```typescript
const entityColors = {
  Person: '#1890ff',
  Organization: '#52c41a',
  Location: '#faad14',
  Algorithm: '#722ed1',
  Concept: '#13c2c2',
  Default: '#8c8c8c'
}
```

## 交互设计

### 文档上传
1. 点击上传按钮或拖拽文件
2. 显示上传进度
3. 上传成功后显示文档卡片
4. 可点击查看详情或开始处理

### 图谱构建
1. 选择文档
2. 配置抽取参数
3. 启动任务
4. 实时显示进度（WebSocket）
5. 完成后展示统计信息

### 图谱浏览
1. 加载图谱数据
2. 力导向图自动布局
3. 拖拽节点调整位置
4. 点击节点展示详情
5. 双击节点展开相关子图

### 自然语言查询
1. 输入问题
2. 提交查询
3. 展示答案和相关三元组
4. 可点击三元组跳转到图谱

## 响应式设计

- **桌面端**: 侧边栏 + 内容区
- **平板端**: 可折叠侧边栏
- **移动端**: 底部导航 + 内容区

## 性能优化

- **虚拟列表**: 大量数据列表虚拟滚动
- **懒加载**: 图谱节点懒加载
- **缓存**: API 响应缓存
- **防抖**: 搜索输入防抖
- **代码分割**: 路由级代码分割
