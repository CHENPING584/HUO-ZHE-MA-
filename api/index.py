import os
import sys

# 获取当前文件的目录 (api/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父目录 (项目根目录)
parent_dir = os.path.dirname(current_dir)

# 将父目录添加到 sys.path 中，以便能导入 webapp.py
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 导入 Flask 应用实例
# 注意：webapp.py 中必须有 app = Flask(__name__)
from webapp import app

# Vercel Serverless Function 需要一个名为 app 的 WSGI 应用对象
# 这里的 app 就是从 webapp 导入的 Flask 实例
