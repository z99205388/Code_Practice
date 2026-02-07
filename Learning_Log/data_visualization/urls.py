"""定义data_visualization的URL模式"""

from django.urls import path
from . import views

app_name = 'data_visualization'

urlpatterns = [
    # 数据可视化主页
    path('', views.index, name='index'),

    # 显示所有的图表
    path('charts/', views.charts, name='charts'),

    # 特定图表的详细页面
    path('charts/<int:chart_id>/', views.chart_detail, name='chart_detail'),

    # 处理数据
    path('process/', views.process_data, name='process_data'),

]
