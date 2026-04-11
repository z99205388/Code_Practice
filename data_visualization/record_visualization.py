"""
Apollo Record 2D 可视化播放器

仿 nuplan 风格的 2D 自动驾驶场景可视化：
- 自车（Ego Vehicle）：矩形框 + 轨迹线
- 他车（Other Vehicles）：矩形框
- 车道线（Lanes）：多段线
- 时间轴播放控制

使用方式:
    from data_visualization.record_visualization import RecordPlayer
    
    player = RecordPlayer('demo.record')
    player.parse_all_messages()  # 解析所有消息
    
    # 获取某一帧的可视化
    frame_data = player.get_frame_at_time(timestamp=10.5)
    image_path = player.render_frame(frame_data, output_path='frame.png')
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrow, Rectangle, Polygon
import numpy as np

# 复用 record_parse.py 的解析逻辑
# 支持独立运行（非 Django 模块导入）
try:
    from .record_parse import parse_record
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from record_parse import parse_record


class RecordPlayer:
    """Apollo Record 文件 2D 可视化播放器"""
    
    # nuplan 风格颜色方案
    COLORS = {
        'ego_vehicle': '#FF6B35',        # 橙色 - 自车
        'other_vehicle': '#4ECDC4',      # 青色 - 他车
        'lane_line': '#87CEEB',          # 天蓝 - 车道线
        'lane_boundary': '#FFD93D',      # 黄色 - 道路边界
        'trajectory': '#FF3E3E',         # 红色 - 轨迹线
        'trajectory_past': '#FF8888',    # 浅红 - 已过轨迹
        'trajectory_future': '#FF3E3E',  # 鲜红 - 未来轨迹
        'background': '#1a1a2e',         # 深蓝背景
        'grid': '#2a2a3e',               # 网格线
        'text': '#FFFFFF',               # 白色文字
    }
    
    # 车辆尺寸（米）
    EGO_VEHICLE_SIZE = (4.5, 2.0)  # 长 x 宽
    OTHER_VEHICLE_SIZE = (4.0, 1.8)
    
    def __init__(self, file_path: str, max_messages: int = None):
        self.file_path = file_path
        self.max_messages = max_messages
        self.file_size = 0
        self.channels = {}
        self.messages = []  # 所有解析的消息列表
        self.time_series = {}  # 按时间索引的数据
        
        # 统计数据
        self.stats = {
            'ego_poses': 0,
            'vehicles': 0,
            'lanes': 0,
            'total_messages': 0,
        }
        
    def parse_all_messages(self) -> Dict:
        """解析 record 文件中的所有消息（复用 record_parse.parse_record）"""
        try:
            if not os.path.exists(self.file_path):
                return {'success': False, 'error': f'File not found: {self.file_path}'}
            
            self.file_size = os.path.getsize(self.file_path)
            
            # 复用 record_parse.py 的解析逻辑
            # 如果不指定 max_messages，解析所有消息（设置一个很大的值）
            max_msgs = self.max_messages if self.max_messages else 1000000
            
            parse_result = parse_record(
                file_path=self.file_path,
                channel=None,
                max_messages=max_msgs,
                export=None,
                verbose=False,  # 静默模式
            )
            
            # 收集通道信息
            self.channels = parse_result.get('channels', {})
            
            # 转换消息格式
            for msg in parse_result.get('messages', []):
                msg_dict = {
                    'channel': msg.get('channel', ''),
                    'timestamp': msg.get('timestamp', 0),
                    'type': 'unknown',
                }
                
                # 提取位置、速度等数据
                if 'position' in msg:
                    msg_dict['type'] = 'localization'
                    msg_dict['position'] = msg['position']
                    msg_dict['velocity'] = msg.get('velocity', {})
                    msg_dict['heading'] = msg.get('heading', 0)
                    self.stats['ego_poses'] += 1
                
                if 'obstacles' in msg:
                    msg_dict['type'] = 'perception'
                    msg_dict['obstacles'] = msg['obstacles']
                    self.stats['vehicles'] += len(msg['obstacles'])
                
                if 'lanes' in msg:
                    msg_dict['type'] = 'lane'
                    msg_dict['lanes'] = msg['lanes']
                    self.stats['lanes'] += len(msg['lanes'])
                
                if 'trajectory' in msg:
                    msg_dict['type'] = 'trajectory'
                    msg_dict['trajectory'] = msg['trajectory']
                
                self.messages.append(msg_dict)
                self.stats['total_messages'] += 1
            
            # 按时间排序
            self.messages.sort(key=lambda m: m['timestamp'])
            
            # 构建时间序列索引
            self._build_time_series()
            
            return {
                'success': True,
                'total_messages': len(self.messages),
                'channels': len(self.channels),
                'stats': self.stats,
            }
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            return {'success': False, 'error': error_msg}
    
    def _extract_message_data(self, message, msg_data: Dict):
        """提取消息数据并分类"""
        # 1. 定位数据（Ego Vehicle Pose）
        if hasattr(message, 'pose'):
            try:
                msg_data['type'] = 'localization'
                msg_data['position'] = {
                    'x': message.pose.position.x,
                    'y': message.pose.position.y,
                    'z': message.pose.position.z,
                }
                msg_data['velocity'] = {
                    'x': message.pose.linear_velocity.x,
                    'y': message.pose.linear_velocity.y,
                }
                if hasattr(message.pose, 'heading'):
                    msg_data['heading'] = message.pose.heading
                self.stats['ego_poses'] += 1
            except AttributeError:
                pass
        
        # 2. 感知目标（其他车辆）
        elif hasattr(message, 'perception_obstacle'):
            try:
                msg_data['type'] = 'perception'
                msg_data['obstacles'] = []
                for obstacle in message.perception_obstacle:
                    obj_data = {
                        'id': obstacle.id,
                        'position': {
                            'x': obstacle.position.x,
                            'y': obstacle.position.y,
                        },
                        'velocity': {
                            'x': obstacle.velocity.x,
                            'y': obstacle.velocity.y,
                        },
                        'length': obstacle.length,
                        'width': obstacle.width,
                        'height': obstacle.height,
                        'type': obstacle.type,  # VEHICLE, PEDESTRIAN, etc.
                        'heading': obstacle.heading,
                    }
                    msg_data['obstacles'].append(obj_data)
                self.stats['vehicles'] += len(msg_data['obstacles'])
            except AttributeError:
                pass
        
        # 3. 车道线/地图数据
        elif hasattr(message, 'lane'):
            try:
                msg_data['type'] = 'lane'
                msg_data['lanes'] = []
                for lane in message.lane:
                    lane_data = {
                        'id': lane.id,
                        'center_line': [],
                        'left_boundary': [],
                        'right_boundary': [],
                    }
                    # 提取中心线
                    if hasattr(lane, 'central_curve'):
                        for point in lane.central_curve.segment:
                            for line_point in point.line_segment.point:
                                lane_data['center_line'].append({
                                    'x': line_point.x,
                                    'y': line_point.y,
                                })
                    
                    # 提取边界
                    if hasattr(lane, 'left_boundary'):
                        for point in lane.left_boundary.curve.segment:
                            for line_point in point.line_segment.point:
                                lane_data['left_boundary'].append({
                                    'x': line_point.x,
                                    'y': line_point.y,
                                })
                    
                    if hasattr(lane, 'right_boundary'):
                        for point in lane.right_boundary.curve.segment:
                            for line_point in point.line_segment.point:
                                lane_data['right_boundary'].append({
                                    'x': line_point.x,
                                    'y': line_point.y,
                                })
                    
                    msg_data['lanes'].append(lane_data)
                self.stats['lanes'] += len(msg_data['lanes'])
            except AttributeError:
                pass
        
        # 4. 规划轨迹
        elif hasattr(message, 'trajectory_point'):
            try:
                msg_data['type'] = 'trajectory'
                msg_data['trajectory'] = []
                for point in message.trajectory_point:
                    msg_data['trajectory'].append({
                        'x': point.path_point.x,
                        'y': point.path_point.y,
                        'v': point.v,
                        'time': point.relative_time,
                    })
            except AttributeError:
                pass
    
    def _build_time_series(self):
        """构建时间序列索引，便于快速定位"""
        if not self.messages:
            return
        
        # 按类型分组
        self.time_series = {
            'localization': [],
            'perception': [],
            'lane': [],
            'trajectory': [],
        }
        
        for msg in self.messages:
            msg_type = msg.get('type', 'unknown')
            if msg_type in self.time_series:
                self.time_series[msg_type].append(msg)
    
    def get_frame_at_time(self, timestamp: float = None, frame_index: int = None) -> Dict:
        """获取指定时间点的帧数据"""
        if not self.messages:
            return {'success': False, 'error': 'No messages parsed'}
        
        # 确定时间点
        if timestamp is None and frame_index is not None:
            # 根据索引获取时间
            localization_msgs = self.time_series.get('localization', [])
            if frame_index < len(localization_msgs):
                timestamp = localization_msgs[frame_index]['timestamp']
            else:
                return {'success': False, 'error': 'Frame index out of range'}
        
        if timestamp is None:
            timestamp = self.messages[0]['timestamp']
        
        # Apollo 时间戳是纳秒级别
        # 1秒 = 1e9 纳秒
        tolerance_ns = 1e9  # 1秒容差
        
        frame_data = {
            'timestamp': timestamp,
            'ego_pose': None,
            'vehicles': [],
            'lanes': [],
            'trajectory': None,  # None 表示未找到，[] 表示找到但为空
        }
        
        # 获取最近的定位数据
        localization_msgs = self.time_series.get('localization', [])
        closest_pose = None
        min_diff = float('inf')
        for msg in localization_msgs:
            diff = abs(msg['timestamp'] - timestamp)
            if diff < min_diff:
                min_diff = diff
                closest_pose = msg
        
        if closest_pose and min_diff < tolerance_ns:
            frame_data['ego_pose'] = closest_pose
        
        # 获取最近的感知数据（车辆）
        perception_msgs = self.time_series.get('perception', [])
        closest_perception = None
        min_perception_diff = float('inf')
        for msg in perception_msgs:
            diff = abs(msg['timestamp'] - timestamp)
            if diff < min_perception_diff:
                min_perception_diff = diff
                closest_perception = msg
        
        # 5秒容差（纳秒）
        if closest_perception and min_perception_diff < 5e9:
            frame_data['vehicles'] = closest_perception.get('obstacles', [])
        
        # 获取轨迹数据
        trajectory_msgs = self.time_series.get('trajectory', [])
        closest_trajectory = None
        min_trajectory_diff = float('inf')
        for msg in trajectory_msgs:
            diff = abs(msg['timestamp'] - timestamp)
            if diff < min_trajectory_diff:
                min_trajectory_diff = diff
                closest_trajectory = msg
        
        if closest_trajectory and min_trajectory_diff < 5e9:
            frame_data['trajectory'] = closest_trajectory.get('trajectory', [])
        
        # 如果没有轨迹（None），用历史定位数据生成
        if frame_data['trajectory'] is None and localization_msgs:
            past_poses = [m for m in localization_msgs if m['timestamp'] <= timestamp]
            future_poses = [m for m in localization_msgs if m['timestamp'] > timestamp]
            
            frame_data['trajectory_past'] = [
                {'x': m['position']['x'], 'y': m['position']['y'], 'timestamp': m['timestamp']}
                for m in past_poses[-50:]  # 最近50个点
            ]
            frame_data['trajectory_future'] = [
                {'x': m['position']['x'], 'y': m['position']['y'], 'timestamp': m['timestamp']}
                for m in future_poses[:50]  # 未来50个点
            ]
        
        # 生成虚拟车道线（基于自车轨迹推断）
        # 注意：record 文件通常不包含 map 数据，这里根据轨迹生成示意车道线
        if closest_pose and 'position' in closest_pose:
            ego_x = closest_pose['position']['x']
            ego_y = closest_pose['position']['y']
            ego_heading = closest_pose.get('heading', 0)
            
            # 使用历史定位数据生成更长的车道线（前后各100个点）
            past_poses = [m for m in localization_msgs if m['timestamp'] <= timestamp]
            future_poses = [m for m in localization_msgs if m['timestamp'] > timestamp]
            
            lane_points = (
                [{'x': m['position']['x'], 'y': m['position']['y'], 
                  'heading': m.get('heading', ego_heading)} 
                 for m in past_poses[-100:]] +
                [{'x': m['position']['x'], 'y': m['position']['y'], 
                  'heading': m.get('heading', ego_heading)} 
                 for m in future_poses[:100]]
            )
            
            if lane_points and len(lane_points) > 1:
                # 根据轨迹点生成左右车道线
                lane_width = 3.5  # 标准车道宽度（米）
                
                center_line = []
                left_boundary = []
                right_boundary = []
                
                for i, point in enumerate(lane_points):
                    px, py = point['x'], point['y']
                    
                    # 使用点自带的航向角（如果有），否则计算方向
                    if 'heading' in point and point['heading'] != 0:
                        direction_x = np.cos(point['heading'])
                        direction_y = np.sin(point['heading'])
                    elif i < len(lane_points) - 1:
                        next_point = lane_points[i + 1]
                        direction_x = next_point['x'] - px
                        direction_y = next_point['y'] - py
                        direction_len = (direction_x**2 + direction_y**2)**0.5
                        if direction_len > 0:
                            direction_x /= direction_len
                            direction_y /= direction_len
                        else:
                            direction_x = np.cos(ego_heading)
                            direction_y = np.sin(ego_heading)
                    else:
                        direction_x = np.cos(ego_heading)
                        direction_y = np.sin(ego_heading)
                    
                    # 垂直方向（用于计算车道边界）
                    perp_x = -direction_y
                    perp_y = direction_x
                    
                    center_line.append({'x': px, 'y': py})
                    left_boundary.append({
                        'x': px + perp_x * lane_width / 2,
                        'y': py + perp_y * lane_width / 2,
                    })
                    right_boundary.append({
                        'x': px - perp_x * lane_width / 2,
                        'y': py - perp_y * lane_width / 2,
                    })
                
                frame_data['lanes'] = [{
                    'id': 'inferred_lane',
                    'center_line': center_line,
                    'left_boundary': left_boundary,
                    'right_boundary': right_boundary,
                }]
        
        return {'success': True, 'data': frame_data}
    
    def get_total_frames(self) -> int:
        """获取总帧数（基于定位消息数量）"""
        return len(self.time_series.get('localization', []))
    
    def render_frame(self, frame_data: Dict, output_path: str, figsize: Tuple[int, int] = (16, 12)) -> str:
        """渲染单帧 2D 可视化（nuplan 风格）"""
        data = frame_data.get('data', {})
        
        # 创建图形
        fig, ax = plt.subplots(figsize=figsize, facecolor=self.COLORS['background'])
        ax.set_facecolor(self.COLORS['background'])
        
        # 设置坐标范围（默认 100m x 100m，以自车为中心）
        view_range = 50  # 米
        ego_x, ego_y = 0, 0
        ego_heading = 0
        
        if data.get('ego_pose'):
            ego_x = data['ego_pose']['position']['x']
            ego_y = data['ego_pose']['position']['y']
            ego_heading = data['ego_pose'].get('heading', 0)
        
        ax.set_xlim(ego_x - view_range, ego_x + view_range)
        ax.set_ylim(ego_y - view_range, ego_y + view_range)
        ax.set_aspect('equal')
        
        # 绘制网格
        ax.grid(True, color=self.COLORS['grid'], linewidth=0.5, alpha=0.3)
        
        # 1. 绘制车道线
        self._draw_lanes(ax, data.get('lanes', []))
        
        # 2. 绘制轨迹线
        self._draw_trajectory(ax, data)
        
        # 3. 绘制其他车辆
        self._draw_vehicles(ax, data.get('vehicles', []))
        
        # 4. 绘制自车
        self._draw_ego_vehicle(ax, ego_x, ego_y, ego_heading)
        
        # 设置标题和标签
        timestamp = data.get('timestamp', 0)
        # 转换时间戳为相对时间（从开始算起）
        timestamps_list = self.get_frame_timestamps()
        if timestamps_list:
            start_time = timestamps_list[0]
            # Apollo 时间戳是纳秒，转换为秒
            relative_time = (timestamp - start_time) / 1e9
        else:
            relative_time = 0
            
        ax.set_title(
            f'Apollo Record 2D Visualization | Time: {relative_time:.2f}s',
            color=self.COLORS['text'],
            fontsize=14,
            fontweight='bold',
            pad=10
        )
        
        ax.set_xlabel('X (m)', color=self.COLORS['text'], fontsize=10)
        ax.set_ylabel('Y (m)', color=self.COLORS['text'], fontsize=10)
        
        # 设置刻度颜色
        ax.tick_params(colors=self.COLORS['text'])
        
        # 添加图例
        legend_elements = [
            patches.Patch(facecolor=self.COLORS['ego_vehicle'], label='Ego Vehicle'),
            patches.Patch(facecolor=self.COLORS['other_vehicle'], label='Other Vehicles'),
            patches.Patch(facecolor=self.COLORS['lane_line'], label='Lane Lines'),
            patches.Patch(facecolor=self.COLORS['trajectory_past'], label='Past Trajectory'),
            patches.Patch(facecolor=self.COLORS['trajectory_future'], label='Future Trajectory'),
        ]
        ax.legend(
            handles=legend_elements,
            loc='upper right',
            facecolor='#2a2a3e',
            edgecolor=self.COLORS['text'],
            labelcolor=self.COLORS['text']
        )
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=100, bbox_inches='tight', facecolor=self.COLORS['background'])
        plt.close()
        
        return output_path
    
    def _draw_ego_vehicle(self, ax, x: float, y: float, heading: float):
        """绘制自车（橙色矩形 + 方向箭头）"""
        length, width = self.EGO_VEHICLE_SIZE
        
        # 计算矩形角点（考虑朝向）
        cos_h = np.cos(heading)
        sin_h = np.sin(heading)
        
        corners = np.array([
            [-length/2, -width/2],
            [length/2, -width/2],
            [length/2, width/2],
            [-length/2, width/2],
        ])
        
        # 旋转矩阵
        rotation = np.array([[cos_h, -sin_h], [sin_h, cos_h]])
        rotated_corners = corners @ rotation.T
        
        # 平移到实际位置
        rotated_corners[:, 0] += x
        rotated_corners[:, 1] += y
        
        # 绘制矩形
        vehicle = Polygon(rotated_corners, 
                         facecolor=self.COLORS['ego_vehicle'], 
                         edgecolor='white',
                         linewidth=2,
                         alpha=0.8)
        ax.add_patch(vehicle)
        
        # 绘制方向箭头
        arrow_length = length * 0.8
        arrow_x = x + cos_h * arrow_length/2
        arrow_y = y + sin_h * arrow_length/2
        ax.arrow(x, y, 
                cos_h * arrow_length/2, sin_h * arrow_length/2,
                head_width=0.3, head_length=0.2, 
                fc='white', ec='white',
                linewidth=2)
        
        # 添加标签
        ax.text(x, y + width, 'Ego', 
               color=self.COLORS['text'],
               fontsize=10,
               fontweight='bold',
               ha='center',
               va='bottom')
    
    def _draw_vehicles(self, ax, vehicles: List[Dict]):
        """绘制其他车辆（青色矩形）"""
        for vehicle in vehicles:
            x = vehicle['position']['x']
            y = vehicle['position']['y']
            heading = vehicle.get('heading', 0)
            length = vehicle.get('length', self.OTHER_VEHICLE_SIZE[0])
            width = vehicle.get('width', self.OTHER_VEHICLE_SIZE[1])
            
            # 计算矩形角点
            cos_h = np.cos(heading)
            sin_h = np.sin(heading)
            
            corners = np.array([
                [-length/2, -width/2],
                [length/2, -width/2],
                [length/2, width/2],
                [-length/2, width/2],
            ])
            
            rotation = np.array([[cos_h, -sin_h], [sin_h, cos_h]])
            rotated_corners = corners @ rotation.T
            
            rotated_corners[:, 0] += x
            rotated_corners[:, 1] += y
            
            # 绘制矩形
            rect = Polygon(rotated_corners,
                          facecolor=self.COLORS['other_vehicle'],
                          edgecolor='white',
                          linewidth=1,
                          alpha=0.6)
            ax.add_patch(rect)
    
    def _draw_lanes(self, ax, lanes: List[Dict]):
        """绘制车道线"""
        for lane in lanes:
            # 中心线（虚线，淡蓝色）
            center_line = lane.get('center_line', [])
            if center_line:
                x_coords = [p['x'] for p in center_line]
                y_coords = [p['y'] for p in center_line]
                ax.plot(x_coords, y_coords, 
                       color=self.COLORS['lane_line'],
                       linewidth=2,
                       linestyle='--',
                       alpha=0.5,
                       dashes=[10, 5])  # 虚线间距
            
            # 左边界（实线，黄色）
            left_boundary = lane.get('left_boundary', [])
            if left_boundary:
                x_coords = [p['x'] for p in left_boundary]
                y_coords = [p['y'] for p in left_boundary]
                ax.plot(x_coords, y_coords,
                       color=self.COLORS['lane_boundary'],
                       linewidth=2.5,
                       linestyle='-',
                       alpha=0.8)
            
            # 右边界（实线，黄色）
            right_boundary = lane.get('right_boundary', [])
            if right_boundary:
                x_coords = [p['x'] for p in right_boundary]
                y_coords = [p['y'] for p in right_boundary]
                ax.plot(x_coords, y_coords,
                       color=self.COLORS['lane_boundary'],
                       linewidth=2.5,
                       linestyle='-',
                       alpha=0.8)
    
    def _draw_trajectory(self, ax, data: Dict):
        """绘制轨迹线"""
        # 历史轨迹
        past_traj = data.get('trajectory_past', [])
        if past_traj:
            x_coords = [p['x'] for p in past_traj]
            y_coords = [p['y'] for p in past_traj]
            ax.plot(x_coords, y_coords,
                   color=self.COLORS['trajectory_past'],
                   linewidth=3,
                   linestyle='-',
                   alpha=0.7,
                   marker='o',
                   markersize=5,
                   markeredgecolor='white',
                   markeredgewidth=0.5)

        # 规划轨迹（来自 planning 通道）
        trajectory = data.get('trajectory', [])
        if trajectory:
            x_coords = [p['x'] for p in trajectory]
            y_coords = [p['y'] for p in trajectory]
            ax.plot(x_coords, y_coords,
                   color=self.COLORS['trajectory_future'],
                   linewidth=3,
                   linestyle='-',
                   alpha=0.9,
                   marker='o',
                   markersize=5,
                   markeredgecolor='white',
                   markeredgewidth=0.5)
        else:
            # 如果没有规划轨迹，用未来定位数据生成
            future_traj = data.get('trajectory_future', [])
            if future_traj:
                x_coords = [p['x'] for p in future_traj]
                y_coords = [p['y'] for p in future_traj]
                ax.plot(x_coords, y_coords,
                       color=self.COLORS['trajectory_future'],
                       linewidth=2,
                       linestyle='--',
                       alpha=0.7,
                       marker='o',
                       markersize=4,
                       markeredgecolor='white',
                       markeredgewidth=0.5)
    
    def get_frame_timestamps(self) -> List[float]:
        """获取所有帧的时间戳列表"""
        localization_msgs = self.time_series.get('localization', [])
        return [m['timestamp'] for m in localization_msgs]
    
    def export_frame_data_to_json(self, frame_index: int, output_path: str) -> str:
        """导出单帧数据为 JSON（供前端使用）"""
        import json
        
        frame_data = self.get_frame_at_time(frame_index=frame_index)
        
        # 转换为 JSON 可序列化格式
        json_data = {
            'frame_index': frame_index,
            'total_frames': self.get_total_frames(),
            'timestamp': frame_data.get('data', {}).get('timestamp', 0),
            'ego_pose': frame_data.get('data', {}).get('ego_pose'),
            'vehicles': frame_data.get('data', {}).get('vehicles', []),
            'lanes': frame_data.get('data', {}).get('lanes', []),
            'trajectory_past': frame_data.get('data', {}).get('trajectory_past', []),
            'trajectory_future': frame_data.get('data', {}).get('trajectory_future', []),
        }
        
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return output_path


def create_record_player(file_path: str, max_messages: int = None) -> RecordPlayer:
    """创建 RecordPlayer 实例的便捷函数"""
    return RecordPlayer(file_path, max_messages)


def main():
    """独立运行入口 - 直接运行此脚本"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='Apollo Record 2D 可视化播放器（独立运行）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 解析并渲染所有帧（默认）
    python record_visualization.py demo.record
    
    # 只渲染指定帧
    python record_visualization.py demo.record --frames 0 10 50 100
    
    # 渲染所有帧到指定目录
    python record_visualization.py demo.record --output ./frames/
    
    # 限制解析消息数（快速测试）
    python record_visualization.py demo.record --max-messages 1000
        """
    )
    
    parser.add_argument('file', 
                       default='/home/ubuntu/Code_Practice/media/uploads/demo_3.5.record',
                       nargs='?',
                       help='Record文件路径')
    parser.add_argument('--output', '-o',
                       default='/home/ubuntu/Code_Practice/record_frames/',
                       help='输出目录（默认: /tmp/record_frames/）')
    parser.add_argument('--frames', '-f',
                       nargs='+', type=int,
                       help='指定渲染的帧索引（不指定则渲染所有帧）')
    parser.add_argument('--max-messages', '-m',
                       type=int,
                       help='最大解析消息数（用于快速测试）')
    parser.add_argument('--preview', '-p',
                       action='store_true',
                       help='只渲染首帧和尾帧作为预览')
    
    args = parser.parse_args()
    
    # 检查文件
    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Apollo Record 2D 可视化播放器")
    print(f"{'='*60}")
    print(f"文件: {args.file}")
    print(f"大小: {os.path.getsize(args.file) / 1024 / 1024:.2f} MB")
    
    # 创建播放器
    print(f"\n🔍 解析 record 文件...")
    player = RecordPlayer(args.file, max_messages=args.max_messages)
    result = player.parse_all_messages()
    
    if not result['success']:
        print(f"❌ 解析失败: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    print(f"✅ 解析成功!")
    print(f"   - 总消息数: {result['total_messages']}")
    print(f"   - 总帧数: {player.get_total_frames()}")
    print(f"   - 车辆目标: {player.stats['vehicles']}")
    
    # 确定要渲染的帧
    total_frames = player.get_total_frames()
    
    if args.preview:
        # 预览模式：只渲染首帧和尾帧
        frame_indices = [0, total_frames // 2, total_frames - 1]
    elif args.frames:
        # 指定帧
        frame_indices = args.frames
    else:
        # 所有帧（但最多100帧，避免输出太多）
        if total_frames > 100:
            print(f"\n⚠️  总帧数 {total_frames} 过多，自动采样100帧")
            # 均匀采样
            step = total_frames // 100
            frame_indices = list(range(0, total_frames, step))
            if frame_indices[-1] != total_frames - 1:
                frame_indices.append(total_frames - 1)
        else:
            frame_indices = list(range(total_frames))
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    
    # 渲染帧
    print(f"\n🎨 渲染 {len(frame_indices)} 帧...")
    for i, frame_idx in enumerate(frame_indices):
        if frame_idx >= total_frames:
            print(f"⚠️  跳过超出范围的帧: {frame_idx}")
            continue
        
        try:
            frame_data = player.get_frame_at_time(frame_index=frame_idx)
            output_path = os.path.join(args.output, f'frame_{frame_idx:05d}.png')
            player.render_frame(frame_data, output_path)
            
            # 显示进度
            progress = (i + 1) / len(frame_indices) * 100
            if i % 10 == 0 or i == len(frame_indices) - 1:
                print(f"   [{progress:.1f}%] 帧 {frame_idx}/{total_frames} -> {output_path}")
        except Exception as e:
            print(f"❌ 渲染帧 {frame_idx} 失败: {e}")
    
    print(f"\n{'='*60}")
    print(f"渲染完成!")
    print(f"输出目录: {args.output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
