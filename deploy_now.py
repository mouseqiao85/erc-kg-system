#!/usr/bin/env python3
"""ERC-KG 部署脚本"""
import paramiko
import time

HOST = "chuansha.tech"
USER = "root"
PASSWORD = "q@851018"
REMOTE_PATH = "/opt/erc-kg"

def run(ssh, cmd):
    print(f"> {cmd[:80]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out[:800])
    if err and "warning" not in err.lower():
        print(f"ERR: {err[:400]}")
    return out, err

def main():
    print("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("连接成功!")
    
    # 检测系统
    print("\n=== 检测系统 ===")
    run(ssh, "cat /etc/os-release")
    run(ssh, "which docker")
    run(ssh, "which docker-compose")
    
    # 清理并重新克隆
    print("\n=== 清理并克隆项目 ===")
    run(ssh, f"rm -rf {REMOTE_PATH}")
    run(ssh, f"mkdir -p {REMOTE_PATH}")
    run(ssh, f"cd {REMOTE_PATH} && git clone https://github.com/mouseqiao85/erc-kg-system.git .")
    
    # 配置环境
    print("\n=== 配置环境 ===")
    run(ssh, f"cd {REMOTE_PATH} && cp .env.example .env")
    
    # 检查docker-compose
    print("\n=== Docker Compose文件 ===")
    run(ssh, f"cd {REMOTE_PATH} && ls -la")
    run(ssh, f"cd {REMOTE_PATH} && cat docker-compose.yml | head -30")
    
    # 启动服务
    print("\n=== 启动服务 ===")
    run(ssh, f"cd {REMOTE_PATH} && docker-compose down 2>/dev/null || true")
    run(ssh, f"cd {REMOTE_PATH} && docker-compose up -d --build")
    
    # 检查状态
    print("\n=== 检查状态 ===")
    run(ssh, "docker ps")
    
    ssh.close()
    print("\n部署完成!")

if __name__ == "__main__":
    main()
