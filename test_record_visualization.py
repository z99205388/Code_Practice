"""测试 record 可视化功能"""
import os
import sys

# 设置 Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_log.settings')
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import django
django.setup()

from data_visualization.record_visualization import RecordPlayer

def test_record_visualization():
    """测试 record 可视化的解析和渲染"""
    record_file = '/home/ubuntu/Code_Practice/media/uploads/demo_3.5.record'
    
    if not os.path.exists(record_file):
        print(f"❌ Record 文件不存在: {record_file}")
        return False
    
    print(f"📂 Record 文件: {record_file}")
    print(f"📏 文件大小: {os.path.getsize(record_file) / 1024 / 1024:.2f} MB")
    
    # 创建播放器
    print("\n🔍 开始解析 record 文件...")
    player = RecordPlayer(record_file)
    result = player.parse_all_messages()
    
    if not result['success']:
        print(f"❌ 解析失败: {result.get('error', 'Unknown error')}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"✅ 解析成功!")
    print(f"   - 总消息数: {result['total_messages']}")
    print(f"   - 通道数: {result['channels']}")
    print(f"   - 统计数据: {player.stats}")
    
    # 打印channels 信息
    print(f"   - Channels: {list(player.channels.keys())[:5]}...")
    
    # 获取总帧数
    total_frames = player.get_total_frames()
    print(f"\n🎬 总帧数: {total_frames}")
    
    if total_frames == 0:
        print("⚠️  没有定位数据，无法渲染帧")
        print("   这可能是由于 record 文件中没有 /apollo/localization/pose 通道")
        return False
    
    # 渲染第一帧
    print("\n🎨 渲染第一帧...")
    frame_data = player.get_frame_at_time(frame_index=0)
    
    if not frame_data.get('success'):
        print(f"❌ 获取帧数据失败: {frame_data.get('error', 'Unknown error')}")
        return False
    
    output_path = '/tmp/test_record_frame.png'
    player.render_frame(frame_data, output_path)
    
    if os.path.exists(output_path):
        print(f"✅ 第一帧渲染成功: {output_path}")
        print(f"   - 图片大小: {os.path.getsize(output_path) / 1024:.2f} KB")
    else:
        print("❌ 渲染失败")
        return False
    
    # 渲染中间帧
    if total_frames > 10:
        print(f"\n🎨 渲染第 10 帧...")
        frame_data = player.get_frame_at_time(frame_index=10)
        output_path_10 = '/tmp/test_record_frame_10.png'
        player.render_frame(frame_data, output_path_10)
        
        if os.path.exists(output_path_10):
            print(f"✅ 第 10 帧渲染成功: {output_path_10}")
    
    print("\n✅ 所有测试通过!")
    return True

if __name__ == '__main__':
    success = test_record_visualization()
    sys.exit(0 if success else 1)
