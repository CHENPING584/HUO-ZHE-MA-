#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Hello, World!")
print("This is a basic Python test script.")

# 测试基本导入
import sys
print(f"Python version: {sys.version}")

# 测试文件操作
try:
    with open("test.txt", "w") as f:
        f.write("test")
    print("File write successful")
    
    with open("test.txt", "r") as f:
        content = f.read()
    print(f"File read successful: {content}")
    
    import os
    os.remove("test.txt")
    print("File delete successful")
except Exception as e:
    print(f"File operation failed: {e}")

print("Test completed!")
