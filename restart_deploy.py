#!/usr/bin/env python3
"""完全重启ERC-KG"""
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
    
    # 完全停止
    print("\n=== 停止所有Python进程 ===")
    run(ssh, "ps aux | grep python")
    run(ssh, "kill -9 $(pgrep python) 2>/dev/null || true")
    run(ssh, "sleep 2")
    run(ssh, "ps aux | grep python || echo 'No python processes'")
    
    # 上传文件
    print("\n=== 上传简化版文件 ===")
    sftp = ssh.open_sftp()
    
    # 清空__init__.py
    with sftp.file(f"{REMOTE_PATH}/backend/app/__init__.py", 'w') as f:
        f.write("")
    print("清空 __init__.py")
    
    # 创建空的core/__init__.py
    with sftp.file(f"{REMOTE_PATH}/backend/app/core/__init__.py", 'w') as f:
        f.write("")
    print("清空 core/__init__.py")
    
    # 上传简化main
    main_content = open("C:/Projects/erc-kg-system/backend/app/main_simple.py").read()
    with sftp.file(f"{REMOTE_PATH}/backend/app/main.py", 'w') as f:
        f.write(main_content)
    print("上传 main.py")
    
    sftp.close()
    
    # 启动
    print("\n=== 启动服务 ===")
    run(ssh, f"cd {REMOTE_PATH}/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/erc.log 2>&1 &")
    
    time.sleep(5)
    
    # 检查
    print("\n=== 检查 ===")
    run(ssh, "curl -s http://localhost:8000/")
    run(ssh, "curl -s http://localhost:8000/health")
    run(ssh, "cat /tmp/erc.log | tail -15")
    
    ssh.close()
    print("\n完成! http://chuansha.tech:8000/docs")

if __name__ == "__main__":
    main()
