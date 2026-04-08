#!/bin/bash

# Django Learning Log - 快速启动脚本 (使用 ll_env)

echo "================================================"
echo "   Learning Log - 快速启动脚本"
echo "================================================"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "ll_env" ]; then
    echo "⚠️  未找到 ll_env 虚拟环境，正在创建..."
    uv venv --python 3.11 ll_env
    echo "📦 安装依赖..."
    uv pip install django django-bootstrap3 matplotlib pillow protobuf==3.20.3 python-dotenv asgiref sqlparse python-dateutil packaging certifi cycler fonttools kiwisolver numpy pyparsing --python ll_env/bin/python --index-url https://mirrors.aliyun.com/pypi/simple/
fi

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

# 激活虚拟环境
source ll_env/bin/activate

# 使用 ll_env 运行 Django 检查
echo "🔍 检查项目配置..."
python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ 项目检查失败！"
    exit 1
fi

echo "✅ 项目检查通过"
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
echo "  - http://101.133.145.194:8000 (公网)"
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

# 启动开发服务器
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0,101.133.145.194,172.24.52.84"
python manage.py runserver 0.0.0.0:8000
