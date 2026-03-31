#!/usr/bin/env python3
"""部署ERC-KG"""
import paramiko
import time
import os

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
        if err and "Requirement" not in err[:20]:
            print(f"ERR: {err[:500]}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("OK")
    
    # 停止服务
    print("\n=== 停止旧服务 ===")
    run(ssh, "pkill -f uvicorn || true")
    
    # 上传简化版main.py
    print("\n=== 上传文件 ===")
    sftp = ssh.open_sftp()
    
    # 创建配置文件
    config_content = '''from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    llm_model: str = "gpt-4"
    secret_key: str = "dev-secret"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
    
    # 上传config
    with sftp.file(f"{REMOTE_PATH}/backend/app/core/config.py", 'w') as f:
        f.write(config_content)
    print("上传 config.py")
    
    # 上传简化版main
    main_content = open("C:/Projects/erc-kg-system/backend/app/main_simple.py").read()
    with sftp.file(f"{REMOTE_PATH}/backend/app/main.py", 'w') as f:
        f.write(main_content)
    print("上传 main.py")
    
    sftp.close()
    
    # 安装依赖
    print("\n=== 安装依赖 ===")
    run(ssh, "pip3 install --user fastapi uvicorn pydantic python-dotenv")
    
    # 启动服务
    print("\n=== 启动服务 ===")
    run(ssh, f"cd {REMOTE_PATH}/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/erc.log 2>&1 &")
    
    time.sleep(3)
    
    # 检查
    print("\n=== 检查 ===")
    run(ssh, "curl -s http://localhost:8000/")
    run(ssh, "tail -10 /tmp/erc.log")
    
    ssh.close()
    print("\n完成! http://chuansha.tech:8000/docs")

if __name__ == "__main__":
    main()
