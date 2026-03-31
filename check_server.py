#!/usr/bin/env python3
"""检查服务器状态"""
import paramiko

HOST = "8.215.63.182"
USER = "root"
PASSWORD = "q@851018"

def run(ssh, cmd):
    print(f"> {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out)
    if err:
        print(f"ERR: {err}")
    return out

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)

print("=== Docker容器 ===")
run(ssh, "docker ps -a")

print("\n=== Docker日志 ===")
run(ssh, "docker-compose -f /opt/erc-kg-system/docker-compose.yml logs --tail=30")

print("\n=== 端口 ===")
run(ssh, "netstat -tlnp | grep -E '8000|3000'")

ssh.close()
