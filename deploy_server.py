#!/usr/bin/env python3
"""部署ERC-KG到服务器 8.215.63.182"""
import paramiko
import time

HOST = "8.215.63.182"
USER = "root"
PASSWORD = "q@851018"
REMOTE_PATH = "/opt/erc-kg-system"

def run(ssh, cmd, timeout=180):
    print(f"> {cmd[:60]}...")
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out:
            print(out[:1500])
        if err and "Requirement" not in err[:20]:
            print(f"ERR: {err[:400]}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("OK")
    
    # 检查Docker
    print("\n=== 检查Docker ===")
    run(ssh, "docker --version")
    run(ssh, "docker-compose --version")
    
    # 克隆项目
    print("\n=== 克隆项目 ===")
    run(ssh, f"rm -rf {REMOTE_PATH}")
    run(ssh, f"git clone https://github.com/mouseqiao85/erc-kg-system.git {REMOTE_PATH}")
    
    # 配置环境
    print("\n=== 配置环境 ===")
    run(ssh, f"cp {REMOTE_PATH}/.env.example {REMOTE_PATH}/.env")
    
    # 启动Docker服务
    print("\n=== 启动Docker服务 ===")
    run(ssh, f"cd {REMOTE_PATH} && docker-compose up -d --build", timeout=600)
    
    time.sleep(10)
    
    # 检查状态
    print("\n=== 检查容器状态 ===")
    run(ssh, "docker ps")
    
    ssh.close()
    print("\n完成! http://8.215.63.182:8000/docs")

if __name__ == "__main__":
    main()
