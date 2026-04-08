"""
Apollo Record 文件解析器

用于解析Apollo自动驾驶平台的record文件格式。

使用方法:
    python record_parse.py [record_file_path] [options]

示例:
    python record_parse.py
    python record_parse.py --channel /apollo/localization/pose
    python record_parse.py --export summary.json

依赖:
    pip install cyber-record protobuf==3.20.3
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional

# 设置protobuf兼容模式
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'


class ApolloRecordParser:
    """Apollo Record 文件解析器类"""

    def __init__(self, file_path: str, max_messages: int = 10, verbose: bool = False):
        self.file_path = file_path
        self.max_messages = max_messages
        self.verbose = verbose
        self.result = {
            'file_path': file_path,
            'file_size': 0,
            'channels': {},
            'messages': [],
            'message_count': {},
            'detal_state': True,
            'error_message': '',
        }

    def parse(self) -> Dict:
        """解析record文件并返回结果"""
        try:
            if not os.path.exists(self.file_path):
                self.result['detal_state'] = False
                self.result['error_message'] = f"File not found: {self.file_path}"
                return self.result

            self.result['file_size'] = os.path.getsize(self.file_path)

            try:
                from cyber_record.record import Record
                from cyber_record.cyber.proto import record_pb2
                from google.protobuf.internal.decoder import _DecodeVarint
            except ImportError:
                self.result['detal_state'] = False
                self.result['error_message'] = "cyber_record library not installed"
                return self.result

            record = Record(self.file_path)
            channels = record.get_channel_cache()

            for ch in channels:
                self.result['channels'][ch.name] = {
                    'type': ch.message_type,
                    'count': ch.message_number,
                }
                self.result['message_count'][ch.name] = ch.message_number

            count = 0
            for chunk_header_index, chunk_body_index in record._reader.sorted_chunk_indexs:
                if count >= self.max_messages:
                    break

                pos = chunk_header_index.position
                record._reader._set_position(pos)

                section_type = int.from_bytes(record._reader._read(4), byteorder='little')
                record._reader._skip_size(4)
                section_size = int.from_bytes(record._reader._read(8), byteorder='little')
                data = record._reader._read(section_size)

                offset = 0
                while offset < len(data) and count < self.max_messages:
                    try:
                        tag = data[offset]
                        field_num = tag >> 3
                        wire_type = tag & 0x7

                        if field_num != 1 or wire_type != 2:
                            break

                        msg_len, new_offset = _DecodeVarint(data, offset + 1)
                        single_msg = record_pb2.SingleMessage()
                        single_msg.ParseFromString(data[new_offset:new_offset + msg_len])

                        topic = single_msg.channel_name
                        timestamp = single_msg.time

                        self.result['message_count'][topic] = self.result['message_count'].get(topic, 0) + 1

                        msg_data = {
                            'channel': topic,
                            'timestamp': timestamp,
                        }

                        message_type = record._reader.message_type_pool.get(topic)
                        if message_type:
                            message = message_type()
                            message.ParseFromString(single_msg.content)
                            _extract_message_data(message, msg_data)

                        self.result['messages'].append(msg_data)
                        count += 1
                        offset = new_offset + msg_len

                    except Exception as e:
                        if self.verbose:
                            print(f"Parse error: {e}")
                        break

        except Exception as e:
            self.result['detal_state'] = False
            self.result['error_message'] = str(e)

        return self.result


def parse_record(
    file_path: str,
    channel: str = None,
    max_messages: int = 10,
    export: str = None,
    verbose: bool = True
) -> Dict:
    """使用cyber_record库解析record文件

    Args:
        file_path: record文件路径
        channel: 可选，指定解析的通道
        max_messages: 最大消息数
        export: 导出文件路径
        verbose: 是否显示详细信息

    Returns:
        解析结果字典
    """
    try:
        from cyber_record.record import Record
        from cyber_record.cyber.proto import record_pb2
        from google.protobuf.internal.decoder import _DecodeVarint
    except ImportError:
        print("错误: 未安装 cyber_record 库")
        print("\n请运行以下命令安装:")
        print("  pip install cyber-record protobuf==3.20.3")
        print("\n或者使用 uv:")
        print("  uv add cyber-record protobuf==3.20.3")
        sys.exit(1)

    record = Record(file_path)
    channels = record.get_channel_cache()
    result = {
        'file_path': file_path,
        'file_size': os.path.getsize(file_path),
        'channels': {},
        'messages': [],
    }

    if verbose:
        print(f"\n{'='*60}")
        print("Apollo Record 文件信息")
        print(f"{'='*60}")
        print(f"文件: {file_path}")
        print(f"大小: {result['file_size']:,} 字节")
        print(f"\n发现 {len(channels)} 个通道:\n")
        _print_channel_groups(channels)

    # 收集通道信息
    for ch in channels:
        result['channels'][ch.name] = {
            'type': ch.message_type,
            'count': ch.message_number,
        }

    # 解析消息（使用手动解析，因为 cyber_record 的 read_messages 有 bug）
    if verbose:
        print(f"\n{'='*60}")
        print("消息数据解析")
        print(f"{'='*60}")

    count = 0
    channel_filter = channel

    # 手动遍历 chunk 并解析消息
    for chunk_header_index, chunk_body_index in record._reader.sorted_chunk_indexs:
        if count >= max_messages:
            break

        # 注意：Apollo record 文件中，chunk_header 和 chunk_body 的位置是反的
        # 需要使用 chunk_header_index.position 来读取 chunk body
        pos = chunk_header_index.position
        record._reader._set_position(pos)

        # 读取 section header
        section_type = int.from_bytes(record._reader._read(4), byteorder='little')
        record._reader._skip_size(4)  # skip size field
        section_size = int.from_bytes(record._reader._read(8), byteorder='little')
        data = record._reader._read(section_size)

        # 手动解析 protobuf 消息
        offset = 0
        while offset < len(data) and count < max_messages:
            try:
                tag = data[offset]
                field_num = tag >> 3
                wire_type = tag & 0x7

                if field_num != 1 or wire_type != 2:
                    break

                # 读取消息长度
                msg_len, new_offset = _DecodeVarint(data, offset + 1)

                # 解析 SingleMessage
                single_msg = record_pb2.SingleMessage()
                single_msg.ParseFromString(data[new_offset:new_offset + msg_len])

                topic = single_msg.channel_name
                timestamp = single_msg.time

                # 过滤通道
                if channel_filter and topic != channel_filter:
                    offset = new_offset + msg_len
                    continue

                # 创建消息类型实例
                message_type = record._reader.message_type_pool.get(topic)
                if message_type:
                    message = message_type()
                    message.ParseFromString(single_msg.content)
                else:
                    message = None

                count += 1
                msg_data = {
                    'channel': topic,
                    'timestamp': timestamp,
                }

                if verbose:
                    _print_message(count, topic, timestamp, message)

                # 提取消息内容
                if message:
                    _extract_message_data(message, msg_data)

                result['messages'].append(msg_data)
                offset = new_offset + msg_len

            except Exception as e:
                if verbose:
                    print(f"  解析错误: {e}")
                break

    if verbose:
        print(f"\n共解析 {count} 条消息")

    # 导出
    if export:
        result['export_time'] = datetime.now().isoformat()
        with open(export, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n已导出到: {export}")

    return result


def _extract_message_data(message, msg_data: Dict):
    """提取消息数据"""
    if hasattr(message, 'pose'):
        try:
            msg_data['position'] = {
                'x': message.pose.position.x,
                'y': message.pose.position.y,
                'z': message.pose.position.z,
            }
            msg_data['velocity'] = {
                'x': message.pose.linear_velocity.x,
                'y': message.pose.linear_velocity.y,
            }
        except AttributeError:
            pass
    elif hasattr(message, 'speed_mps'):
        try:
            msg_data['speed_mps'] = message.speed_mps
            msg_data['throttle'] = message.throttle_percentage
            msg_data['brake'] = message.brake_percentage
        except AttributeError:
            pass


def _print_channel_groups(channels):
    """按类别分组打印通道"""
    groups = {
        '定位': [], '传感器': [], '感知': [],
        '规划': [], '控制': [], '其他': []
    }

    for ch in channels:
        name = ch.name.lower()
        if 'localization' in name or 'pose' in name:
            groups['定位'].append(ch)
        elif 'sensor' in name or 'gnss' in name:
            groups['传感器'].append(ch)
        elif 'perception' in name:
            groups['感知'].append(ch)
        elif 'planning' in name:
            groups['规划'].append(ch)
        elif 'control' in name:
            groups['控制'].append(ch)
        else:
            groups['其他'].append(ch)

    for group, chs in groups.items():
        if chs:
            print(f"[{group}]")
            for ch in sorted(chs, key=lambda x: x.name):
                print(f"  {ch.name}: {ch.message_number} 条 ({ch.message_type})")
            print()


def _print_message(index: int, topic: str, timestamp: int, message):
    """打印消息内容"""
    print(f"\n[消息 #{index}]")
    print(f"  通道: {topic}")
    print(f"  时间戳: {timestamp}")

    if hasattr(message, 'pose'):
        print(f"  位置: x={message.pose.position.x:.4f}, "
              f"y={message.pose.position.y:.4f}")
        print(f"  速度: vx={message.pose.linear_velocity.x:.4f}")
    elif hasattr(message, 'speed_mps'):
        print(f"  速度: {message.speed_mps:.2f} m/s")
        print(f"  油门: {message.throttle_percentage:.1f}%")
        print(f"  刹车: {message.brake_percentage:.1f}%")
    else:
        print(f"  消息类型: {type(message).__name__}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Apollo Record 文件解析器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python record_parse.py
    python record_parse.py demo.record
    python record_parse.py demo.record -c /apollo/localization/pose
    python record_parse.py demo.record -e output.json -m 20
        """
    )

    parser.add_argument('file', nargs='?',
                       default='/home/ubuntu/Code_Practice/media/uploads/demo_3.5.record',
                       help='Record文件路径')
    parser.add_argument('--channel', '-c', help='指定解析的通道')
    parser.add_argument('--export', '-e', help='导出到JSON文件')
    parser.add_argument('--max', '-m', type=int, default=10,
                       help='最大消息数 (默认: 10)')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"错误: 文件不存在 - {args.file}")
        sys.exit(1)

    print(f"\n{'#'*60}")
    print(f"# Apollo Record 文件解析器 (cyber_record)")
    print(f"# 文件: {args.file}")
    print(f"{'#'*60}")

    parse_record(
        args.file,
        channel=args.channel,
        max_messages=args.max,
        export=args.export,
    )

    print(f"\n{'='*60}")
    print("解析完成!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
