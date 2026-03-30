# ERC-KG Deployment Script

## 1. Upload project to server
```bash
# From local machine, copy project to server
scp -r /path/to/erc-kg-system root@8.215.63.182:~/
```

## 2. Server setup commands

```bash
# SSH to server
ssh root@8.215.63.182

# Install Python dependencies
cd ~/erc-kg-system/backend
pip install -r requirements.txt

# Install Node.js dependencies
cd ~/erc-kg-system/frontend
npm install

# Configure environment
cp .env.example .env
nano .env  # Edit with your database credentials
```

## 3. Start services

```bash
# Start backend (port 8000)
cd ~/erc-kg-system/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start frontend (port 3000)
cd ~/erc-kg-system/frontend
npm run dev -- --host 0.0.0.0
```

## 4. Nginx (optional, for production)

```bash
# Install nginx
apt install nginx

# Create nginx config
nano /etc/nginx/sites-available/erc-kg

# Content:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}

# Enable site
ln -s /etc/nginx/sites-available/erc-kg /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx
```
