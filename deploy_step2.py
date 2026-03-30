#!/usr/bin/env python3
"""ERC-KG 部署脚本 - 第2步"""
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
        print(out[:1000])
    if err:
        print(f"ERR: {err[:500]}")
    return out, err

def main():
    print("连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("连接成功!")
    
    # 创建.env文件
    print("\n=== 创建环境配置 ===")
    env_content = """OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=dev-secret-key
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/erc_kg
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
REDIS_URL=redis://redis:6379
"""
    cmd = f'''cat > {REMOTE_PATH}/.env << 'EOF'
{env_content}
EOF'''
    run(ssh, cmd)
    run(ssh, f"cat {REMOTE_PATH}/.env")
    
    # 启动服务
    print("\n=== 启动Docker服务 ===")
    run(ssh, f"cd {REMOTE_PATH} && docker-compose ps")
    run(ssh, f"cd {REMOTE_PATH} && docker-compose up -d")
    
    # 等待服务启动
    print("\n等待服务启动...")
    time.sleep(30)
    
    # 检查状态
    print("\n=== 检查容器状态 ===")
    run(ssh, "docker ps -a")
    
    # 检查日志
    print("\n=== 后端日志 ===")
    run(ssh, f"cd {REMOTE_PATH} && docker-compose logs backend 2>&1 | tail -20")
    
    # 检查端口
    print("\n=== 检查端口 ===")
    run(ssh, "netstat -tlnp | grep -E '8000|3000|5432|7474'")
    
    ssh.close()
    print("\n完成!")

if __name__ == "__main__":
    main()
