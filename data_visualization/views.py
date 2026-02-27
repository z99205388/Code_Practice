from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import csv
import json
from datetime import datetime

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
        print("request:",request.POST)
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
    # 确保图表目录存在
    charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
    
    # 生成唯一的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chart_filename = f'chart_{timestamp}.png'
    chart_path = os.path.join(charts_dir, chart_filename)
    
    try:
        parse_file_result = parse_file(file_path)
        generate_chart(parse_file_result, chart_path, chart_type, chart_title)

        # 创建数据库记录
        chart = Chart.objects.create(
            title=chart_title,
            description=description or f'Generated from {source_type} file',
            category='Custom',
            image_path=f'/media/charts/{chart_filename}',
            data_file=file_path,
            script_file=f'data_visualization/views.py (handle_data_processing)'
        )

    except Exception as e:
        # 处理错误
        return render(request, 'data_visualization/process_result.html', {
            'success': False,
            'message': f'Error processing data: {str(e)}',
            'file_path': file_path
        })

    # 重定向到结果页面
    return render(request, 'data_visualization/process_result.html', {
        'chart': chart,
        'success': True,
        'message': f'Chart "{chart_title}" has been successfully generated!'
    })

def parse_file(file_path):
    """文件解析"""
    result = {
        'data': [],
        'header': None,
        'file_type': None,
        'detal_state':True,
        'error_message': ''
    }
    try:
        if file_path.endswith('.json'):
            with open(file_path, 'r')  as f:
                result['data'] = json.load(f)
                result['file_type'] = 'json'
        elif file_path.endswith('.csv'):
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                result['header'] = next(reader)  
                result['data'] = [row for row in reader]
                result['file_type'] = 'csv'
        else:
            ext = os.path.splitext(file_path)[1]
            result['detal_state'] = False
            result['error_message'] = f"暂不支持 {ext} 文件类型解析"
    except Exception as e:
            result['detal_state'] = False
            result['error_message'] = str(e)

    return result

def safe_float_convert(value, default=0):
    """安全地将值转换为浮点数"""
    if value == '' or value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def generate_chart(parse_file_result ,chart_path, chart_type, chart_title):
    """根据解析结果生成图表"""
    data = parse_file_result['data']
    header = parse_file_result['header']

    # 数据验证
    if not data:
        raise ValueError("数据为空")

    # 统一数据格式为字典
    if isinstance(data[0], dict):
        keys = list(data[0].keys())
        data = [[row.get(k, i) for k in keys] for i, row in enumerate(data)]
    
    # 提取数据
    x_values = [row[0] for row in data[:10]]
    y_values = [safe_float_convert(row[1]) for row in data[:50] if len(row) > 1]
    
    # 图表类型的到函数映射
    plotter = {
        'line': lambda: plt.plot(x_values, y_values[:10], marker='o'),
        'bar': lambda: plt.bar(x_values, y_values[:10]),
        'scatter': lambda: plt.scatter([float(row[1]) for row in data[:50]], 
                                    [float(row[2]) for row in data[:50]] if len(data[0]) > 2 else list(range(50))),
        'histogram': lambda: plt.hist(y_values, bins=20),
        'pie': lambda: plt.pie(y_values[:10], labels=x_values, autopct='%1.1f%%')
    }    
    
    # 生成图表
    fig = plt.figure(dpi=128, figsize=(10, 6))
    plotter.get(chart_type, lambda: None)()

    plt.title(chart_title, fontsize=16)
    plt.xlabel(header[0] if len(header) > 0 else 'X')
    if header and len(header) > 1:
        plt.ylabel(header[1])

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
