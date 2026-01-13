import paramiko
import os
import sys

# 服务器配置
HOST = '62.234.25.31'
PORT = 22
USERNAME = 'root'
PASSWORD = 'XCxc5200'

def get_logs():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"正在连接到服务器 {HOST}...")
        try:
            client.connect(HOST, PORT, 'ubuntu', PASSWORD)
            print("ubuntu 用户连接成功")
        except:
            client.connect(HOST, PORT, USERNAME, PASSWORD)
            print("root 用户连接成功")
            
        # 获取最近的日志
        cmd = "sudo journalctl -u huozhema -n 50 --no-pager"
        print(f"执行命令: {cmd}")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        print("\n=== 日志开始 ===")
        print(stdout.read().decode('utf-8', errors='replace'))
        print("=== 日志结束 ===\n")
        
        err = stderr.read().decode('utf-8', errors='replace')
        if err:
            print(f"标准错误输出: {err}")
            
    except Exception as e:
        print(f"连接或执行失败: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    get_logs()
