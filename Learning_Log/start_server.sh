#!/bin/bash

# Django Data Visualization - 快速启动脚本

echo "================================================"
echo "   Data Visualization - 快速启动脚本"
echo "================================================"
echo ""

# 进入项目目录
cd /home/ubuntu/Code/Code_Practice/Learning_Log

# 检查虚拟环境
if [ ! -d "ll_env" ]; then
    echo "❌ 错误：虚拟环境 ll_env 不存在！"
    echo "请先创建虚拟环境。"
    exit 1
fi

echo "✅ 虚拟环境检查完成"
echo ""

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
echo "🔄 激活虚拟环境..."
source ll_env/bin/activate

# 运行数据库检查
echo "🔍 检查数据库..."
python manage.py check

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
echo "  - 数据可视化主页：http://localhost:8000/data_visualization/"
echo "  - 数据处理页面：http://localhost:8000/data_visualization/process/"
echo "  - 所有图表：http://localhost:8000/data_visualization/charts/"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================================"
echo ""

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
