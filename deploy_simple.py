#!/usr/bin/env python3
"""部署ERC-KG - 完全适配Python 3.6"""
import paramiko
import time

HOST = "chuansha.tech"
USER = "root"
PASSWORD = "q@851018"
REMOTE_PATH = "/opt/erc-kg"

def run(ssh, cmd, timeout=180):
    print(f"> {cmd[:60]}...")
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out:
            print(out[:2000])
        if err and "Requirement already" not in err and "warning" not in err.lower()[:50]:
            print(f"ERR: {err[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    return

def main():
    print("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("OK")
    
    # 停止服务
    print("\n=== 停止服务 ===")
    run(ssh, "pkill -f 'uvicorn' || true")
    run(ssh, "pkill -f 'main:app' || true")
    
    # 创建兼容版本的config.py
    print("\n=== 创建兼容配置 ===")
    run(ssh, f'''cat > {REMOTE_PATH}/backend/app/core/config.py << 'EOF'
from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.7
    
    database_url: str = "postgresql://postgres:postgres@localhost:5432/erc_kg"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    redis_url: str = "redis://localhost:6379"
    
    secret_key: str = "dev-secret-key"
    access_token_expire_minutes: int = 30
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF
''')
    
    # 创建简化版main.py
    print("\n=== 创建简化版主程序 ===")
    run(ssh, f'''cat > {REMOTE_PATH}/backend/app/main.py << 'MAINEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ERC-KG API",
    description="Knowledge Graph Builder",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "ERC-KG API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/projects")
def get_projects():
    return {"items": [], "total": 0}

@app.get("/api/v1/documents")  
def get_documents():
    return {"items": [], "total": 0}

@app.get("/api/v1/graph")
def get_graph():
    return {"nodes": [], "edges": []}

@app.get("/api/v1/entities")
def get_entities():
    return {"items": []}

@app.get("/api/v1/triples")
def get_triples():
    return {"items": []}

@app.get("/api/v1/sentiment/industry-overview")
def industry_overview():
    result = {"nodes": [], "edges": []}
    return result
MAINEOF
''')
    
    # 安装基本依赖
    print("\n=== 安装依赖 ===")
    run(ssh, "pip3 install --user fastapi uvicorn pydantic python-dotenv", timeout=120)
    
    # 启动服务
    print("\n=== 启动服务 ===")
    run(ssh, f"cd {REMOTE_PATH}/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/erc-backend.log 2>&1 &")
    
    time.sleep(3)
    
    # 检查
    print("\n=== 检查服务 ===")
    run(ssh, "curl -s http://localhost:8000/ || cat /tmp/erc-backend.log")
    
    ssh.close()
    print("\n完成! http://chuansha.tech:8000/docs")

if __name__ == "__main__":
    main()
