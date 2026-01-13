#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块测试脚本：用于测试各个模块的导入和初始化
"""

import sys
import traceback

print("=== 每日签到提醒系统 - 模块测试 ===")
print(f"Python版本: {sys.version}")
print("=" * 50)

# 测试1：数据库模块
try:
    print("\n1. 测试数据库模块...")
    from database import SignInDatabase
    db = SignInDatabase()
    print("✓ 数据库模块导入和初始化成功")
except Exception as e:
    print(f"✗ 数据库模块测试失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# 测试2：邮件模块
try:
    print("\n2. 测试邮件模块...")
    from email_reminder import EmailReminder
    print("✓ 邮件模块导入成功")
except Exception as e:
    print(f"✗ 邮件模块测试失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# 测试3：定时任务模块
try:
    print("\n3. 测试定时任务模块...")
    from scheduler import SignInScheduler
    scheduler = SignInScheduler()
    print("✓ 定时任务模块导入和初始化成功")
except Exception as e:
    print(f"✗ 定时任务模块测试失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# 测试4：GUI模块导入（不初始化）
try:
    print("\n4. 测试GUI模块导入...")
    import tkinter as tk
    # 只导入模块，不初始化GUI
    from gui import SignInApp
    print("✓ GUI模块导入成功")
except Exception as e:
    print(f"✗ GUI模块测试失败: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("✅ 所有模块测试成功！")
print("程序可以正常启动。")
print("如果GUI界面无法显示，可能是环境配置问题。")
