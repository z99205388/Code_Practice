# Quick Test Guide

## 快速测试指南

本指南将帮助您快速测试新的数据处理功能。

### 测试步骤

#### 1. 启动 Django 服务器

```bash
cd /home/ubuntu/Code/Code_Practice/Learning_Log
source ll_env/bin/activate
python manage.py runserver
```

#### 2. 访问数据可视化页面

在浏览器中打开：
```
http://localhost:8000/data_visualization/
```

#### 3. 点击"执行处理"按钮

点击页面顶部的绿色"执行处理"按钮。

### 测试方案

#### 方案 A：使用预设的本地文件路径

1. 在"Or Use Local File Path"部分
2. File Path 字段已预填充：
   ```
   /home/ubuntu/Code/Code_Practice/Data_Visuallization/plot_temperatures/death_valley_2014.csv
   ```
3. 选择图表类型：Line Chart 或 Bar Chart
4. 输入图表标题：My Temperature Chart
5. 点击"Process File"按钮

#### 方案 B：使用测试 CSV 文件

1. 在"Or Use Local File Path"部分
2. 输入文件路径：
   ```
   /home/ubuntu/Code/Code_Practice/Learning_Log/media/uploads/test_temperature_data.csv
   ```
3. 选择图表类型：Line Chart
4. 输入图表标题：Monthly Temperature Data
5. 点击"Process File"按钮

#### 方案 C：使用测试 JSON 文件

1. 在"Or Use Local File Path"部分
2. 输入文件路径：
   ```
   /home/ubuntu/Code/Code_Practice/Learning_Log/media/uploads/test_sales_data.json
   ```
3. 选择图表类型：Bar Chart 或 Pie Chart
4. 输入图表标题：Product Sales Data
5. 点击"Process File"按钮

#### 方案 D：上传自己的文件

1. 在"Upload a File"部分
2. 点击"Choose File"按钮
3. 选择本地 CSV、JSON 或 TXT 文件
4. 选择图表类型
5. 输入图表标题
6. 点击"Upload & Process"按钮

### 测试不同图表类型

使用相同的数据文件，尝试不同的图表类型：

1. **Line Chart (折线图)**: 适合展示趋势数据
2. **Bar Chart (柱状图)**: 适合比较不同类别的数值
3. **Scatter Plot (散点图)**: 需要至少两列数值数据
4. **Histogram (直方图)**: 展示数据分布
5. **Pie Chart (饼图)**: 展示部分与整体的关系

### 预期结果

#### 成功情况

- 显示绿色的成功提示框
- 显示生成的图表
- 显示图表详细信息
- 提供后续操作按钮

#### 失败情况

- 显示红色的错误提示框
- 显示错误信息
- 提供"Try Again"按钮返回处理页面

### 常见测试文件

项目已提供以下测试文件：

1. **test_temperature_data.csv**
   - 位置: `/home/ubuntu/Code/Code_Practice/Learning_Log/media/uploads/test_temperature_data.csv`
   - 内容: 12个月的温度数据
   - 推荐图表: Line Chart, Bar Chart

2. **test_sales_data.json**
   - 位置: `/home/ubuntu/Code/Code_Practice/Learning_Log/media/uploads/test_sales_data.json`
   - 内容: 5个产品的销售数据
   - 推荐图表: Bar Chart, Pie Chart

3. **death_valley_2014.csv**
   - 位置: `/home/ubuntu/Code/Code_Practice/Data_Visuallization/plot_temperatures/death_valley_2014.csv`
   - 内容: 死亡谷2014年365天的温度数据
   - 推荐图表: Line Chart, Histogram

### 测试检查清单

- [ ] 服务器正常启动
- [ ] 数据可视化主页可以访问
- [ ] "执行处理"按钮存在并可点击
- [ ] 数据处理页面正常显示
- [ ] 文件上传功能可用
- [ ] 本地文件路径功能可用
- [ ] 图表类型选择器工作正常
- [ ] 标题和描述输入框正常
- [ ] 处理按钮可提交表单
- [ ] 成功处理数据后显示结果页面
- [ ] 生成的图表正确显示
- [ ] 图表详情信息正确
- [ ] 导航链接工作正常

### 问题排查

如果遇到问题，请检查：

1. **服务器未启动**:
   - 检查是否有其他进程占用端口 8000
   - 尝试使用不同端口：`python manage.py runserver 0.0.0.0:8001`

2. **文件路径错误**:
   - 确认文件路径是绝对路径
   - 检查文件是否存在且有读取权限

3. **图表生成失败**:
   - 检查数据文件格式是否正确
   - 确认 matplotlib 已正确安装

4. **页面无法访问**:
   - 确认用户已登录（某些页面需要认证）
   - 检查浏览器控制台是否有错误

### 测试完成后的清理

生成的图表保存在：
```
/home/ubuntu/Code/Code_Practice/Learning_Log/media/charts/
```

如需清理，可以删除这些文件或运行：
```bash
rm -rf /home/ubuntu/Code/Code_Practice/Learning_Log/media/charts/chart_*
```

数据库记录可通过 Django Admin 界面或 Shell 清理。

### 反馈

如有任何问题或建议，请记录：
- 使用的测试方案
- 遇到的具体错误信息
- 浏览器和操作系统信息
