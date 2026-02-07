"""
Django management command to generate all data visualization charts
"""

import os
import sys
from django.core.management.base import BaseCommand
from data_visualization.models import Chart
from data_visualization.scripts.temperature_chart import generate_temperature_chart
from data_visualization.scripts.random_walk_chart import generate_random_walk_chart

class Command(BaseCommand):
    help = 'Generate all data visualization charts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始生成数据可视化图表...'))

        # 清理旧的图表记录（可选）
        self.stdout.write('清理旧的图表记录...')
        Chart.objects.all().delete()

        # 1. 生成温度图表
        self.stdout.write('\n生成温度图表...')
        try:
            temp_chart_info = generate_temperature_chart()
            Chart.objects.create(**temp_chart_info)
            self.stdout.write(self.style.SUCCESS('✓ 温度图表已生成并保存'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ 温度图表生成失败: {e}'))

        # 2. 生成随机漫步图表
        self.stdout.write('\n生成随机漫步图表...')
        try:
            rw_chart_info = generate_random_walk_chart()
            Chart.objects.create(**rw_chart_info)
            self.stdout.write(self.style.SUCCESS('✓ 随机漫步图表已生成并保存'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ 随机漫步图表生成失败: {e}'))

        # 显示所有生成的图表
        self.stdout.write('\n图表生成完成！数据库中的图表：')
        charts = Chart.objects.all()
        for chart in charts:
            self.stdout.write(f'  - {chart.title} ({chart.category})')

        self.stdout.write(self.style.SUCCESS(f'\n总计：{charts.count()} 个图表'))
