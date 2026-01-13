import paramiko
import os
import sys
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 服务器配置
HOST = '62.234.25.31'
PORT = 22
USERNAME = 'root'
PASSWORD = os.getenv('SERVER_PASSWORD', 'XCxc5200') # 优先从环境变量获取，保留默认值以便本地运行

# 本地项目路径
LOCAL_PATH = os.getcwd()
# 远程部署路径 (改为用户主目录)
REMOTE_PATH = '/home/ubuntu/huo-zhe-ma'

def create_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 优先尝试 ubuntu 用户
    try:
        print("尝试使用 ubuntu 用户连接...")
        client.connect(HOST, PORT, 'ubuntu', PASSWORD)
        print("ubuntu 用户连接成功！")
        return client
    except Exception as e:
        print(f"ubuntu 连接失败: {e}")
        try:
            print(f"正在连接到服务器 {HOST} (root)...")
            client.connect(HOST, PORT, USERNAME, PASSWORD)
            print("root 连接成功！")
            return client
        except Exception as e:
            print(f"root 连接失败: {e}")
            try:
                print("尝试使用 lighthouse 用户连接...")
                client.connect(HOST, PORT, 'lighthouse', PASSWORD)
                print("lighthouse 用户连接成功！")
                return client
            except Exception as e2:
                print(f"lighthouse 连接失败: {e2}")
                return None

def run_command(client, command, sudo=False):
    if sudo:
        command = f"sudo -n {command}"
    print(f"执行命令: {command}")
    
    # 使用 get_pty=True 以获得正确的缓冲行为
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    
    # 手动读取字节并解码，避免 UnicodeDecodeError
    while True:
        try:
            # 读取一行字节 (Paramiko 的 readline 可能在内部解码导致崩溃，所以我们用 recv 或 try-except)
            # 但为了简单起见，我们还是用 readline，但包裹在 try-except 中
            # 注意：Paramiko 的 File 对象在 readline 时会尝试解码
            # 如果我们想完全避免，应该直接操作 channel
            if stdout.channel.recv_ready():
                output_bytes = stdout.channel.recv(4096)
                if not output_bytes:
                    break
                print(output_bytes.decode('utf-8', errors='replace').strip())
            
            if stdout.channel.exit_status_ready() and not stdout.channel.recv_ready():
                break
                
            time.sleep(0.1)
        except Exception as e:
            # 忽略解码错误
            pass
        
    exit_status = stdout.channel.recv_exit_status()
    
    if exit_status != 0:
        print(f"错误: 命令执行失败，退出码: {exit_status}")
        return False
        
    return True

def upload_files(client):
    sftp = client.open_sftp()
    
    # 创建远程根目录
    run_command(client, f"mkdir -p {REMOTE_PATH}", sudo=True)
    run_command(client, f"chown -R ubuntu:ubuntu {REMOTE_PATH}", sudo=True)
    
    print("开始上传文件...")
    count = 0
    
    # 要上传的文件列表
    files_to_upload = [
        'requirements.txt', 'webapp.py', 'database.py', 'quotes.py'
    ]
    
    for file in files_to_upload:
        if os.path.exists(file):
            print(f"Uploading {file}...")
            sftp.put(file, f'{REMOTE_PATH}/{file}')
            count += 1
            
    # 2. 上传 templates 目录
    run_command(client, f"mkdir -p {REMOTE_PATH}/templates", sudo=True)
    run_command(client, f"chown -R ubuntu:ubuntu {REMOTE_PATH}/templates", sudo=True)
    
    template_files = ['home.html', 'login.html', 'register.html', 'config.html', 'admin.html']
    for file in template_files:
        local_path = os.path.join('templates', file)
        if os.path.exists(local_path):
            print(f"Uploading templates/{file}...")
            sftp.put(local_path, f'{REMOTE_PATH}/templates/{file}')
            count += 1
            
    sftp.close()
    print(f"文件上传完成，共 {count} 个文件")

def deploy():
    client = create_ssh_client()
    if not client:
        return

    # 1. 安装系统依赖
    print("\n--- 1. 安装系统依赖 ---")
    stdin, stdout, stderr = client.exec_command("cat /etc/os-release")
    os_info = stdout.read().decode().lower()
    
    pkg_mgr = 'apt-get'
    if 'centos' in os_info or 'tencentos' in os_info:
        pkg_mgr = 'yum'
    
    # 尝试更新，但不因失败而停止 (可能是锁问题)
    run_command(client, f"{pkg_mgr} update -y", sudo=True)
    run_command(client, f"{pkg_mgr} install -y python3 python3-pip git nginx", sudo=True)
    
    # 2. 上传文件
    print("\n--- 2. 上传项目文件 ---")
    upload_files(client)
    
    # 3. 安装 Python 依赖
    print("\n--- 3. 安装 Python 依赖 ---")
    run_command(client, "python3 -m pip install --upgrade pip", sudo=True)
    # 使用 --ignore-installed 强制重装/升级包 (解决系统包冲突)
    run_command(client, f"python3 -m pip install --ignore-installed -r {REMOTE_PATH}/requirements.txt", sudo=True)
    # 安装 Gunicorn
    run_command(client, "python3 -m pip install gunicorn", sudo=True)
    
    # 4. 配置 Systemd 服务 (Gunicorn)
    print("\n--- 4. 配置 Systemd 服务 (Gunicorn) ---")
    service_content = f"""[Unit]
Description=Huo Zhe Ma Web App
After=network.target

[Service]
User=root
WorkingDirectory={REMOTE_PATH}
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 webapp:app
Restart=always

[Install]
WantedBy=multi-user.target
"""
    with open('huozhema.service', 'w', encoding='utf-8') as f:
        f.write(service_content)
    
    sftp = client.open_sftp()
    sftp.put('huozhema.service', f'{REMOTE_PATH}/huozhema.service')
    
    # 5. 配置 Nginx 反向代理
    print("\n--- 5. 配置 Nginx 反向代理 ---")
    nginx_config = """server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
"""
    with open('huozhema_nginx', 'w', encoding='utf-8') as f:
        f.write(nginx_config)
    
    sftp.put('huozhema_nginx', f'{REMOTE_PATH}/huozhema_nginx')
    sftp.close()
    
    os.remove('huozhema.service')
    os.remove('huozhema_nginx')
    
    # 移动并启用服务
    run_command(client, f"mv {REMOTE_PATH}/huozhema.service /etc/systemd/system/huozhema.service", sudo=True)
    run_command(client, "systemctl daemon-reload", sudo=True)
    run_command(client, "systemctl enable huozhema", sudo=True)
    run_command(client, "systemctl restart huozhema", sudo=True)
    
    # 配置 Nginx
    run_command(client, f"mv {REMOTE_PATH}/huozhema_nginx /etc/nginx/sites-available/huozhema", sudo=True)
    run_command(client, "ln -sf /etc/nginx/sites-available/huozhema /etc/nginx/sites-enabled/", sudo=True)
    run_command(client, "rm -f /etc/nginx/sites-enabled/default", sudo=True)
    
    run_command(client, "nginx -t", sudo=True)
    run_command(client, "systemctl restart nginx", sudo=True)
    
    # 6. 配置防火墙
    print("\n--- 6. 配置防火墙 ---")
    if 'centos' in os_info:
        run_command(client, "firewall-cmd --zone=public --add-port=80/tcp --permanent", sudo=True)
        run_command(client, "firewall-cmd --reload", sudo=True)
    else:
        run_command(client, "ufw allow 80/tcp", sudo=True)
        
    print("\n===========================================")
    print(f"部署完成！")
    print(f"请访问: http://{HOST}")
    print("===========================================")
    
    client.close()

if __name__ == '__main__':
    deploy()
