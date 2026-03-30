# ERC-KG 部署指南

## 方式一：Docker Compose 一键部署

### 1. 上传项目到服务器

将整个 `erc-kg-system` 文件夹上传到服务器 `/var/www/` 目录

### 2. 配置环境变量

```bash
cd /var/www/erc-kg-system
cp .env.example .env
nano .env
```

编辑 `.env` 文件，添加你的 OpenAI API Key：
```
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-secret-key
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 访问地址

- 前端: http://chuansha.tech
- 后端API: http://chuansha.tech:8000
- API文档: http://chuansha.tech:8000/docs
- Neo4j: http://chuansha.tech:7474

---

## 方式二：手动部署（不使用Docker）

### 后端

```bash
# 安装Python依赖
cd backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 添加 OPENAI_API_KEY

# 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端

```bash
# 安装依赖
cd frontend
npm install

# 构建
npm run build

# 开发模式
npm run dev -- --host 0.0.0.0
```

---

## Nginx 配置

如果需要域名访问，配置 Nginx：

```nginx
server {
    listen 80;
    server_name chuansha.tech;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
```

---

## 快速部署命令

在服务器上执行：

```bash
cd /var/www/erc-kg-system
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

查看日志：
```bash
docker-compose logs -f
```
