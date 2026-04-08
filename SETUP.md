# Learning Log 项目环境配置指南

> 本文档用于指导大模型快速配置项目运行环境，所有命令和源都已明确指定。

---

## 一、项目信息

| 项目 | 值 |
|------|-----|
| 框架 | Django 5.2 |
| Python 版本 | >=3.11 |
| 包管理工具 | uv |
| 虚拟环境目录 | `ll_env/` |
| 启动脚本 | `./start_server.sh` |
| 配置文件 | `pyproject.toml`, `secret_key.env` |
| 项目名称 | code-practice |

---

## 二、环境配置步骤

### 1. 安装 uv 包管理工具

```bash
# 检查是否已安装
~/.local/bin/uv --version

# 如果未安装，使用以下命令安装
curl -LsSf https://astral.sh/uv/install.sh | sh

# 如果 curl 失败，使用 pip 安装（需要 --break-system-packages）
pip install uv --break-system-packages
```

安装后路径：`~/.local/bin/uv`

---

### 2. 创建虚拟环境

```bash
cd /home/ubuntu/Code_Practice

# 使用 uv 创建 Python 3.11 虚拟环境
export PATH="$HOME/.local/bin:$PATH"
uv venv --python 3.11 ll_env

# 激活环境
source ll_env/bin/activate
```

---

### 3. 安装依赖

#### 方式一：使用 pyproject.toml 安装（推荐）

```bash
cd /home/ubuntu/Code_Practice
uv pip install -e . --python ll_env/bin/python --index-url https://mirrors.aliyun.com/pypi/simple/
```

#### 方式二：手动安装核心依赖

```bash
# 安装核心依赖
uv pip install django django-bootstrap3 matplotlib pillow protobuf==3.20.3 python-dotenv asgiref sqlparse python-dateutil packaging certifi cycler fonttools kiwisolver numpy pyparsing --python ll_env/bin/python --index-url https://mirrors.aliyun.com/pypi/simple/
```

> **国内镜像源**: `https://mirrors.aliyun.com/pypi/simple/`
>
> 备用镜像源（如果阿里云不可用）:
> - `https://pypi.tuna.tsinghua.edu.cn/simple/`
> - `https://mirrors.cloud.tencent.com/pypi/simple/`

---

### 4. 配置环境变量（secret_key.env）

创建或编辑 `secret_key.env` 文件：

```env
DJANGO_SECRET_KEY=django-insecure-^ub$8b*j%fsx_j_py&)wg38sal$*7#vs&lp#n(0&wnye2j4ixa
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,101.133.145.194,172.24.52.84
```

**配置说明：**

| 变量 | 说明 | 开发环境 | 生产环境 |
|------|------|----------|----------|
| `DJANGO_SECRET_KEY` | Django 密钥，用于签名和加密 | 使用默认值 | **必须更换**为安全的随机密钥 |
| `DJANGO_DEBUG` | 调试模式，开启后显示详细错误信息 | `True` | `False` |
| `DJANGO_ALLOWED_HOSTS` | 允许访问的主机列表，逗号分隔 | 包含 localhost 和开发 IP | 仅包含生产环境域名/IP |

**如何生成安全的 SECRET_KEY：**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**注意事项：**
- `secret_key.env` 已加入 `.gitignore`，不会被提交到版本控制
- 生产环境务必设置 `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS` 需要包含所有访问地址（本地、内网、公网）

**settings.py 加载方式：**

```python
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "secret_key.env")
load_dotenv(BASE_DIR / ".env")  # 允许用 .env 覆盖配置

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
```

> ⚠️ 如果未配置 `DJANGO_SECRET_KEY`，项目启动时会抛出 `ValueError` 错误

---

### 5. 数据库迁移

```bash
source ll_env/bin/activate
python manage.py migrate
```

---

### 6. 创建必要的目录

```bash
mkdir -p media/uploads
mkdir -p media/charts
```

---

### 7. 启动服务器

```bash
# 方式一：使用启动脚本（推荐）
./start_server.sh

# 方式二：手动启动
source ll_env/bin/activate
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0,101.133.145.194,172.24.52.84"
python manage.py runserver 0.0.0.0:8000
```

服务器绑定 `0.0.0.0:8000`，支持本地和公网访问。

**访问地址：**
- 首页：http://localhost:8000/
- 学习日志：http://localhost:8000/learning_logs/
- 数据可视化：http://localhost:8000/data_visualization/
- 管理后台：http://localhost:8000/admin/

---

## 三、常用命令速查

| 命令 | 说明 |
|------|------|
| `source ll_env/bin/activate` | 激活虚拟环境 |
| `deactivate` | 退出虚拟环境 |
| `python manage.py check` | 检查项目配置 |
| `python manage.py migrate` | 执行数据库迁移 |
| `python manage.py makemigrations` | 创建数据库迁移文件 |
| `python manage.py runserver 0.0.0.0:8000` | 启动开发服务器 |
| `python manage.py collectstatic` | 收集静态文件 |
| `python manage.py createsuperuser` | 创建管理员用户 |
| `python manage.py test` | 运行测试 |
| `uv pip install -e .` | 使用 pyproject.toml 安装依赖 |

---

## 四、项目结构

```
Code_Practice/
├── ll_env/                 # 虚拟环境（已加入 .gitignore）
├── learning_log/           # Django 项目配置
│   ├── settings.py         # 主配置
│   ├── urls.py             # 主路由
│   └── wsgi.py / asgi.py
├── learning_logs/          # 学习日志应用
├── users/                  # 用户认证应用
├── data_visualization/     # 数据可视化应用
├── static/                 # 项目静态文件
├── staticfiles/            # collectstatic 输出
├── media/                  # 媒体文件
│   ├── uploads/            # 上传文件
│   └── charts/             # 图表文件
├── tests/                  # 测试文件
├── secret_key.env          # 环境变量（已加入 .gitignore）
├── db.sqlite3              # SQLite 数据库（已加入 .gitignore）
├── pyproject.toml          # 项目依赖定义（含 pytest, ruff, mypy 配置）
├── start_server.sh         # 快速启动脚本
├── manage.py               # Django 管理脚本
└── SETUP.md                # 本文档
```

---

## 五、常见问题

### Q1: 安装依赖时超时或失败

```bash
# 使用阿里云镜像源
uv pip install <package> --python ll_env/bin/python --index-url https://mirrors.aliyun.com/pypi/simple/
```

### Q2: 提示缺少 Python.h

需要安装 Python 开发头文件：
```bash
sudo apt-get install python3.11-dev
```

### Q3: 虚拟环境权限问题

如果 `ll_env/` 目录权限异常：
```bash
rm -rf ll_env/
uv venv --python 3.11 ll_env
source ll_env/bin/activate
```

### Q4: ALLOWED_HOSTS 错误

确保 `secret_key.env` 中包含了访问 IP：
```env
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,<你的公网IP>,<你的内网IP>
```

### Q5: 端口被占用

```bash
# 查看占用 8000 端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

---

## 六、依赖列表

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| django | >=5.0 | Web 框架 |
| django-bootstrap3 | 最新 | UI 框架 |
| matplotlib | 最新 | 图表生成 |
| pillow | 最新 | 图像处理 |
| protobuf | 3.20.3 | 数据解析 |
| python-dotenv | 最新 | 环境变量加载 |
| cyber-record | >=0.1.8 | 录制文件解析 |
| record-msg | >=0.1.3 | 录制消息处理 |

### 开发依赖（optional）

| 包名 | 版本 | 用途 |
|------|------|------|
| pytest | 最新 | 测试框架 |
| pytest-django | 最新 | Django 测试支持 |
| pytest-cov | 最新 | 测试覆盖率 |
| pytest-xdist | 最新 | 并行测试 |
| ruff | 最新 | 代码检查（替代 flake8） |
| mypy | 最新 | 类型检查 |
| django-stubs | 最新 | Django 类型存根 |

### 传递依赖（自动安装）

| 包名 | 用途 |
|------|------|
| asgiref | Django 异步支持 |
| sqlparse | SQL 格式化 |
| python-dateutil | 日期处理 |
| packaging | 版本解析 |
| certifi | CA 证书 |
| cycler | 样式循环 |
| fonttools | 字体工具 |
| kiwisolver | 布局求解器 |
| numpy | 数值计算 |
| pyparsing | 解析器 |

> ⚠️ `cyber-record` 和 `record-msg` 可能需要编译，依赖 `python3.11-dev`

---

## 七、代码质量工具

项目已配置以下代码质量工具（配置见 `pyproject.toml`）：

### Ruff（代码检查）

```bash
# 运行 ruff 检查
ruff check .

# 自动修复
ruff check --fix .

# 格式化
ruff format .
```

**配置要点：**
- 行长度：120
- Python 版本：3.11
- 排除：migrations, scripts, tutorial 目录

### MyPy（类型检查）

```bash
# 运行类型检查
mypy .
```

### Pytest（测试）

```bash
# 运行测试
pytest

# 带覆盖率
pytest --cov

# 并行测试
pytest -n auto
```

**覆盖率要求：** >= 55%

---

## 八、部署提示

### 开发环境
```bash
DJANGO_DEBUG=True
python manage.py runserver 0.0.0.0:8000
```

### 生产环境（参考）
```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<安全的密钥>

# 使用 Gunicorn
pip install gunicorn
gunicorn learning_log.wsgi:application --bind 0.0.0.0:8000

# 使用 Nginx 反向代理
# 运行 collectstatic
python manage.py collectstatic --noinput
```

---

## 九、给大模型的 Prompt 模板

下次配置环境时，可以直接使用以下 Prompt：

```
请按照以下步骤配置 /home/ubuntu/Code_Practice 项目环境：

1. 确保 uv 已安装（路径：~/.local/bin/uv）
2. 进入项目目录：cd /home/ubuntu/Code_Practice
3. 创建虚拟环境：uv venv --python 3.11 ll_env
4. 激活环境：source ll_env/bin/activate
5. 使用 pyproject.toml 安装依赖（推荐）：
   uv pip install -e . --python ll_env/bin/python --index-url https://mirrors.aliyun.com/pypi/simple/
   
   或手动安装核心依赖：
   uv pip install django django-bootstrap3 matplotlib pillow protobuf==3.20.3 python-dotenv asgiref sqlparse python-dateutil packaging certifi cycler fonttools kiwisolver numpy pyparsing --python ll_env/bin/python --index-url https://mirrors.aliyun.com/pypi/simple/

6. 检查 secret_key.env 文件是否存在且配置正确：
   - DJANGO_SECRET_KEY=django-insecure-^ub$8b*j%fsx_j_py&)wg38sal$*7#vs&lp#n(0&wnye2j4ixa
   - DJANGO_DEBUG=True
   - DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,101.133.145.194,172.24.52.84

7. 创建必要的目录：mkdir -p media/uploads media/charts
8. 运行数据库迁移：python manage.py migrate
9. 启动服务器：python manage.py runserver 0.0.0.0:8000
10. 验证服务：curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/
```

---

*最后更新：2026-04-09*
