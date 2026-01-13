#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版主程序：用于测试和调试
"""

import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_main.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    主函数
    """
    logger.info("开始运行简化版主程序")
    
    try:
        # 测试数据库模块
        logger.info("测试数据库模块...")
        from database import SignInDatabase
        db = SignInDatabase()
        logger.info("数据库模块测试成功")
        
        # 测试邮件模块
        logger.info("测试邮件模块...")
        from email_reminder import EmailReminder
        logger.info("邮件模块测试成功")
        
        # 测试GUI模块
        logger.info("测试GUI模块...")
        import tkinter as tk
        from gui import SignInApp
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        app = SignInApp(root)
        logger.info("GUI模块测试成功")
        root.destroy()
        
        logger.info("所有模块测试成功！")
        print("\n所有模块测试成功！您可以运行main.py启动完整应用")
        return 0
        
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        print(f"\n程序运行出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
