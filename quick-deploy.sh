#!/bin/bash
# ERC-KG 一键部署脚本
# 使用: curl -sSL https://raw.githubusercontent.com/mouseqiao85/erc-kg-system/main/deploy-erc-kg.sh | bash

set -e

echo "=== ERC-KG 部署开始 ==="

# 配置
PROJECT_DIR="/var/www/erc-kg-system"
OPENAI_KEY="${OPENAI_API_KEY:-}"

# 安装Docker
if ! command -v docker &> /dev/null; then
    echo "安装Docker..."
    apt-get update
    apt-get install -y curl
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker $USER
fi

# 启动Docker
systemctl start docker || service docker start

# 克隆项目
echo "获取项目代码..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR
git clone https://github.com/mouseqiao85/erc-kg-system.git .

# 配置环境变量
echo "配置环境变量..."
cp .env.example .env 2>/dev/null || true

if [ -n "$OPENAI_KEY" ]; then
    echo "OPENAI_API_KEY=$OPENAI_KEY" >> .env
fi

# 启动服务
echo "启动服务..."
docker-compose up -d --build

echo ""
echo "=== 部署完成 ==="
echo "前端: http://你的服务器IP:3000"
echo "后端: http://你的服务器IP:8000"
echo "API文档: http://你的服务器IP:8000/docs"
