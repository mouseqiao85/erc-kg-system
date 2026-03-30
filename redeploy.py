#!/usr/bin/env python3
"""重新部署ERC-KG"""
import paramiko
import time

HOST = "chuansha.tech"
USER = "root"
PASSWORD = "q@851018"
REMOTE_PATH = "/opt/erc-kg"

def run(ssh, cmd, timeout=120):
    print(f"> {cmd[:70]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out[:2000])
    if err and "warning" not in err.lower()[:100]:
        print(f"ERR: {err[:600]}")
    return out, err

def main():
    print("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("OK")
    
    # 停止旧服务
    print("\n=== 停止旧服务 ===")
    run(ssh, "pkill -f 'uvicorn' || true")
    run(ssh, "pkill -f 'node.*3000' || true")
    
    # 更新代码
    print("\n=== 更新代码 ===")
    run(ssh, f"cd {REMOTE_PATH} && git pull")
    
    # 创建.env
    print("\n=== 配置环境 ===")
    run(ssh, f'''cat > {REMOTE_PATH}/.env << 'ENVEOF'
OPENAI_API_KEY=sk-test-key
SECRET_KEY=erc-kg-secret-2024
DEBUG=true
ENVEOF
''')
    
    # 安装Python依赖并启动后端
    print("\n=== 启动后端 ===")
    run(ssh, f"cd {REMOTE_PATH}/backend && pip3 install -r requirements.txt 2>&1 | tail -5", timeout=180)
    run(ssh, f"cd {REMOTE_PATH}/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &")
    
    # 安装前端依赖并启动
    print("\n=== 启动前端 ===")
    run(ssh, f"cd {REMOTE_PATH}/frontend && npm install 2>&1 | tail -5", timeout=180)
    run(ssh, f"cd {REMOTE_PATH}/frontend && nohup npm run dev -- --host 0.0.0.0 --port 3000 > /tmp/frontend.log 2>&1 &")
    
    # 等待启动
    print("\n等待服务启动...")
    time.sleep(10)
    
    # 检查状态
    print("\n=== 检查状态 ===")
    run(ssh, "curl -s http://localhost:8000/")
    run(ssh, "curl -s http://localhost:3000/ | head -10")
    run(ssh, "netstat -tlnp | grep -E '8000|3000'")
    
    ssh.close()
    print("\n完成! 访问 http://chuansha.tech")

if __name__ == "__main__":
    main()
