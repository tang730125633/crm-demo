#!/bin/bash
# CRM Demo 启动脚本

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/output/backend"

echo "CRM Demo 启动中..."

# 安装依赖
echo "安装 Python 依赖..."
pip install -r "$BACKEND_DIR/requirements.txt" -q

# 初始化示例数据（如果数据库不存在）
if [ ! -f "$BACKEND_DIR/crm.db" ]; then
    echo "初始化示例数据..."
    cd "$BACKEND_DIR" && python seed_data.py
fi

# 启动后端
echo "后端启动: http://localhost:8000"
echo "前端地址: 请用浏览器打开 $PROJECT_DIR/output/frontend/index.html"
echo ""
echo "API 文档: http://localhost:8000/docs"
echo ""
cd "$BACKEND_DIR" && uvicorn main:app --reload --host 0.0.0.0 --port 8000
