print("Python version:")
import sys
print(sys.version)
print("sys.path:")
print(sys.path)
print("Current directory:")
import os
print(os.getcwd())
print("Testing Tkinter import...")
try:
    import tkinter as tk
    print("Tkinter imported successfully")
    print(f"Tk version: {tk.TkVersion}")
except Exception as e:
    print(f"Tkinter import failed: {e}")
