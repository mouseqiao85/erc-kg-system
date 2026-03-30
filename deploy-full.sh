#!/bin/bash
# ERC-KG 一键部署脚本

set -e

echo "=== ERC-KG 部署脚本 ==="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "安装 Docker..."
    apt update && apt install -y docker.io
fi

if ! command -v docker-compose &> /dev/null; then
    echo "安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 启动 Docker
systemctl start docker || true
systemctl enable docker || true

echo "正在启动服务..."
docker-compose up -d

echo "等待服务就绪..."
sleep 30

echo "检查服务状态..."
docker-compose ps

echo ""
echo "=== 部署完成 ==="
echo "前端: http://$(hostname -I | awk '{print $1}'):3000"
echo "后端 API: http://$(hostname -I | awk '{print $1}'):8000"
echo "Neo4j: http://$(hostname -I | awk '{print $1}'):7474"
echo ""
echo "查看日志: docker-compose logs -f"
