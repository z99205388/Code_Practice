# Data Visualization - Data Processing Feature

## 概述

已成功为 Data Visualization 页面添加数据执行处理功能，用户可以：
1. 点击"执行处理"按钮进入数据处理页面
2. 上传本地数据文件或指定服务器上的文件路径
3. 选择图表类型并自定义标题和描述
4. 自动处理数据并生成可视化图表
5. 在页面上查看生成的图表和详细信息

## 新增功能

### 1. 执行处理按钮

在 Data Visualization 主页顶部添加了一个醒目的"执行处理"按钮，点击后跳转到数据处理页面。

**位置**: `/home/ubuntu/Code/Code_Practice/Learning_Log/data_visualization/templates/data_visualization/index.html`

### 2. 数据处理页面

提供了两种数据输入方式：

#### 方式一：文件上传
- 支持上传本地数据文件（CSV、JSON、TXT 格式）
- 指定图表类型（折线图、柱状图、散点图、直方图、饼图）
- 自定义图表标题和描述

#### 方式二：本地文件路径
- 输入服务器上数据文件的完整路径
- 预设了示例文件路径（death_valley_2014.csv）
- 支持相同的图表类型和自定义选项

**模板文件**: `/home/ubuntu/Code/Code_Practice/Learning_Log/data_visualization/templates/data_visualization/process_data.html`

### 3. 数据处理逻辑

自动识别和处理不同格式的数据文件：

- **CSV 文件**: 读取 CSV 数据，根据表头和内容生成图表
- **JSON 文件**: 解析 JSON 数据，提取关键信息生成图表
- **其他格式**: 默认按 CSV 格式处理

**视图函数**: `data_visualization/views.py` 中的 `process_data()` 和 `handle_data_processing()`

### 4. 图表生成功能

支持多种图表类型：

1. **Line Chart (折线图)**: 展示数据随时间或类别的变化趋势
2. **Bar Chart (柱状图)**: 比较不同类别的数值大小
3. **Scatter Plot (散点图)**: 展示两个变量之间的关系
4. **Histogram (直方图)**: 展示数据分布情况
5. **Pie Chart (饼图)**: 展示各部分占整体的比例

### 5. 结果展示页面

处理完成后显示：
- 成功/失败提示信息
- 生成的图表预览
- 图表详细信息（标题、类别、日期等）
- 数据文件路径和处理脚本信息
- 导航链接（查看详情、所有图表、处理新文件等）

**模板文件**: `/home/ubuntu/Code/Code_Practice/Learning_Log/data_visualization/templates/data_visualization/process_result.html`

## 使用流程

### 步骤 1: 访问数据可视化主页

```
http://localhost:8000/data_visualization/
```

### 步骤 2: 点击"执行处理"按钮

点击页面顶部绿色的"执行处理"按钮。

### 步骤 3: 选择数据源

**选项 A - 上传文件**:
1. 点击"选择文件"按钮
2. 从本地选择 CSV、JSON 或 TXT 文件
3. 选择图表类型
4. 输入图表标题（必填）
5. 输入描述（可选）
6. 点击"Upload & Process"按钮

**选项 B - 使用本地路径**:
1. 在"File Path"输入框中输入服务器上文件的完整路径
2. 选择图表类型
3. 输入图表标题（必填）
4. 输入描述（可选）
5. 点击"Process File"按钮

### 步骤 4: 查看结果

系统会自动处理数据并生成图表，然后显示结果页面，包括：
- 处理成功提示
- 生成的图表预览
- 图表详细信息
- 后续操作选项

## 文件结构

```
Learning_Log/
├── data_visualization/
│   ├── templates/data_visualization/
│   │   ├── base.html
│   │   ├── index.html                    # 主页（添加了执行处理按钮）
│   │   ├── charts.html
│   │   ├── chart_detail.html
│   │   ├── process_data.html             # 数据处理页面（新增）
│   │   └── process_result.html           # 结果展示页面（新增）
│   ├── views.py                          # 视图函数（新增处理逻辑）
│   └── urls.py                           # URL 配置（新增路由）
├── media/
│   ├── charts/                           # 生成的图表文件
│   └── uploads/                          # 上传的数据文件（新增）
└── DATA_PROCESSING_README.md             # 本说明文档
```

## 技术实现

### 视图函数

1. **process_data()**: 处理数据选择页面
   - GET: 显示表单
   - POST: 处理文件上传或本地路径

2. **handle_data_processing()**: 核心处理逻辑
   - 读取数据文件
   - 生成图表
   - 保存到数据库
   - 返回结果页面

3. **generate_chart_from_csv()**: CSV 文件处理
   - 读取 CSV 数据
   - 根据图表类型生成相应图表

4. **generate_chart_from_json()**: JSON 文件处理
   - 解析 JSON 数据
   - 提取并可视化关键信息

### URL 路由

```python
urlpatterns = [
    path('', views.index, name='index'),
    path('charts/', views.charts, name='charts'),
    path('charts/<int:chart_id>/', views.chart_detail, name='chart_detail'),
    path('process/', views.process_data, name='process_data'),  # 新增
]
```

### 数据模型

使用现有的 `Chart` 模型，额外字段：
- `category`: 设置为 'Custom'（自定义图表）
- `data_file`: 存储数据文件路径
- `script_file`: 记录处理脚本信息

## 示例数据

### CSV 文件示例

```csv
Date,Temperature
2024-01-01,15
2024-01-02,18
2024-01-03,20
...
```

### JSON 文件示例

```json
[
  {"name": "A", "value": 10},
  {"name": "B", "value": 20},
  {"name": "C", "value": 15}
]
```

## 注意事项

1. **文件格式**: 目前支持 CSV、JSON 和简单的文本文件
2. **文件大小**: 建议上传小于 10MB 的文件
3. **数据结构**: CSV 文件第一行应包含列标题
4. **图表限制**: 为避免页面过慢，最多显示前 50 个数据点
5. **权限**: 处理本地文件需要用户具有读取权限

## 扩展建议

未来可以添加的功能：
1. 支持更多文件格式（Excel、XML 等）
2. 提供数据预览功能
3. 允许自定义图表颜色和样式
4. 添加图表编辑和更新功能
5. 支持多数据源合并处理
6. 添加数据验证和错误提示
7. 提供图表下载功能
8. 支持批量处理多个文件

## 故障排除

### 问题：文件上传失败
**解决方案**：
- 检查 `media/uploads` 目录权限
- 确认文件格式受支持
- 验证文件大小限制

### 问题：图表生成错误
**解决方案**：
- 检查数据文件格式是否正确
- 确认数据结构是否适合选定的图表类型
- 查看错误信息了解具体问题

### 问题：页面无法访问
**解决方案**：
- 确认 Django 服务器正在运行
- 检查 URL 配置是否正确
- 验证用户是否已登录（某些页面需要认证）

## 测试

启动服务器进行测试：

```bash
cd /home/ubuntu/Code/Code_Practice/Learning_Log
source ll_env/bin/activate
python manage.py runserver
```

访问测试页面：
- 主页: http://localhost:8000/data_visualization/
- 处理页面: http://localhost:8000/data_visualization/process/

使用预设的示例文件路径测试：
```
/home/ubuntu/Code/Code_Practice/Data_Visuallization/plot_temperatures/death_valley_2014.csv
```
