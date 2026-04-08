# QWEN.md - Learning Log 项目上下文

## 项目概述

**Learning Log（学习笔记）** 是一个基于 Django 5.2 的 Web 应用程序，让用户能够记录感兴趣的主题，并在学习每个主题的过程中添加日志条目。

### 核心功能

- **用户认证系统**：注册、登录、注销
- **主题管理**：创建、查看、编辑学习主题（每个主题归属于特定用户）
- **日志条目**：在主题下添加、编辑具体的学习条目
- **数据可视化**：上传/处理数据文件（JSON、CSV、Record 格式），生成图表（折线图、柱状图、散点图、饼图等）
- **管理后台**：Django admin 管理界面

### 技术栈

| 类别 | 技术 |
|------|------|
| **后端框架** | Django 5.2 |
| **Python 版本** | >=3.11 |
| **包管理工具** | uv |
| **UI 框架** | django-bootstrap3 |
| **数据库** | SQLite3 (开发环境) |
| **图表生成** | matplotlib |
| **文件处理** | Pillow (图像处理) |
| **Record 解析** | cyber-record, record-msg, protobuf |
| **测试框架** | pytest, pytest-django, pytest-cov |
| **代码质量** | ruff (lint/format), mypy (类型检查) |

---

## 项目架构

### 应用模块

```
Code_Practice/
├── learning_log/           # Django 项目核心配置
│   ├── settings.py         # 主配置（环境变量、数据库、静态文件、安全等）
│   ├── urls.py             # 主路由（根URL重定向到 learning_logs）
│   ├── wsgi.py / asgi.py   # WSGI/ASGI 配置
│
├── learning_logs/          # 学习日志核心应用
│   ├── models.py           # Topic（主题）、Entry（条目）模型
│   ├── views.py            # CRUD 视图（topics、entries 管理）
│   ├── forms.py            # TopicForm、EntryForm 表单
│   ├── urls.py             # 应用路由
│   └── templates/          # HTML 模板
│
├── users/                  # 用户认证应用
│   ├── views.py            # 注册、登录、注销视图
│   ├── urls.py             # 用户路由
│   └── templates/          # 认证模板
│
├── data_visualization/     # 数据可视化应用
│   ├── models.py           # Chart 模型
│   ├── views.py            # 数据处理、图表生成视图
│   ├── record_parse.py     # Record 文件解析器（ApolloRecordParser）
│   ├── management/         # 管理命令
│   ├── scripts/            # 辅助脚本
│   ├── tutorial/           # 教程文件
│   └── templates/          # 可视化模板
│
├── static/                 # 项目静态文件（CSS、JS、图片等）
├── staticfiles/            # collectstatic 输出目录
├── media/                  # 媒体文件
│   ├── uploads/            # 用户上传文件
│   └── charts/             # 生成的图表文件
├── tests/                  # 测试文件
├── secret_key.env          # 环境变量（已加入 .gitignore）
├── db.sqlite3              # SQLite 数据库（已加入 .gitignore）
├── pyproject.toml          # 项目依赖和工具配置
├── start_server.sh         # 快速启动脚本
└── manage.py               # Django 管理脚本
```

### 数据模型

**learning_logs/models.py:**
- **Topic**: 学习主题，包含文本描述、创建日期、所属用户（外键到 User）
- **Entry**: 具体学习条目，关联到主题，包含详细文本内容和时间戳

**data_visualization/models.py:**
- **Chart**: 图表记录，包含标题、描述、分类、图片路径、数据文件路径等

### URL 路由

| 路径 | 应用 | 说明 |
|------|------|------|
| `/` | learning_logs | 首页（重定向到 learning_logs:index） |
| `/admin/` | admin | Django 管理后台 |
| `/learning_logs/` | learning_logs | 学习日志核心功能 |
| `/users/` | users | 用户认证（登录、注册等） |
| `/data_visualization/` | data_visualization | 数据可视化功能 |

---

## 环境配置与运行

### 快速启动（推荐）

```bash
# 使用启动脚本（自动检查环境、创建目录、启动服务器）
./start_server.sh
```

### 手动启动

```bash
# 1. 激活虚拟环境
source ll_env/bin/activate

# 2. 设置环境变量（如果需要覆盖 secret_key.env）
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0"

# 3. 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 访问地址

- 首页：http://localhost:8000/
- 学习日志：http://localhost:8000/learning_logs/
- 数据可视化：http://localhost:8000/data_visualization/
- 管理后台：http://localhost:8000/admin/

### 环境变量配置

项目使用 `secret_key.env` 文件配置敏感信息（详见 SETUP.md）：

```env
DJANGO_SECRET_KEY=<your-secret-key>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,<公网IP>,<内网IP>
```

> ⚠️ **重要**: 未配置 `DJANGO_SECRET_KEY` 会导致启动时报 `ValueError`

### 完整环境配置步骤

详细的环境配置指南（包括 uv 安装、依赖安装、数据库迁移等）请参阅 **SETUP.md** 文件。

---

## 常用命令

### Django 管理

| 命令 | 说明 |
|------|------|
| `python manage.py check` | 检查项目配置 |
| `python manage.py migrate` | 执行数据库迁移 |
| `python manage.py makemigrations` | 创建数据库迁移文件 |
| `python manage.py runserver 0.0.0.0:8000` | 启动开发服务器 |
| `python manage.py collectstatic` | 收集静态文件 |
| `python manage.py createsuperuser` | 创建管理员用户 |
| `python manage.py test` | 运行测试 |

### 虚拟环境

| 命令 | 说明 |
|------|------|
| `source ll_env/bin/activate` | 激活虚拟环境 |
| `deactivate` | 退出虚拟环境 |
| `uv venv --python 3.11 ll_env` | 创建新的虚拟环境 |

### 依赖管理

| 命令 | 说明 |
|------|------|
| `uv pip install -e .` | 使用 pyproject.toml 安装依赖 |
| `uv pip install <package>` | 安装单个包 |

### 代码质量

| 命令 | 说明 |
|------|------|
| `ruff check .` | 运行代码检查 |
| `ruff check --fix .` | 自动修复问题 |
| `ruff format .` | 格式化代码 |
| `mypy .` | 运行类型检查 |
| `pytest` | 运行测试 |
| `pytest --cov` | 运行测试并生成覆盖率报告 |
| `pytest -n auto` | 并行运行测试 |

---

## 开发约定

### 代码风格

- **行长度**: 120 字符
- **引号风格**: 双引号（`"`）
- **Python 版本**: 3.11
- **类型注解**: 鼓励使用，已配置 mypy

### 代码检查规则 (Ruff)

**启用规则**: E, F, I, N, W, UP, B, C4, DJ
**忽略规则**: E501（行长度）, F403, F405, F841

### 测试

- 测试文件位置: `tests/` 目录及各应用下的 `tests.py`、`test_*.py`、`*_tests.py`
- 测试框架: pytest + pytest-django
- 覆盖率要求: >= 55%
- 覆盖率排除: migrations, tests, __init__.py, management/commands, scripts

### 视图函数签名

视图函数使用类型注解，例如：

```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def index(request: HttpRequest) -> HttpResponse:
    return render(request, "app/template.html")
```

### 用户权限

- 需要登录的视图使用 `@login_required` 装饰器
- 用户只能访问/编辑自己创建的数据（通过 `owner` 字段过滤）
- 权限检查失败时抛出 `Http404` 或返回错误消息并重定向

### 消息框架

使用 Django messages 框架向用户显示成功/错误消息：

```python
from django.contrib import messages
messages.success(request, "操作成功！")
messages.error(request, "操作失败！")
```

---

## 数据可视化功能说明

### 支持的文件格式

| 格式 | 解析方式 |
|------|----------|
| JSON | Python json 模块 |
| CSV | Python csv 模块 |
| Record | ApolloRecordParser（cyber-record + protobuf） |

### 支持的图表类型

- line（折线图）
- bar（柱状图）
- scatter（散点图）
- histogram（直方图）
- pie（饼图）

### 数据处理流程

1. 用户上传文件或输入本地文件路径
2. 系统根据文件扩展名选择解析器
3. 解析数据并提取 X/Y 值
4. 使用 matplotlib 生成图表（保存为 PNG）
5. 创建 Chart 记录到数据库
6. 显示结果页面

---

## 安全配置

### 开发环境

- `DEBUG = True`
- SQLite 数据库
- 允许所有本地访问

### 生产环境（当 `DEBUG = False` 时自动启用）

- HTTPS 重定向
- HSTS (HTTP Strict Transport Security)
- Secure Cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- 安全头部 (SECURE_CONTENT_TYPE_NOSNIFF, X_FRAME_OPTIONS = "DENY")
- `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"` （始终启用）

---

## 重要注意事项

1. **secret_key.env 文件**: 已加入 `.gitignore`，不会被提交。新环境需要手动创建此文件。
2. **虚拟环境**: `ll_env/` 目录已加入 `.gitignore`，每个环境需要独立创建。
3. **媒体文件**: `media/` 和 `staticfiles/` 目录已加入 `.gitignore`。
4. **数据库**: `db.sqlite3` 已加入 `.gitignore`，生产环境建议使用其他数据库。
5. **Record 文件解析**: 依赖 `cyber-record` 和 `record-msg` 包，可能需要编译和安装 `python3.11-dev`。
6. **日志配置**: 已配置控制台日志记录器，可通过 `DJANGO_LOG_LEVEL` 环境变量调整级别。

---

## 相关文件

- **SETUP.md**: 完整的环境配置指南
- **pyproject.toml**: 项目依赖和工具配置
- **start_server.sh**: 快速启动脚本
- **secret_key.env.new**: secret_key.env 模板文件

---

*生成日期: 2026-04-09*
