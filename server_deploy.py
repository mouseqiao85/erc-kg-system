#!/usr/bin/env python3
"""
ERC-KG 部署脚本 - 直接在服务器执行
"""

import subprocess
import sys

def run(cmd):
    print(f"> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and "error" not in result.stderr.lower():
        print(result.stderr)
    return result.returncode

def main():
    cmds = [
        "apt update && apt install -y docker.io docker-compose git",
        "mkdir -p /opt/erc-kg && cd /opt/erc-kg",
        "git clone https://github.com/mouseqiao85/erc-kg-system.git .",
        "cp .env.example .env",
        "echo 'OPENAI_API_KEY=sk-your-key' >> .env",
        "docker-compose up -d --build"
    ]
    
    for cmd in cmds:
        if run(cmd) != 0:
            print("命令失败")
            return
    
    print("=== 部署完成 ===")
    print("访问 http://chuansha.tech")

if __name__ == "__main__":
    main()
