#!/bin/bash

# Django Learning Log - 快速启动脚本 (使用 uv)

echo "================================================"
echo "   Learning Log - 快速启动脚本"
echo "================================================"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 检查必要的目录
if [ ! -d "media/uploads" ]; then
    echo "⚠️  创建 uploads 目录..."
    mkdir -p media/uploads
fi

if [ ! -d "media/charts" ]; then
    echo "⚠️  创建 charts 目录..."
    mkdir -p media/charts
fi

echo "✅ 目录检查完成"
echo ""

# 使用 uv 运行 Django 检查
echo "🔍 检查数据库..."
uv run --python 3.11 python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ 数据库检查失败！"
    exit 1
fi

echo "✅ 数据库检查通过"
echo ""

# 显示访问信息
echo "================================================"
echo "   启动开发服务器"
echo "================================================"
echo ""
echo "服务器将在以下地址启动："
echo "  - http://localhost:8000"
echo "  - http://127.0.0.1:8000"
echo "  - http://0.0.0.0:8000"
echo ""
echo "重要页面："
echo "  - 首页：http://localhost:8000/"
echo "  - 学习日志：http://localhost:8000/learning_logs/"
echo "  - 数据可视化：http://localhost:8000/data_visualization/"
echo "  - 管理后台：http://localhost:8000/admin/"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================================"
echo ""

# 启动开发服务器 (使用 uv run)
uv run --python 3.11 python manage.py runserver 0.0.0.0:8000
