#!/bin/bash

# ERC-KG 部署脚本 - 在服务器上运行
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e

echo "=========================================="
echo "ERC-KG 自动化部署脚本"
echo "=========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
  echo "请使用root用户运行: sudo ./deploy.sh"
  exit 1
fi

# 更新系统
echo "[1/7] 更新系统包..."
apt-get update -y
apt-get upgrade -y

# 安装Docker
echo "[2/7] 安装Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sh /tmp/get-docker.sh
    rm /tmp/get-docker.sh
    systemctl start docker
    systemctl enable docker
fi

# 安装Docker Compose
echo "[3/7] 安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 创建项目目录
echo "[4/7] 创建项目目录..."
mkdir -p /var/www
cd /var/www

# 克隆或更新项目
echo "[5/7] 获取项目代码..."
if [ -d "erc-kg-system/.git" ]; then
    cd erc-kg-system
    git pull
else
    git clone https://github.com/mouseqiao85/erc-kg-system.git
    cd erc-kg-system
fi

# 配置环境变量
echo "[6/7] 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "请编辑 .env 文件设置 OPENAI_API_KEY"
fi

# 编辑环境变量 - 添加你的API Key
# 如果有API Key，直接写入
if [ -n "$OPENAI_API_KEY" ]; then
    sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$OPENAI_API_KEY/" .env
fi

# 启动服务
echo "[7/7] 启动Docker服务..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

echo ""
echo "=========================================="
echo "部署完成!"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  前端: http://$(hostname -I | awk '{print $1}'):3000"
echo "  后端: http://$(hostname -I | awk '{print $1}'):8000"
echo "  API文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "如需配置域名，请在 /etc/nginx/sites-available/ 配置 Nginx"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
