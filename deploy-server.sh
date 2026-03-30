#!/bin/bash

# ERC-KG Deployment Script for Chuansha Server
# Run: chmod +x deploy-server.sh && ./deploy-server.sh

set -e

echo "=== ERC-KG Deployment Script ==="

# Update system
echo "Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl start docker
    systemctl enable docker
fi

# Install Docker Compose
echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create project directory
echo "Setting up project directory..."
mkdir -p /var/www/erc-kg-system
cd /var/www/erc-kg-system

# If git repository exists, pull latest
if [ -d ".git" ]; then
    echo "Pulling latest from Git..."
    git pull
else
    echo "Cloning repository..."
    # Replace with your repository URL
    git clone https://github.com/mouseqiao85/erc-kg-system.git .
fi

# Create environment file
echo "Setting up environment..."
cp .env.example .env 2>/dev/null || true

# Edit .env with your settings
echo "Please edit /var/www/erc-kg-system/.env with your API keys!"
echo "Required: OPENAI_API_KEY"

# Build and start containers
echo "Building containers..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache

echo "Starting services..."
docker-compose up -d

echo "=== Deployment Complete ==="
echo "Services starting..."
sleep 10
docker-compose ps

echo ""
echo "=== Access URLs ==="
echo "Frontend: http://chuansha.tech:3000"
echo "Backend API: http://chuansha.tech:8000"
echo "API Docs: http://chuansha.tech:8000/docs"
echo "Neo4j: http://chuansha.tech:7474"
