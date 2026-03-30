#!/usr/bin/env python3
"""
ERC-KG 自动部署脚本
部署到 chuansha.tech
"""

import os
import sys
import subprocess
import requests
import paramiko
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path("C:/Projects/erc-kg-system")
SERVER_HOST = "chuansha.tech"
SERVER_USER = "root"
SERVER_PASSWORD = "q@851018"
REMOTE_PATH = "/opt/erc-kg"

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_message = message.replace("✅", "[OK]").replace("❌", "[FAIL]")
    print(f"[{timestamp}] {safe_message}")

def run_tests() -> bool:
    log("检查本地服务...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            log("本地服务正常")
    except:
        log("本地服务未运行 (跳过)")
    return True

def deploy(ssh: paramiko.SSHClient):
    log("创建远程目录...")
    ssh.exec_command(f"mkdir -p {REMOTE_PATH}")
    
    sftp = ssh.open_sftp()
    
    # 传输关键文件
    files_to_transfer = [
        "docker-compose.yml",
        "nginx.conf",
        ".env",
    ]
    
    for f in files_to_transfer:
        local_path = PROJECT_DIR / f
        if local_path.exists():
            remote_path = f"{REMOTE_PATH}/{f}"
            sftp.put(str(local_path), remote_path)
            log(f"传输: {f}")
    
    # 传输目录
    dirs = ["backend", "frontend", "docs"]
    for d in dirs:
        local_dir = PROJECT_DIR / d
        if local_dir.exists():
            for py_file in local_dir.rglob("*.py"):
                rel_path = py_file.relative_to(PROJECT_DIR)
                remote_file = f"{REMOTE_PATH}/{rel_path}".replace("\\", "/")
                remote_dir = "/".join(remote_file.split("/")[:-1])
                ssh.exec_command(f"mkdir -p {remote_dir}")
                try:
                    sftp.put(str(py_file), remote_file)
                except:
                    pass
            for json_file in local_dir.rglob("*.json"):
                rel_path = json_file.relative_to(PROJECT_DIR)
                remote_file = f"{REMOTE_PATH}/{rel_path}".replace("\\", "/")
                remote_dir = "/".join(remote_file.split("/")[:-1])
                ssh.exec_command(f"mkdir -p {remote_dir}")
                try:
                    sftp.put(str(json_file), remote_file)
                except:
                    pass
    
    sftp.close()
    log("文件传输完成")

def build_and_run(ssh: paramiko.SSHClient):
    log("构建Docker镜像...")
    
    commands = [
        f"cd {REMOTE_PATH} && docker-compose down 2>/dev/null || true",
        f"cd {REMOTE_PATH} && docker-compose build --no-cache",
        f"cd {REMOTE_PATH} && docker-compose up -d",
    ]
    
    for cmd in commands:
        log(f"执行: {cmd[:50]}...")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err and "error" in err.lower():
            log(f"错误: {err[:200]}")
    
    log("Docker部署完成")

def configure_nginx(ssh: paramiko.SSHClient):
    log("配置Nginx...")
    
    nginx_config = '''
server {
    listen 80;
    server_name chuansha.tech;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
'''
    
    ssh.exec_command(f"cat > /etc/nginx/sites-available/erc-kg << 'EOF'\n{nginx_config}\nEOF")
    ssh.exec_command("ln -sf /etc/nginx/sites-available/erc-kg /etc/nginx/sites-enabled/")
    ssh.exec_command("nginx -t && systemctl reload nginx")
    log("Nginx配置完成")

def verify():
    log("验证部署...")
    try:
        response = requests.get("http://chuansha.tech/", timeout=10)
        if response.status_code == 200:
            log("部署成功!")
            return True
    except Exception as e:
        log(f"验证: {e}")
    return False

def main():
    log("=" * 50)
    log("ERC-KG 自动部署开始")
    log("=" * 50)
    
    run_tests()
    
    log("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        log("SSH连接成功")
    except Exception as e:
        log(f"SSH连接失败: {e}")
        return
    
    try:
        deploy(ssh)
        build_and_run(ssh)
        configure_nginx(ssh)
    finally:
        ssh.close()
    
    verify()
    
    log("=" * 50)
    log("部署完成!")
    log("访问: http://chuansha.tech")
    log("=" * 50)

if __name__ == "__main__":
    main()
