# Data Visualization - Complete Feature Set

## 完整功能说明

本文档总结了 Data Visualization 模块的所有功能。

---

## 🎨 原有功能

### 1. 图表画廊
- 展示所有已创建的数据可视化图表
- 按类别分组显示
- 图表缩略图预览
- 点击查看详情

### 2. 图表详情页
- 显示完整图表
- 图表元信息（标题、类别、日期等）
- 数据文件和脚本文件路径
- 详细描述

### 3. 预设图表

#### 温度可视化
- **标题**: Death Valley Temperatures 2014
- **类别**: Temperature
- **描述**: 死亡谷2014年每日最高和最低气温
- **数据文件**: death_valley_2014.csv

#### 随机漫步可视化
- **标题**: Random Walk Visualization
- **类别**: Random Walk
- **描述**: 5000点的随机漫步可视化
- **算法**: 生成算法

---

## ✨ 新增功能

### 1. 数据执行处理

#### 功能入口
- **位置**: 数据可视化主页顶部
- **按钮**: "执行处理"（绿色大按钮）
- **操作**: 点击后跳转到数据处理页面

#### 数据处理页面

**方式一：文件上传**
- 支持格式：CSV、JSON、TXT
- 操作流程：
  1. 点击"选择文件"按钮
  2. 选择本地文件
  3. 选择图表类型
  4. 输入标题和描述
  5. 点击"Upload & Process"

**方式二：本地文件路径**
- 支持服务器上的任何文件
- 预设示例：death_valley_2014.csv
- 操作流程：
  1. 输入文件完整路径
  2. 选择图表类型
  3. 输入标题和描述
  4. 点击"Process File"

#### 支持的图表类型

1. **Line Chart（折线图）**
   - 用途：展示数据随时间或类别的变化趋势
   - 适用：时间序列数据、连续数据

2. **Bar Chart（柱状图）**
   - 用途：比较不同类别的数值大小
   - 适用：分类数据、排名数据

3. **Scatter Plot（散点图）**
   - 用途：展示两个变量之间的关系
   - 适用：相关性分析、分布分析

4. **Histogram（直方图）**
   - 用途：展示数据的分布情况
   - 适用：频率分布、统计特征

5. **Pie Chart（饼图）**
   - 用途：展示各部分占整体的比例
   - 适用：占比分析、构成分析

#### 结果展示页面

**成功状态**
- 绿色成功提示
- 生成的图表预览
- 图表详细信息
- 导航按钮：
  - 查看完整详情
  - 所有图表
  - 处理新文件
  - 返回画廊

**失败状态**
- 红色错误提示
- 错误信息显示
- 文件路径信息
- 重试按钮

---

## 🚀 快速开始

### 1. 查看预设图表

```
http://localhost:8000/data_visualization/
```

浏览已创建的温度和随机漫步图表。

### 2. 处理自己的数据

**步骤 1**: 点击"执行处理"按钮

**步骤 2**: 选择数据源
- 上传本地文件，或
- 输入服务器文件路径

**步骤 3**: 配置图表
- 选择图表类型
- 输入标题（必填）
- 输入描述（可选）

**步骤 4**: 提交处理
- 点击"Upload & Process"或"Process File"

**步骤 5**: 查看结果
- 系统自动生成图表
- 显示处理结果页面

---

## 📁 文件和目录

### 项目结构

```
Learning_Log/
├── data_visualization/
│   ├── templates/data_visualization/
│   │   ├── base.html                 # 基础模板
│   │   ├── index.html                # 主页（含执行按钮）
│   │   ├── charts.html               # 所有图表列表
│   │   ├── chart_detail.html         # 图表详情
│   │   ├── process_data.html         # 数据处理页面 ⭐
│   │   └── process_result.html       # 结果展示页面 ⭐
│   ├── views.py                      # 视图函数
│   ├── urls.py                       # URL 配置
│   ├── models.py                     # 数据模型
│   └── scripts/                      # 图表生成脚本
├── media/
│   ├── charts/                       # 生成的图表
│   └── uploads/                      # 上传的数据 ⭐
└── 文档/
    ├── DATA_VISUALIZATION_README.md   # 原功能说明
    ├── DATA_PROCESSING_README.md     # 新功能说明 ⭐
    ├── QUICK_TEST_GUIDE.md            # 快速测试指南 ⭐
    └── IMPLEMENTATION_SUMMARY.md     # 实现总结 ⭐
```

### 测试数据

- `media/uploads/test_temperature_data.csv` - 温度数据示例
- `media/uploads/test_sales_data.json` - 销售数据示例
- `/home/ubuntu/Code/Code_Practice/Data_Visuallization/` - 完整示例数据集

---

## 💡 使用技巧

### CSV 文件格式要求

```csv
Column1,Column2,Column3
value1,value2,value3
value4,value5,value6
...
```

- 第一行：列标题（可选但推荐）
- 数据行：每行一条记录
- 分隔符：逗号

### JSON 文件格式要求

```json
[
  {"name": "A", "value": 10},
  {"name": "B", "value": 20},
  ...
]
```

- 格式：数组格式
- 每个元素：包含键值对的对象
- 推荐：包含 name/value 或 label/value 键

### 图表类型选择建议

| 数据类型 | 推荐图表类型 |
|---------|-------------|
| 时间序列 | Line Chart |
| 分类比较 | Bar Chart |
| 相关性分析 | Scatter Plot |
| 分布分析 | Histogram |
| 占比分析 | Pie Chart |

---

## 🔧 配置说明

### Django 配置

**文件**: `learning_log/settings.py`

```python
# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 已安装应用
INSTALLED_APPS = [
    ...
    'data_visualization',
]
```

**文件**: `learning_log/urls.py`

```python
urlpatterns = [
    ...
    path('data_visualization/', include('data_visualization.urls')),
]

# 开发环境媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### URL 路由

| 路径 | 名称 | 说明 |
|------|------|------|
| `/data_visualization/` | `index` | 数据可视化主页 |
| `/data_visualization/charts/` | `charts` | 所有图表列表 |
| `/data_visualization/charts/<id>/` | `chart_detail` | 图表详情 |
| `/data_visualization/process/` | `process_data` | 数据处理 ⭐ |

---

## 📊 功能对比

| 功能 | 原版本 | 新版本 |
|------|--------|--------|
| 查看预设图表 | ✅ | ✅ |
| 图表详情页 | ✅ | ✅ |
| 上传数据文件 | ❌ | ✅ ⭐ |
| 本地文件路径 | ❌ | ✅ ⭐ |
| 自动数据处理 | ❌ | ✅ ⭐ |
| 多图表类型 | 2种 | 5种 ⭐ |
| 自定义标题 | ❌ | ✅ ⭐ |
| 添加描述 | ❌ | ✅ ⭐ |
| 结果展示页 | ❌ | ✅ ⭐ |
| 错误处理 | ❌ | ✅ ⭐ |

---

## 🎓 使用示例

### 示例 1：上传 CSV 文件

1. 准备 CSV 文件：
```csv
Product,Sales
A,100
B,150
C,120
```

2. 上传并配置：
   - 文件：选择上述 CSV
   - 图表类型：Bar Chart
   - 标题：Product Sales
   - 描述：第一季度销售数据

3. 查看结果：系统自动生成柱状图

### 示例 2：使用本地 JSON 文件

1. 准备 JSON 文件：
```json
[
  {"month": "Jan", "revenue": 1000},
  {"month": "Feb", "revenue": 1200},
  {"month": "Mar", "revenue": 900}
]
```

2. 配置：
   - 文件路径：`/path/to/data.json`
   - 图表类型：Line Chart
   - 标题：Monthly Revenue

3. 查看结果：生成折线图展示趋势

### 示例 3：使用预设数据

1. 使用示例路径：
```
/home/ubuntu/Code/Code_Practice/Data_Visuallization/plot_temperatures/death_valley_2014.csv
```

2. 配置：
   - 图表类型：Line Chart
   - 标题：Temperature Analysis

3. 查看结果：生成温度趋势图

---

## ⚠️ 注意事项

1. **文件权限**: 确保对本地文件有读取权限
2. **文件格式**: 验证数据文件格式正确
3. **数据大小**: 大文件可能影响性能
4. **图表数量**: 最多显示前 50 个数据点
5. **用户登录**: 某些功能需要登录
6. **字符编码**: CSV 文件建议使用 UTF-8 编码

---

## 🐛 故障排除

### 问题：文件上传失败
**解决方案**：
- 检查文件大小（< 10MB）
- 验证文件格式（CSV/JSON/TXT）
- 检查上传目录权限

### 问题：图表生成错误
**解决方案**：
- 确认数据格式正确
- 检查图表类型是否适合数据
- 查看错误信息

### 问题：页面无法访问
**解决方案**：
- 确认服务器正在运行
- 检查用户是否已登录
- 验证 URL 路由配置

---

## 📞 支持

### 文档
- 完整功能说明：`DATA_PROCESSING_README.md`
- 快速测试指南：`QUICK_TEST_GUIDE.md`
- 实现总结：`IMPLEMENTATION_SUMMARY.md`

### 联系方式
- 问题反馈：https://cnb.cool/codebuddy/codebuddy-code/-/issues

---

## 🎉 总结

Data Visualization 模块现在提供：

1. **预设图表库**: 温度、随机漫步等示例
2. **自定义处理**: 上传或指定数据文件
3. **多种图表**: 5种专业图表类型
4. **智能处理**: 自动识别和生成
5. **友好界面**: 直观的操作流程
6. **完整文档**: 详细的使用说明

开始使用：访问 http://localhost:8000/data_visualization/

享受数据可视化的便利！
