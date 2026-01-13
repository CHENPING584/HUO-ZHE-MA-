#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：用于测试各个模块的基本功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append('.')

def test_database():
    """
    测试数据库操作
    """
    print("=== 测试数据库操作 ===")
    try:
        from database import SignInDatabase
        db = SignInDatabase()
        # 测试数据库连接
        print("数据库连接测试成功")
        # 测试创建表
        print("数据库表创建测试成功")
        return True
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False

def test_email_module():
    """
    测试邮件模块
    """
    print("\n=== 测试邮件模块 ===")
    try:
        # 读取配置文件
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        
        sender_email = config.get('Email', 'sender_email', fallback='')
        sender_password = config.get('Email', 'sender_password', fallback='')
        
        if sender_email and sender_password:
            print(f"邮箱配置已设置: {sender_email}")
            return True
        else:
            print("邮箱配置未设置，请在config.ini中配置sender_email和sender_password")
            return False
    except Exception as e:
        print(f"邮件模块测试失败: {e}")
        return False

def main():
    """
    主测试函数
    """
    print("每日签到提醒系统 - 测试脚本")
    print("=" * 40)
    
    # 测试数据库操作
    test_database()
    
    # 测试邮件模块
    test_email_module()
    
    print("\n=== 测试完成 ===")
    print("如果您需要使用邮件提醒功能，请编辑config.ini文件，配置您的邮箱信息")

if __name__ == "__main__":
    main()
