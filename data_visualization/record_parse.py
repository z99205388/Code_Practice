"""
Apollo Record 文件解析器

用于解析Apollo自动驾驶平台的record文件格式。
支持解析多种传感器数据和定位信息。

使用方法:
    python record_parse.py [record_file_path] [--channel CHANNEL_NAME]

示例:
    # 解析整个文件
    python record_parse.py

    # 解析特定通道
    python record_parse.py --channel /apollo/localization/pose

    # 导出到JSON
    python record_parse.py --export localization_data.json
"""

import struct
import os
import sys
import re
import json
import argparse
from collections import defaultdict
from datetime import datetime


class ApolloRecordParser:
    """Apollo Record 文件解析器（不依赖完整Apollo环境）"""

    # 通道类型映射
    CHANNEL_TYPES = {
        '/apollo/localization/pose': 'LocalizationEstimate',
        '/apollo/sensor/gnss/best_pose': 'GnssBestPose',
        '/apollo/sensor/gnss/imu': 'CorrectedImu',
        '/apollo/canbus/chassis': 'Chassis',
        '/apollo/perception/obstacles': 'PerceptionObstacles',
        '/apollo/planning': 'ADCTrajectory',
        '/apollo/prediction': 'PredictionObstacles',
        '/apollo/sensor/conti_radar': 'RadarObstacles',
    }

    def __init__(self, file_path):
        """初始化解析器

        Args:
            file_path: record文件路径
        """
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.channels = {}
        self.channel_data = defaultdict(list)
        self.proto_types = set()

    def parse(self, verbose=True):
        """解析record文件

        Args:
            verbose: 是否输出详细信息

        Returns:
            dict: 解析结果
        """
        if verbose:
            print(f"\n{'='*60}")
            print("Apollo Record 文件解析")
            print(f"{'='*60}")
            print(f"文件路径: {self.file_path}")
            print(f"文件大小: {self.file_size:,} 字节 ({self.file_size/(1024*1024):.2f} MB)")

        with open(self.file_path, 'rb') as f:
            self.content = f.read()

        # 提取通道信息
        self._extract_channels()

        # 提取Proto类型
        self._extract_proto_types()

        # 尝试解析消息数据
        self._parse_messages(verbose)

        if verbose:
            self._print_summary()

        return {
            'channels': list(self.channels),
            'proto_types': list(self.proto_types),
            'message_count': {k: len(v) for k, v in self.channel_data.items()},
        }

    def _extract_channels(self):
        """提取通道名称"""
        # 通道名模式: /apollo/xxx/yyy
        patterns = [
            rb'/apollo/[a-zA-Z0-9_/]+',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, self.content)
            for match in matches:
                try:
                    channel = match.decode('utf-8')
                    # 清理
                    channel = re.split(r'[\x00-\x1f]', channel)[0]
                    if 5 < len(channel) < 80 and channel not in self.channels:
                        # 过滤掉dag文件路径
                        if '.dag' not in channel:
                            self.channels[channel] = {
                                'type': self.CHANNEL_TYPES.get(channel, 'Unknown'),
                                'count': 0
                            }
                except:
                    pass

    def _extract_proto_types(self):
        """提取Proto类型名"""
        # CamelCase类型名模式
        pattern = rb'[A-Z][a-z]+[A-Z][a-zA-Z]+'
        matches = re.findall(pattern, self.content)

        for match in matches:
            try:
                ptype = match.decode('utf-8')
                if 5 < len(ptype) < 50:
                    self.proto_types.add(ptype)
            except:
                pass

    def _parse_messages(self, verbose=True):
        """尝试解析消息数据"""
        # Protobuf消息特征检测
        # 定位消息通常包含时间戳和位置数据

        if verbose:
            print(f"\n正在扫描消息数据...")

        # 查找时间戳特征（纳秒时间戳范围）
        # Apollo时间戳: 纳秒级，通常在 1.5e18 到 1.7e18

        for channel in self.channels:
            # 统计每个通道出现的次数
            channel_bytes = channel.encode('utf-8')
            count = self.content.count(channel_bytes)
            self.channels[channel]['count'] = count

    def _print_summary(self):
        """打印解析摘要"""
        print(f"\n{'-'*60}")
        print("解析结果摘要")
        print(f"{'-'*60}")

        print(f"\n发现通道: {len(self.channels)} 个")
        print("\n主要数据通道:")
        data_channels = [ch for ch in self.channels.keys()
                        if not ch.startswith('/apollo/modules')]

        for ch in sorted(data_channels):
            info = self.channels[ch]
            print(f"  {ch}")
            print(f"    类型: {info['type']}")
            print(f"    引用: {info['count']}")

        print(f"\nProto类型: {len(self.proto_types)} 个")

    def get_channel_data(self, channel_name, max_messages=100):
        """获取特定通道的数据（简化版本，需要完整Apollo环境才能解析完整数据）

        Args:
            channel_name: 通道名称
            max_messages: 最大消息数

        Returns:
            list: 消息列表
        """
        if channel_name not in self.channels:
            print(f"错误: 通道 '{channel_name}' 不存在")
            return []

        print(f"\n提取通道 '{channel_name}' 的数据...")
        print(f"提示: 完整数据解析需要Apollo环境，这里提供数据位置信息")

        # 查找通道在文件中的位置
        channel_bytes = channel_name.encode('utf-8')
        positions = []
        start = 0

        while len(positions) < max_messages:
            pos = self.content.find(channel_bytes, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        return [{
            'position': pos,
            'offset': hex(pos)
        } for pos in positions]

    def export_summary(self, output_file):
        """导出解析摘要到JSON文件

        Args:
            output_file: 输出文件路径
        """
        summary = {
            'file_path': self.file_path,
            'file_size': self.file_size,
            'parse_time': datetime.now().isoformat(),
            'channels': {k: v for k, v in self.channels.items()
                        if not k.startswith('/apollo/modules')},
            'proto_types': sorted(list(self.proto_types)),
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n已导出解析摘要到: {output_file}")


def try_apollo_native_parse(file_path, channel=None):
    """尝试使用Apollo原生库解析

    Args:
        file_path: record文件路径
        channel: 可选，指定解析的通道

    Returns:
        bool: 是否成功解析
    """
    try:
        from cyber_py import cyber
        from cyber.tools.record.record_reader import RecordReader

        print("\n检测到Apollo环境，使用原生解析器...")
        print(f"{'='*60}")

        cyber.init()
        reader = RecordReader(file_path)

        # 获取通道列表
        channels = reader.get_channellist()
        print(f"\n通道列表 ({len(channels)} 个):")

        # 按类别分组显示
        channel_groups = {
            '定位': [],
            '传感器': [],
            '感知': [],
            '规划': [],
            '控制': [],
            '其他': []
        }

        for ch in channels:
            if 'localization' in ch or 'pose' in ch:
                channel_groups['定位'].append(ch)
            elif 'sensor' in ch or 'gnss' in ch.lower():
                channel_groups['传感器'].append(ch)
            elif 'perception' in ch:
                channel_groups['感知'].append(ch)
            elif 'planning' in ch:
                channel_groups['规划'].append(ch)
            elif 'control' in ch:
                channel_groups['控制'].append(ch)
            else:
                channel_groups['其他'].append(ch)

        for group, chs in channel_groups.items():
            if chs:
                print(f"\n  [{group}]")
                for ch in sorted(chs):
                    print(f"    - {ch}")

        # 统计消息数量
        print(f"\n{'-'*60}")
        print("消息统计:")
        channel_counts = defaultdict(int)
        channel_types = {}

        for msg in reader.read_messages():
            channel_counts[msg.channel_name] += 1
            if msg.channel_name not in channel_types:
                channel_types[msg.channel_name] = msg.data_type

        for ch in sorted(channel_counts.keys()):
            count = channel_counts[ch]
            dtype = channel_types.get(ch, 'Unknown')
            print(f"  {ch}: {count:,} 条 ({dtype})")

        # 解析特定通道的数据
        target_channel = channel or '/apollo/localization/pose'

        if target_channel in channels:
            print(f"\n{'-'*60}")
            print(f"解析通道: {target_channel}")
            print(f"{'-'*60}")

            # 尝试导入对应的proto
            if 'localization' in target_channel:
                try:
                    from apollo.localization.proto import localization_pb2

                    print("\n定位数据 (前5条):")
                    count = 0
                    for msg in reader.read_messages(target_channel):
                        if count >= 5:
                            break
                        pose = localization_pb2.LocalizationEstimate()
                        pose.ParseFromString(msg.message)

                        timestamp_ns = msg.timestamp
                        timestamp_s = timestamp_ns / 1e9

                        print(f"\n  消息 #{count+1}")
                        print(f"    时间戳: {timestamp_ns} ({timestamp_s:.3f}s)")
                        print(f"    位置: x={pose.pose.position.x:.4f}, "
                              f"y={pose.pose.position.y:.4f}, "
                              f"z={pose.pose.position.z:.4f}")
                        print(f"    速度: x={pose.pose.linear_velocity.x:.4f}, "
                              f"y={pose.pose.linear_velocity.y:.4f}")
                        print(f"    姿态四元数: w={pose.pose.orientation.qw:.4f}, "
                              f"x={pose.pose.orientation.qx:.4f}, "
                              f"y={pose.pose.orientation.qy:.4f}, "
                              f"z={pose.pose.orientation.qz:.4f}")
                        count += 1

                except ImportError as e:
                    print(f"无法导入定位proto: {e}")

            elif 'gnss' in target_channel.lower():
                try:
                    from apollo.localization.proto import localization_pb2

                    print("\nGNSS数据 (前5条):")
                    count = 0
                    for msg in reader.read_messages(target_channel):
                        if count >= 5:
                            break
                        print(f"\n  消息 #{count+1}")
                        print(f"    时间戳: {msg.timestamp}")
                        print(f"    消息大小: {len(msg.message)} 字节")
                        count += 1

                except ImportError as e:
                    print(f"无法导入GNSS proto: {e}")

        cyber.shutdown()
        return True

    except ImportError as e:
        print(f"\n未检测到完整Apollo环境 (ImportError: {e})")
        return False
    except Exception as e:
        print(f"\nApollo原生解析失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Apollo Record 文件解析器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            示例:
            # 解析整个文件
            python %(prog)s

            # 解析特定通道
            python %(prog)s --channel /apollo/localization/pose

            # 导出摘要到JSON
            python %(prog)s --export summary.json

            # 指定文件路径
            python %(prog)s /path/to/record.file
        """
    )

    parser.add_argument('file', nargs='?',
                       default='/home/ubuntu/apollo/resources/records/demo_3.5.record',
                       help='Record文件路径 (默认: demo_3.5.record)')
    parser.add_argument('--channel', '-c',
                       help='指定要解析的通道')
    parser.add_argument('--export', '-e',
                       help='导出解析摘要到JSON文件')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细信息')

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.file):
        print(f"错误: 文件不存在 - {args.file}")
        sys.exit(1)

    print(f"\n{'#'*60}")
    print(f"# Apollo Record 文件解析器")
    print(f"# 文件: {args.file}")
    print(f"{'#'*60}")

    # 尝试使用Apollo原生解析
    if not try_apollo_native_parse(args.file, args.channel):
        # 使用通用解析器
        print("\n使用通用二进制解析器...")
        record_parser = ApolloRecordParser(args.file)
        result = record_parser.parse(verbose=True)

        # 如果指定了通道，获取该通道数据
        if args.channel:
            channel_data = record_parser.get_channel_data(args.channel)
            if channel_data:
                print(f"\n通道 '{args.channel}' 数据位置:")
                for i, data in enumerate(channel_data[:10]):
                    print(f"  消息 {i+1}: 偏移 {data['offset']}")

        # 导出摘要
        if args.export:
            record_parser.export_summary(args.export)

    print(f"\n{'='*60}")
    print("解析完成!")
    print(f"{'='*60}\n")

def parse(file_path, verbose=False):
      """
      解析 Apollo record 文件
      
      Args:
          file_path: record 文件路径
          verbose: 是否输出详细信息
          
      Returns:
          dict: ApolloRecordParser.parse() 的原始结果
      """
      parser = ApolloRecordParser(file_path)
      return parser.parse(verbose=verbose)

if __name__ == "__main__":
    main()
