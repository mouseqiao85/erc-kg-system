#!/usr/bin/env python3
"""检查ERC-KG服务状态"""
import paramiko
import requests

HOST = "chuansha.tech"
USER = "root"
PASSWORD = "q@851018"

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out[:1500])
    return out

def main():
    print("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    
    print("\n=== Docker容器 ===")
    run(ssh, "docker ps")
    
    print("\n=== 检查后端服务 ===")
    run(ssh, "curl -s http://localhost:8000/ || echo 'Backend not responding'")
    
    print("\n=== 检查前端服务 ===")
    run(ssh, "curl -s http://localhost:3000/ | head -20 || echo 'Frontend not responding'")
    
    print("\n=== 检查API文档 ===")
    run(ssh, "curl -s http://localhost:8000/docs | head -10 || echo 'API docs not available'")
    
    ssh.close()
    
    # 测试外部访问
    print("\n=== 测试外部访问 ===")
    try:
        r = requests.get("http://chuansha.tech:8000/", timeout=10)
        print(f"后端状态: {r.status_code}")
    except Exception as e:
        print(f"后端访问失败: {e}")
    
    try:
        r = requests.get("http://chuansha.tech:3000/", timeout=10)
        print(f"前端状态: {r.status_code}")
    except Exception as e:
        print(f"前端访问失败: {e}")

if __name__ == "__main__":
    main()
