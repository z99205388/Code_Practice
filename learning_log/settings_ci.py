"""
CI 环境专用 Django 设置

用于 GitHub Actions 等 CI 环境，覆盖生产环境的安全限制。
"""

from .settings import *

# CI 环境配置
DEBUG = True
SECRET_KEY = "ci-test-secret-key-not-for-production-use"

# 关闭生产环境安全设置
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
X_FRAME_OPTIONS = "SAMEORIGIN"

# 简化密码验证（仅测试环境）
AUTH_PASSWORD_VALIDATORS = []

# 测试数据库（使用内存数据库加速）
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# 日志级别
LOGGING["loggers"]["django"]["level"] = "WARNING"
