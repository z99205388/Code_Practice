# Data Visualization Integration in Learning Log

## 概述

已成功将 Data_Visuallization 目录下的数据可视化项目集成到 Learning_Log Django web 应用中。

## 集成内容

### 1. 创建的 Django 应用

- **应用名称**: `data_visualization`
- **模型**: `Chart` - 存储图表信息（标题、描述、类别、图片路径等）
- **视图**: `index`, `charts`, `chart_detail` - 处理图表展示
- **模板**: HTML 模板用于展示图表列表和详情
- **URL 配置**: 路由配置

### 2. 已集成的可视化项目

从 Data_Visuallization 目录集成了以下项目：

1. **温度可视化** (`plot_temperatures`)
   - 图表：Death Valley 2014 年日最高/最低气温
   - 类别：Temperature
   - 数据文件：death_valley_2014.csv

2. **随机漫步可视化** (`random_walk`)
   - 图表：5000 点的随机漫步可视化
   - 类别：Random Walk
   - 算法生成

### 3. 目录结构

```
Learning_Log/
├── data_visualization/
│   ├── management/commands/
│   │   └── create_charts.py       # Django 管理命令
│   ├── scripts/
│   │   ├── generate_charts.py     # 图表生成脚本
│   │   ├── temperature_chart.py   # 温度图表生成
│   │   └── random_walk_chart.py    # 随机漫步图表生成
│   ├── templates/data_visualization/
│   │   ├── base.html               # 基础模板
│   │   ├── index.html              # 图表画廊主页
│   │   ├── charts.html             # 所有图表列表
│   │   └── chart_detail.html       # 图表详情页
│   ├── models.py                   # Chart 模型
│   ├── views.py                    # 视图函数
│   └── urls.py                     # URL 配置
├── media/charts/                   # 生成的图表图片
│   ├── death_valley_temperatures.png
│   └── random_walk.png
└── generate_charts.py              # 独立的图表生成脚本
```

## 使用说明

### 1. 启动开发服务器

```bash
cd /home/ubuntu/Code/Code_Practice/Learning_Log
source ll_env/bin/activate
python manage.py runserver
```

### 2. 访问数据可视化页面

- **主页**: http://localhost:8000/data_visualization/
- **所有图表**: http://localhost:8000/data_visualization/charts/
- **特定图表**: http://localhost:8000/data_visualization/charts/1/

### 3. 添加新的图表

#### 方法一：使用 Django 管理命令

```bash
cd /home/ubuntu/Code/Code_Practice/Learning_Log
source ll_env/bin/activate
python manage.py create_charts
```

#### 方法二：使用独立脚本

```bash
cd /home/ubuntu/Code/Code_Practice/Learning_Log
python3 generate_charts.py
```

### 4. 导航

在 Learning Log 主页和导航栏中已添加 "Data Visualization" 链接，可以快速访问数据可视化画廊。

## 技术细节

### 数据库模型 (Chart)

```python
class Chart(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    image_path = models.CharField(max_length=500)
    date_added = models.DateTimeField(auto_now_add=True)
    data_file = models.CharField(max_length=500, blank=True)
    script_file = models.CharField(max_length=500)
```

### 图表生成流程

1. 使用 matplotlib 读取数据或运行算法
2. 生成图表并保存为 PNG 格式到 `media/charts/` 目录
3. 在数据库中创建对应的 Chart 记录
4. 通过 Django 模板展示图表

### 静态文件和媒体文件配置

在 `learning_log/settings.py` 中已配置：

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

在 `learning_log/urls.py` 中已添加媒体文件服务：

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 注意事项

1. **matplotlib 依赖**: 图表生成需要 matplotlib 库，已在系统环境中安装（Python 3.11 + matplotlib 3.6.3）

2. **虚拟环境**: 虚拟环境 `ll_env` 中未安装 matplotlib，使用系统 Python 运行图表生成脚本

3. **数据文件**: 温度图表需要 CSV 数据文件，路径为 `/home/ubuntu/Code/Code_Practice/Data_Visuallization/plot_temperatures/death_valley_2014.csv`

4. **图片路径**: 所有图表图片保存在 `media/charts/` 目录中，并通过 `/media/charts/` URL 访问

## 未来扩展

可以继续集成 Data_Visuallization 目录中的其他项目：

- **heaker_news**: Hacker News 数据可视化
- **python_repose**: Python 仓库数据可视化
- **world_population_maps**: 世界人口地图可视化

只需为每个项目创建对应的图表生成脚本和数据库记录即可。
