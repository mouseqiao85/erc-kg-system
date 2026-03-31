#!/usr/bin/env python3
"""完全替换部署ERC-KG"""
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
        if err:
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
    
    # 停止所有Python和Node进程
    print("\n=== 停止所有服务 ===")
    run(ssh, "pkill -9 python3 || true")
    run(ssh, "pkill -9 node || true")
    run(ssh, "sleep 2")
    
    # 修改requirements.txt兼容阿里云镜像
    print("\n=== 修改依赖版本 ===")
    run(ssh, f'''cat > {REMOTE_PATH}/backend/requirements.txt << 'EOF'
fastapi>=0.80.0
uvicorn>=0.2.0
sqlalchemy>=1.4.0
psycopg2-binary>=2.9.0
neo4j>=4.0.0
redis>=4.0.0
openai>=1.0.0
python-multipart
pydantic>=1.0.0
python-dotenv
python-jose
passlib
python-docx
pypdf2
aiofiles
jieba
feedparser
aiohttp
EOF
''')
    
    # 安装依赖
    print("\n=== 安装依赖 ===")
    run(ssh, f"cd {REMOTE_PATH}/backend && pip3 install -r requirements.txt", timeout=300)
    
    # 启动后端
    print("\n=== 启动后端 ===")
    run(ssh, f"cd {REMOTE_PATH}/backend && export PYTHONPATH={REMOTE_PATH}/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/erc-backend.log 2>&1 &")
    
    time.sleep(3)
    
    # 检查后端
    print("\n=== 检查后端 ===")
    run(ssh, "curl -s http://localhost:8000/ || cat /tmp/erc-backend.log | tail -20")
    
    ssh.close()
    print("\n完成!")

if __name__ == "__main__":
    main()
