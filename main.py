"""Railway 部署入口 - 转发到 output/backend/main.py"""
import sys
import os

# 把 output/backend 加入 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "output", "backend"))

from main import app  # noqa: F401 - 让 uvicorn 找到 app
