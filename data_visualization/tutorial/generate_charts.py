#!/usr/bin/env python3
"""
脚本：生成所有数据可视化图表图片

运行此脚本将生成图表图片并保存到 media/charts 目录
"""

import os
import csv
import sys
from datetime import datetime

# 添加 Data_Visuallization/random_walk 路径到 Python 路径
DATA_DIR = '/home/ubuntu/Code/Code_Practice/Data_Visuallization'
CHART_DIR = '/home/ubuntu/Code/Code_Practice/Learning_Log/media/charts'

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt

def ensure_chart_dir():
    """确保图表目录存在"""
    if not os.path.exists(CHART_DIR):
        os.makedirs(CHART_DIR)

def generate_temperature_chart():
    """生成温度高低图表"""
    ensure_chart_dir()

    filename = os.path.join(DATA_DIR, 'plot_temperatures', 'death_valley_2014.csv')
    output_path = os.path.join(CHART_DIR, 'death_valley_temperatures.png')

    # 从文件中获取日期、最高气温和最低气温
    with open(filename) as f:
        reader = csv.reader(f)
        header_row = next(reader)
        dates, highs, lows = [], [], []
        for row in reader:
            try:
                current_date = datetime.strptime(row[0], "%Y-%m-%d")
                high = int(row[1])
                low = int(row[3])

            except ValueError:
                print(current_date, 'missing data')
            else:
                dates.append(current_date)
                highs.append(high)
                lows.append(low)

    # 根据数据绘制图形
    fig = plt.figure(dpi=128, figsize=(10, 6))
    plt.plot(dates, highs, c='red', alpha=0.5)
    plt.plot(dates, lows, c='blue', alpha=0.5)
    plt.fill_between(dates, highs, lows, facecolor='blue', alpha=0.1)

    # 设置图形的格式
    title = "Daily high and low temperatures - 2014\nDeath Valley, CA"
    plt.title(title, fontsize=24)
    plt.xlabel(' ', fontsize=16)
    fig.autofmt_xdate()
    plt.ylabel("Temperature (F)", fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    return output_path

def generate_random_walk_chart():
    """生成随机漫步图表"""
    ensure_chart_dir()

    output_path = os.path.join(CHART_DIR, 'random_walk.png')

    # 添加 random_walk 模块路径
    sys.path.append(os.path.join(DATA_DIR, 'random_walk'))
    from random_walk import Randomwalk

    # 创建一个 RandomWalk 实例
    rw = Randomwalk(5000)
    rw.fill_walk()

    # 设置绘图窗口的尺寸
    plt.figure(dpi=128, figsize=(10, 6))

    point_numbers = list(range(rw.num_points))
    plt.scatter(rw.x_values, rw.y_values, c=point_numbers, cmap=plt.cm.Blues, edgecolors='none', s=1)

    # 突出起点和终点
    plt.scatter(0, 0, c='green', edgecolors='none', s=100)
    plt.scatter(rw.x_values[-1], rw.y_values[-1], c='red', edgecolors='none', s=100)

    # 隐藏坐标轴
    plt.axis('off')

    # 保存图表
    plt.savefig(output_path, bbox_inches='tight', dpi=128)
    plt.close()

    return output_path

def main():
    print("开始生成数据可视化图表...")

    # 1. 生成温度图表
    print("\n生成温度图表...")
    try:
        temp_chart_path = generate_temperature_chart()
        print(f"✓ 温度图表已生成: {temp_chart_path}")
    except Exception as e:
        print(f"✗ 温度图表生成失败: {e}")
        import traceback
        traceback.print_exc()

    # 2. 生成随机漫步图表
    print("\n生成随机漫步图表...")
    try:
        rw_chart_path = generate_random_walk_chart()
        print(f"✓ 随机漫步图表已生成: {rw_chart_path}")
    except Exception as e:
        print(f"✗ 随机漫步图表生成失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n图表生成完成！")

if __name__ == '__main__':
    main()
