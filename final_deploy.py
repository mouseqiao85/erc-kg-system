#!/usr/bin/env python3
"""ERC-KG 重新部署"""
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
        if err and "warning" not in err.lower()[:100]:
            print(f"ERR: {err[:500]}")
    except:
        print("Timeout, continuing...")
    return

def main():
    print("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("OK")
    
    # 更新代码
    print("\n=== 更新代码 ===")
    run(ssh, f"cd {REMOTE_PATH} && git pull")
    
    # 安装依赖
    print("\n=== 安装后端依赖 ===")
    run(ssh, f"cd {REMOTE_PATH}/backend && pip3 install -r requirements.txt", timeout=300)
    
    # 启动后端
    print("\n=== 启动后端 ===")
    run(ssh, "pkill -f 'uvicorn.*8000' 2>/dev/null || true")
    run(ssh, f"cd {REMOTE_PATH}/backend && export PYTHONPATH=/opt/erc-kg/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &")
    
    # 启动前端
    print("\n=== 启动前端 ===")
    run(ssh, "pkill -f 'vite.*3000' 2>/dev/null || true")
    run(ssh, f"cd {REMOTE_PATH}/frontend && nohup npm run dev -- --host 0.0.0.0 --port 3000 > /tmp/frontend.log 2>&1 &")
    
    time.sleep(5)
    
    # 检查
    print("\n=== 检查服务 ===")
    run(ssh, "sleep 3 && curl -s http://localhost:8000/ || echo 'Backend starting...'")
    run(ssh, "curl -s http://localhost:3000/ | head -5 || echo 'Frontend starting...'")
    
    ssh.close()
    print("\n完成! http://chuansha.tech:8000/docs")

if __name__ == "__main__":
    main()
