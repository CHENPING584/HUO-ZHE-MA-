import tkinter as tk
from gui import SignInApp
from scheduler import SignInScheduler
import traceback
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 获取邮箱配置
sender_email = config.get('Email', 'sender_email', fallback='')
sender_password = config.get('Email', 'sender_password', fallback='')
smtp_server = config.get('Email', 'smtp_server', fallback='')
smtp_port = config.get('Email', 'smtp_port', fallback='')

# 完整版主应用，运行GUI和定时任务
if __name__ == "__main__":
    try:
        print("启动每日签到提醒系统...")
        
        # 初始化并启动定时任务调度器
        scheduler = SignInScheduler(sender_email, sender_password, smtp_server, smtp_port)
        scheduler.start_scheduler()
        print(f"定时任务已启动，邮件发送器状态: {'已初始化' if scheduler.email_sender else '未初始化'}")
        
        # 启动GUI
        root = tk.Tk()
        app = SignInApp(root)
        root.mainloop()
        
        # 停止定时任务
        scheduler.stop_scheduler()
    except Exception as e:
        print(f"应用启动失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        input("按回车键退出...")