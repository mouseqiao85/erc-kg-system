# 舆情分析图谱可视化设计文档

## 一、系统概述

### 1.1 目标
构建一个基于知识图谱的舆情分析可视化系统，支持：
- **多行业覆盖**：制造、能源、金融、科技
- **多源数据**：新闻网站、社交媒体、公告
- **多维评分**：情感倾向、影响力、时效性、可信度
- **多粒度分析**：客户级别、行业级别、事件级别

### 1.2 核心能力
- 🎯 **实时舆情采集**：基于 OpenClaw 自动采集
- 🧠 **智能分析评分**：NLP + LLM 自动分析
- 📊 **图谱可视化**：交互式知识图谱展示
- 🔔 **智能预警**：风险事件自动提醒

---

## 二、图谱数据模型

### 2.1 实体类型

| 实体类型 | 标签 | 属性 | 说明 |
|---------|------|------|------|
| 客户 | `Customer` | name, industry, level, sentiment_score | 企业/机构客户 |
| 行业 | `Industry` | name, code, sentiment_trend | 制造/能源/金融/科技 |
| 事件 | `Event` | title, type, severity, status | 舆情事件 |
| 文章 | `Article` | title, source, url, publish_time, content | 舆情文章 |
| 人物 | `Person` | name, position, company | 关键人物 |
| 关键词 | `Keyword` | word, frequency, trend | 热点关键词 |

### 2.2 关系类型

| 关系类型 | 起点 | 终点 | 属性 | 说明 |
|---------|------|------|------|------|
| `BELONGS_TO` | Customer | Industry | - | 客户所属行业 |
| `INVOLVED_IN` | Customer | Event | role | 客户参与事件 |
| `MENTIONED_IN` | Customer | Article | sentiment, score | 客户被提及 |
| `RELATED_TO` | Event | Event | correlation | 事件关联 |
| `TRIGGERED_BY` | Event | Article | impact | 事件触发源 |
| `HAS_KEYWORD` | Article | Keyword | frequency | 文章关键词 |
| `REPORTED_BY` | Article | Person | sentiment | 人物报道 |

### 2.3 舆情评分属性

```json
{
  "sentiment_score": {
    "overall": 0.75,
    "dimensions": {
      "emotion": {
        "value": 0.8,
        "label": "positive",
        "weight": 0.3
      },
      "influence": {
        "value": 0.7,
        "level": "high",
        "weight": 0.3,
        "metrics": {
          "reach": 100000,
          "shares": 5000,
          "media_level": "national"
        }
      },
      "timeliness": {
        "value": 0.9,
        "label": "fresh",
        "weight": 0.2,
        "age_hours": 2
      },
      "credibility": {
        "value": 0.85,
        "label": "high",
        "weight": 0.2,
        "source_type": "official"
      }
    }
  }
}
```

---

## 三、可视化设计

### 3.1 图谱视图模式

#### A. 行业全景图
```
展示四大行业的舆情分布和关联
- 节点大小：影响力
- 节点颜色：情感倾向（红=负面，绿=正面，灰=中性）
- 连线粗细：关联强度
- 支持缩放、拖拽、筛选
```

#### B. 客户关系图
```
展示客户的舆情网络
- 中心节点：目标客户
- 一级关联：直接相关的客户、事件、人物
- 二级关联：间接关联实体
- 支持层级展开/收起
```

#### C. 事件演变图
```
展示舆情事件的时间演变
- 时间轴：横向时间线
- 节点：事件里程碑
- 连线：因果关系
- 动画：事件发展过程
```

#### D. 热点聚类图
```
展示舆情热点分布
- 聚类算法：LDA/K-Means
- 气泡大小：热度
- 颜色深浅：情感倾向
- 支持点击钻取
```

### 3.2 交互功能

| 功能 | 说明 | 快捷键 |
|------|------|--------|
| 节点搜索 | 按名称/类型搜索实体 | Ctrl+F |
| 筛选过滤 | 按行业/时间/情感筛选 | - |
| 路径探索 | 查找两个实体的关联路径 | Ctrl+P |
| 时间回溯 | 查看历史图谱状态 | Ctrl+T |
| 导出图片 | 导出当前视图为PNG/SVG | Ctrl+E |
| 全屏模式 | 切换全屏显示 | F11 |

### 3.3 节点详情面板

点击节点后显示：
- **基本信息**：名称、类型、属性
- **舆情评分**：四维评分雷达图
- **相关文章**：最新相关文章列表
- **时间趋势**：舆情情感变化曲线
- **关联实体**：相关客户/事件/人物

---

## 四、前端技术方案

### 4.1 技术栈

| 组件 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| 图可视化 | D3.js | v7 | 力导向图、自定义渲染 |
| 流程图 | React Flow | v11 | 事件演变图 |
| 图谱库 | Cytoscape.js | v3 | 复杂网络分析 |
| 3D视图 | Three.js | v157 | 3D图谱展示 |
| 状态管理 | Zustand | v4 | 全局状态 |
| 图表库 | Ant Design Charts | v2 | 统计图表 |

### 4.2 组件结构

```
frontend/src/components/graph/
├── GraphCanvas.tsx          # 图谱画布组件
├── GraphControls.tsx        # 控制面板（缩放、筛选、布局）
├── NodeDetail.tsx           # 节点详情面板
├── SearchBar.tsx            # 搜索栏
├── TimeSlider.tsx           # 时间轴滑块
├── LegendPanel.tsx          # 图例面板
├── FilterPanel.tsx          # 筛选面板
├── ExportButton.tsx         # 导出按钮
├── layouts/
│   ├── ForceLayout.ts       # 力导向布局
│   ├── CircularLayout.ts    # 环形布局
│   ├── HierarchicalLayout.ts # 层级布局
│   └── TimelineLayout.ts    # 时间线布局
└── renderers/
    ├── NodeRenderer.tsx     # 节点渲染器
    ├── EdgeRenderer.tsx     # 边渲染器
    └── LabelRenderer.tsx    # 标签渲染器
```

### 4.3 图谱状态管理

```typescript
// stores/graphStore.ts
interface GraphState {
  // 数据
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNode: GraphNode | null;
  
  // 视图
  viewMode: 'industry' | 'customer' | 'event' | 'cluster';
  layout: 'force' | 'circular' | 'hierarchical' | 'timeline';
  zoom: number;
  center: [number, number];
  
  // 筛选
  filters: {
    industries: string[];
    sentimentRange: [number, number];
    timeRange: [Date, Date];
    entityTypes: string[];
  };
  
  // 操作
  loadGraph: (viewMode: string) => Promise<void>;
  selectNode: (node: GraphNode) => void;
  applyFilters: (filters: Filters) => void;
  exportGraph: (format: 'png' | 'svg') => void;
}
```

---

## 五、后端 API 设计

### 5.1 图谱数据 API

```yaml
# 获取行业全景图
GET /api/v1/graph/industry-overview
Query:
  - industries: string[]  # 筛选行业
  - timeRange: string     # 时间范围
Response:
  {
    "nodes": [
      {
        "id": "uuid",
        "type": "Customer",
        "name": "某科技公司",
        "industry": "科技",
        "sentiment_score": 0.75,
        "influence_level": "high",
        "article_count": 120
      }
    ],
    "edges": [
      {
        "id": "uuid",
        "source": "node_id_1",
        "target": "node_id_2",
        "type": "COMPETITOR",
        "weight": 0.8
      }
    ],
    "statistics": {
      "total_nodes": 1000,
      "total_edges": 5000,
      "sentiment_distribution": {...}
    }
  }

# 获取客户关系图
GET /api/v1/graph/customer-network/{customer_id}
Query:
  - depth: number        # 关联深度（1-3）
  - relationTypes: string[]  # 关系类型

# 获取事件演变图
GET /api/v1/graph/event-evolution/{event_id}
Query:
  - includeArticles: boolean

# 获取热点聚类图
GET /api/v1/graph/hotspot-clusters
Query:
  - industry: string
  - limit: number
```

### 5.2 舆情分析 API

```yaml
# 获取实体评分
GET /api/v1/sentiment/entity/{entity_id}
Response:
  {
    "entity_id": "uuid",
    "entity_name": "某科技公司",
    "sentiment_score": {
      "overall": 0.75,
      "dimensions": {...}
    },
    "trend": [...],
    "recent_articles": [...]
  }

# 获取行业舆情趋势
GET /api/v1/sentiment/industry/{industry}/trend
Query:
  - period: string  # day/week/month

# 舆情预警列表
GET /api/v1/sentiment/alerts
Query:
  - severity: string  # high/medium/low
  - status: string    # active/resolved
```

---

## 六、数据库设计

### 6.1 PostgreSQL 新增表

```sql
-- 舆情文章表
CREATE TABLE sentiment_articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(500) NOT NULL,
  source VARCHAR(100) NOT NULL,
  source_type VARCHAR(20),  -- news/social/announcement
  url VARCHAR(1000),
  content TEXT,
  publish_time TIMESTAMP,
  sentiment_score JSONB,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_articles_source ON sentiment_articles(source);
CREATE INDEX idx_articles_publish_time ON sentiment_articles(publish_time);

-- 客户信息表
CREATE TABLE customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  industry VARCHAR(50) NOT NULL,
  level VARCHAR(20),  -- strategic/key/regular
  tags JSONB DEFAULT '[]',
  sentiment_score FLOAT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_customers_industry ON customers(industry);
CREATE INDEX idx_customers_name ON customers(name);

-- 舆情事件表
CREATE TABLE sentiment_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(500) NOT NULL,
  type VARCHAR(50),  -- risk/opportunity/trend
  severity VARCHAR(20),  -- high/medium/low
  status VARCHAR(20),  -- active/resolved/closed
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  affected_customers UUID[],
  sentiment_impact JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_type ON sentiment_events(type);
CREATE INDEX idx_events_severity ON sentiment_events(severity);

-- 评分记录表
CREATE TABLE sentiment_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID NOT NULL,
  score_overall FLOAT,
  score_emotion FLOAT,
  score_influence FLOAT,
  score_timeliness FLOAT,
  score_credibility FLOAT,
  article_id UUID,
  calculated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scores_entity ON sentiment_scores(entity_type, entity_id);
```

### 6.2 Neo4j 图谱模型

```cypher
// 创建客户节点
CREATE (c:Customer {
  id: "uuid",
  name: "某科技公司",
  industry: "科技",
  level: "key",
  sentiment_score: 0.75
})

// 创建事件节点
CREATE (e:Event {
  id: "uuid",
  title: "产品发布事件",
  type: "opportunity",
  severity: "medium",
  status: "active"
})

// 创建文章节点
CREATE (a:Article {
  id: "uuid",
  title: "某科技公司发布新产品",
  source: "新浪科技",
  publish_time: datetime(),
  sentiment_score: 0.8
})

// 创建关系
MATCH (c:Customer {id: "customer_id"})
MATCH (e:Event {id: "event_id"})
CREATE (c)-[:INVOLVED_IN {role: "主角"}]->(e)

MATCH (c:Customer {id: "customer_id"})
MATCH (a:Article {id: "article_id"})
CREATE (c)-[:MENTIONED_IN {sentiment: "positive", score: 0.8}]->(a)

// 查询客户网络
MATCH (c:Customer {id: $customer_id})
CALL apoc.path.subgraphAll(c, {
  maxDepth: 2,
  relationshipFilter: "INVOLVED_IN|MENTIONED_IN|COMPETITOR|PARTNER"
})
YIELD nodes, relationships
RETURN nodes, relationships
```

---

## 七、数据采集流程

### 7.1 OpenClaw 采集任务

```yaml
# 采集任务配置
tasks:
  - name: "科技行业新闻采集"
    type: "web_crawler"
    sources:
      - "https://tech.sina.com.cn"
      - "https://www.36kr.com"
      - "https://www.pingwest.com"
    schedule: "0 */2 * * *"  # 每2小时
    parser: "news_parser"
    
  - name: "社交媒体采集"
    type: "social_monitor"
    platforms:
      - "weibo"
      - "twitter"
    keywords:
      - "${customer_names}"
    schedule: "0 * * * *"  # 每小时
    
  - name: "公告采集"
    type: "announcement_crawler"
    sources:
      - "http://www.sse.com.cn"
      - "http://www.szse.cn"
    schedule: "0 9,15,21 * * *"  # 每日三次
```

### 7.2 数据处理流水线

```
原始数据 → 清洗 → 实体识别 → 关系抽取 → 情感分析 → 评分计算 → 入库
   │        │        │          │          │          │        │
   └────────┴────────┴──────────┴──────────┴──────────┴────────┘
                         OpenClaw + NLP Pipeline
```

---

## 八、实现计划

### Phase 1: 基础框架（2周）
- [ ] 创建数据库表结构
- [ ] 实现 Neo4j 图谱模型
- [ ] 开发基础 API 接口
- [ ] 搭建前端图谱组件

### Phase 2: 数据采集（2周）
- [ ] 开发 OpenClaw 采集任务
- [ ] 实现 NLP 处理流水线
- [ ] 开发情感分析模型
- [ ] 实现评分计算逻辑

### Phase 3: 可视化（2周）
- [ ] 开发力导向图布局
- [ ] 实现节点/边渲染
- [ ] 开发交互功能
- [ ] 实现详情面板

### Phase 4: 高级功能（2周）
- [ ] 开发事件演变图
- [ ] 实现热点聚类
- [ ] 开发预警系统
- [ ] 性能优化

---

## 九、技术亮点

1. **知识图谱可视化**：基于 D3.js 的交互式图谱，支持多视图切换
2. **实时舆情分析**：OpenClaw 自动采集 + NLP 实时分析
3. **多维度评分**：情感/影响力/时效/可信度四维评分体系
4. **智能预警**：基于图谱的风险事件识别和推送
5. **行业定制**：针对制造、能源、金融、科技四大行业的定制化分析

---

**文档版本**: V1.0  
**创建日期**: 2026-03-30  
**更新日期**: 2026-03-30
