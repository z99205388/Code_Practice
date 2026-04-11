"""
Record 2D 可视化播放器视图

提供 record 文件上传、解析、帧渲染和播放器页面
"""

import os
import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from .record_visualization import RecordPlayer


# 全局播放器缓存（避免重复解析）
_player_cache = {}


def _get_player(file_path: str) -> RecordPlayer:
    """获取或创建播放器（带缓存）"""
    if file_path not in _player_cache:
        player = RecordPlayer(file_path)
        result = player.parse_all_messages()
        if not result['success']:
            raise ValueError(f"Failed to parse record file: {result.get('error', 'Unknown error')}")
        _player_cache[file_path] = player
    return _player_cache[file_path]


@login_required
def record_player_index(request: HttpRequest) -> HttpResponse:
    """Record 播放器首页 - 上传/选择 record 文件"""
    context = {
        'title': 'Apollo Record 2D 可视化播放器',
    }
    return render(request, 'data_visualization/record_player/index.html', context)


@login_required
@require_http_methods(["POST"])
def upload_record_file(request: HttpRequest) -> HttpResponse:
    """上传 record 文件"""
    record_file = request.FILES.get('record_file')
    
    if not record_file:
        messages.error(request, '请选择一个 record 文件上传')
        return redirect('data_visualization:record_player_index')
    
    # 检查文件扩展名
    if not record_file.name.endswith('.record'):
        messages.error(request, '请上传 .record 格式的文件')
        return redirect('data_visualization:record_player_index')
    
    # 保存文件
    uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    file_path = os.path.join(uploads_dir, record_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in record_file.chunks():
            destination.write(chunk)
    
    # 跳转到播放器页面
    return redirect('data_visualization:record_player', file_name=record_file.name)


@login_required
def record_player(request: HttpRequest, file_name: str) -> HttpResponse:
    """Record 播放器页面"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)
    
    if not os.path.exists(file_path):
        messages.error(request, f'Record 文件不存在: {file_name}')
        return redirect('data_visualization:record_player_index')
    
    try:
        player = _get_player(file_path)
        
        # 获取播放器信息
        frame_count = player.get_total_frames()
        timestamps = player.get_frame_timestamps()
        
        context = {
            'file_name': file_name,
            'file_path': file_path,
            'frame_count': frame_count,
            'timestamps': json.dumps(timestamps),
            'channels': json.dumps(player.channels),
            'stats': json.dumps(player.stats),
        }
        
        return render(request, 'data_visualization/record_player/player.html', context)
        
    except Exception as e:
        messages.error(request, f'解析 record 文件失败: {str(e)}')
        return redirect('data_visualization:record_player_index')


@login_required
def render_frame_image(request: HttpRequest, file_name: str, frame_index: int) -> HttpResponse:
    """渲染指定帧的图片"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)
    
    if not os.path.exists(file_path):
        return JsonResponse({'error': 'File not found'}, status=404)
    
    try:
        player = _get_player(file_path)
        
        # 获取帧数据
        frame_data = player.get_frame_at_time(frame_index=frame_index)
        
        if not frame_data.get('success'):
            return JsonResponse({'error': frame_data.get('error', 'Failed to get frame')}, status=400)
        
        # 生成图片
        charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        image_filename = f'record_frame_{file_name}_{frame_index}.png'
        image_path = os.path.join(charts_dir, image_filename)
        
        player.render_frame(frame_data, image_path)
        
        # 返回图片 URL
        image_url = f'/media/charts/{image_filename}'
        
        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'frame_index': frame_index,
            'timestamp': frame_data['data'].get('timestamp', 0),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_frame_data_json(request: HttpRequest, file_name: str, frame_index: int) -> HttpResponse:
    """获取指定帧的 JSON 数据（供前端直接渲染）"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)
    
    if not os.path.exists(file_path):
        return JsonResponse({'error': 'File not found'}, status=404)
    
    try:
        player = _get_player(file_path)
        
        # 获取帧数据
        frame_data = player.get_frame_at_time(frame_index=frame_index)
        
        if not frame_data.get('success'):
            return JsonResponse({'error': frame_data.get('error', 'Failed to get frame')}, status=400)
        
        return JsonResponse({
            'success': True,
            'data': frame_data['data'],
            'frame_index': frame_index,
            'total_frames': player.get_total_frames(),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def demo_record_player(request: HttpRequest) -> HttpResponse:
    """演示用 record 播放器（使用默认 demo 文件）"""
    demo_file = 'demo_3.5.record'
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', demo_file)
    
    if not os.path.exists(file_path):
        messages.error(request, f'Demo record 文件不存在: {file_path}')
        return redirect('data_visualization:record_player_index')
    
    return redirect('data_visualization:record_player', file_name=demo_file)
