"""定义data_visualization的URL模式"""

from django.urls import path

from . import views
from . import views_record_player

app_name = "data_visualization"

urlpatterns = [
    # 数据可视化主页
    path("", views.index, name="index"),
    # 显示所有的图表
    path("charts/", views.charts, name="charts"),
    # 特定图表的详细页面
    path("charts/<int:chart_id>/", views.chart_detail, name="chart_detail"),
    # 处理数据
    path("process/", views.process_data, name="process_data"),
    
    # Record 2D 可视化播放器
    path("record-player/", views_record_player.record_player_index, name="record_player_index"),
    path("record-player/upload/", views_record_player.upload_record_file, name="upload_record_file"),
    path("record-player/<str:file_name>/", views_record_player.record_player, name="record_player"),
    path("record-player/<str:file_name>/frame/<int:frame_index>/", 
         views_record_player.render_frame_image, name="render_frame_image"),
    path("record-player/<str:file_name>/frame/<int:frame_index>/json/", 
         views_record_player.get_frame_data_json, name="get_frame_data_json"),
    path("record-player/demo/", views_record_player.demo_record_player, name="demo_record_player"),
]
