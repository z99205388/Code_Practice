import csv
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
from matplotlib import pyplot as plt
from datetime import datetime
import os

# 设置图表保存目录
CHART_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'charts')

# Data_Visuallization 目录路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Code_Practice', 'Data_Visuallization')

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

    return {
        'title': 'Death Valley Temperatures 2014',
        'description': 'Daily high and low temperatures recorded in Death Valley, California throughout 2014. This chart visualizes the extreme temperature fluctuations characteristic of this desert location.',
        'category': 'Temperature',
        'image_path': f'/media/charts/death_valley_temperatures.png',
        'data_file': f'{filename}',
        'script_file': 'data_visualization/scripts/temperature_chart.py'
    }

if __name__ == '__main__':
    chart_info = generate_temperature_chart()
    print(f"Chart generated: {chart_info['image_path']}")
    print(f"Title: {chart_info['title']}")
