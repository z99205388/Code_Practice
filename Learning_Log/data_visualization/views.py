from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

from .models import Chart

# Create your views here.

def index(request):
    """数据可视化主页"""
    charts = Chart.objects.all().order_by('category', 'date_added')
    categories = set(chart.category for chart in charts)
    context = {'charts': charts, 'categories': categories}
    return render(request, 'data_visualization/index.html', context)

@login_required
def charts(request):
    """显示所有的图表"""
    charts = Chart.objects.all().order_by('category', '-date_added')
    context = {'charts': charts}
    return render(request, 'data_visualization/charts.html', context)

@login_required
def chart_detail(request, chart_id):
    """显示单个图表的详细信息"""
    chart = Chart.objects.get(id=chart_id)
    context = {'chart': chart}
    return render(request, 'data_visualization/chart_detail.html', context)

@login_required
def process_data(request):
    """处理数据选择页面"""
    if request.method == 'POST':
        action = request.POST.get('action')
        chart_title = request.POST.get('chart_title', '')
        description = request.POST.get('description', '')
        chart_type = request.POST.get('chart_type', 'line')

        if action == 'upload':
            # 处理文件上传
            if 'data_file' in request.FILES:
                uploaded_file = request.FILES['data_file']
                # 保存上传的文件
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                file_path = os.path.join(upload_dir, uploaded_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # 处理数据并生成图表
                return handle_data_processing(request, file_path, chart_title, description, chart_type, 'Uploaded')

        elif action == 'process':
            # 处理本地文件路径
            file_path = request.POST.get('file_path', '')
            if file_path and os.path.exists(file_path):
                return handle_data_processing(request, file_path, chart_title, description, chart_type, 'Local')

    # GET 请求 - 显示表单
    return render(request, 'data_visualization/process_data.html')

def handle_data_processing(request, file_path, chart_title, description, chart_type, source_type):
    """处理数据并生成图表"""
    try:
        import csv
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from datetime import datetime

        # 确保图表目录存在
        charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        if not os.path.exists(charts_dir):
            os.makedirs(charts_dir)

        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chart_filename = f'chart_{timestamp}.png'
        chart_path = os.path.join(charts_dir, chart_filename)

        # 读取数据并生成图表
        if file_path.endswith('.csv'):
            generate_chart_from_csv(file_path, chart_path, chart_type, chart_title)
        elif file_path.endswith('.json'):
            generate_chart_from_json(file_path, chart_path, chart_type, chart_title)
        else:
            # 默认为 CSV 处理
            generate_chart_from_csv(file_path, chart_path, chart_type, chart_title)

        # 创建数据库记录
        chart = Chart.objects.create(
            title=chart_title,
            description=description or f'Generated from {source_type} file',
            category='Custom',
            image_path=f'/media/charts/{chart_filename}',
            data_file=file_path,
            script_file=f'data_visualization/views.py (handle_data_processing)'
        )

        # 重定向到结果页面
        return render(request, 'data_visualization/process_result.html', {
            'chart': chart,
            'success': True,
            'message': f'Chart "{chart_title}" has been successfully generated!'
        })

    except Exception as e:
        # 处理错误
        return render(request, 'data_visualization/process_result.html', {
            'success': False,
            'message': f'Error processing data: {str(e)}',
            'file_path': file_path
        })

def generate_chart_from_csv(file_path, chart_path, chart_type, chart_title):
    """从 CSV 文件生成图表"""
    import csv

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # 读取表头

        # 读取数据列
        data = []
        for row in reader:
            data.append(row)

        # 根据图表类型生成不同的图表
        fig = plt.figure(dpi=128, figsize=(10, 6))

        if chart_type == 'line' or chart_type == 'bar':
            # 假设第一列是标签，第二列是数值
            x_labels = [row[0] for row in data[:10]]  # 只显示前10个
            y_values = [float(row[1]) for row in data[:10]] if len(data[0]) > 1 else list(range(len(data[:10])))

            if chart_type == 'line':
                plt.plot(x_labels, y_values, marker='o')
            else:
                plt.bar(x_labels, y_values)

        elif chart_type == 'scatter':
            x_values = [float(row[1]) for row in data[:50]] if len(data[0]) > 1 else list(range(len(data[:50])))
            y_values = [float(row[2]) for row in data[:50]] if len(data[0]) > 2 else list(range(len(data[:50])))
            plt.scatter(x_values, y_values)

        elif chart_type == 'histogram':
            values = [float(row[1]) for row in data if len(row) > 1]
            plt.hist(values, bins=20)

        elif chart_type == 'pie':
            labels = [row[0] for row in data[:10]]
            values = [float(row[1]) for row in data[:10]] if len(data[0]) > 1 else [1] * len(labels)
            plt.pie(values, labels=labels, autopct='%1.1f%%')

        plt.title(chart_title, fontsize=16)
        plt.xlabel(header[0] if len(header) > 0 else 'X')
        if len(header) > 1:
            plt.ylabel(header[1])

        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()

def generate_chart_from_json(file_path, chart_path, chart_type, chart_title):
    """从 JSON 文件生成图表"""
    import json

    with open(file_path, 'r') as f:
        data = json.load(f)

    # 生成图表
    fig = plt.figure(dpi=128, figsize=(10, 6))

    # 简单的 JSON 数据处理
    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], dict):
            keys = list(data[0].keys())
            if len(keys) >= 2:
                x_labels = [item[keys[0]] for item in data[:10]]
                y_values = [item[keys[1]] for item in data[:10]]

                if chart_type == 'line':
                    plt.plot(x_labels, y_values, marker='o')
                elif chart_type == 'bar':
                    plt.bar(x_labels, y_values)
                elif chart_type == 'scatter':
                    x_values = [float(item[keys[1]]) for item in data[:50]]
                    y_values = [float(item[keys[2]]) for item in data[:50]] if len(keys) >= 3 else list(range(len(x_values)))
                    plt.scatter(x_values, y_values)
                elif chart_type == 'histogram':
                    plt.hist(y_values, bins=20)
                elif chart_type == 'pie':
                    plt.pie(y_values, labels=x_labels, autopct='%1.1f%%')
        else:
            plt.plot(data)

    plt.title(chart_title, fontsize=16)
    plt.tight_layout()

    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
