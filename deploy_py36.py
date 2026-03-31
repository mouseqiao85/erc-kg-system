#!/usr/bin/env python3
"""部署ERC-KG - 适配Python 3.6"""
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
        if err and "Requirement already" not in err:
            print(f"ERR: {err[:600]}")
    except Exception as e:
        print(f"Error: {e}")
    return

def main():
    print("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("OK")
    
    # 检查Python版本
    print("\n=== Python版本 ===")
    run(ssh, "python3 --version")
    run(ssh, "which python3")
    
    # 停止服务
    print("\n=== 停止服务 ===")
    run(ssh, "pkill -f 'uvicorn.*8000' || true")
    run(ssh, "pkill -f 'main:app' || true")
    
    # 创建兼容Python 3.6的requirements
    print("\n=== 创建依赖文件 ===")
    run(ssh, f'''cat > {REMOTE_PATH}/backend/requirements.txt << 'EOF'
fastapi==0.68.0
uvicorn==0.15.0
sqlalchemy==1.4.54
psycopg2-binary==2.9.5
neo4j==4.4.13
redis==4.3.6
openai==0.10.5
python-multipart
pydantic<2.0
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
    run(ssh, f"cd {REMOTE_PATH}/backend && pip3 install --user -r requirements.txt", timeout=300)
    
    # 启动后端
    print("\n=== 启动后端 ===")
    run(ssh, f"cd {REMOTE_PATH}/backend && PYTHONPATH={REMOTE_PATH}/backend nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/erc-backend.log 2>&1 &")
    
    time.sleep(5)
    
    # 检查后端
    print("\n=== 检查后端 ===")
    run(ssh, "curl -s http://localhost:8000/")
    run(ssh, "tail -30 /tmp/erc-backend.log")
    
    ssh.close()
    print("\n完成! http://chuansha.tech:8000/docs")

if __name__ == "__main__":
    main()
