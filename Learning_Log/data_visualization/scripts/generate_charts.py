"""
脚本：生成所有数据可视化图表并创建数据库记录

运行此脚本将：
1. 生成所有图表图片
2. 在数据库中创建对应的 Chart 记录
"""

import os
import sys
import django

# 获取 Learning_Log 项目目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_log.settings')
django.setup()

from data_visualization.models import Chart
from data_visualization.scripts.temperature_chart import generate_temperature_chart
from data_visualization.scripts.random_walk_chart import generate_random_walk_chart

def main():
    print("开始生成数据可视化图表...")

    # 清理旧的图表记录（可选）
    print("清理旧的图表记录...")
    Chart.objects.all().delete()

    # 1. 生成温度图表
    print("\n生成温度图表...")
    try:
        temp_chart_info = generate_temperature_chart()
        Chart.objects.create(**temp_chart_info)
        print(f"✓ 温度图表已生成并保存")
    except Exception as e:
        print(f"✗ 温度图表生成失败: {e}")

    # 2. 生成随机漫步图表
    print("\n生成随机漫步图表...")
    try:
        rw_chart_info = generate_random_walk_chart()
        Chart.objects.create(**rw_chart_info)
        print(f"✓ 随机漫步图表已生成并保存")
    except Exception as e:
        print(f"✗ 随机漫步图表生成失败: {e}")

    # 显示所有生成的图表
    print("\n图表生成完成！数据库中的图表：")
    charts = Chart.objects.all()
    for chart in charts:
        print(f"  - {chart.title} ({chart.category})")

    print(f"\n总计：{charts.count()} 个图表")

if __name__ == '__main__':
    main()
