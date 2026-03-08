"""
pytest 共享 fixtures 配置
"""

import pytest
from django.contrib.auth.models import User

from learning_logs.models import Entry, Topic


@pytest.fixture
def user(db):
    """创建测试用户"""
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def another_user(db):
    """创建另一个测试用户（用于权限隔离测试）"""
    return User.objects.create_user(username="anotheruser", password="anotherpass123")


@pytest.fixture
def authenticated_client(client, user):
    """已认证的测试客户端"""
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture
def another_authenticated_client(client, another_user):
    """另一个用户的已认证客户端"""
    client.login(username="anotheruser", password="anotherpass123")
    return client


@pytest.fixture
def topic(user):
    """创建测试主题"""
    return Topic.objects.create(text="测试主题", owner=user)


@pytest.fixture
def another_topic(another_user):
    """创建另一个用户的主题"""
    return Topic.objects.create(text="其他用户的主题", owner=another_user)


@pytest.fixture
def entry(topic):
    """创建测试条目"""
    return Entry.objects.create(topic=topic, text="测试条目内容")


@pytest.fixture
def long_text_topic(user):
    """创建长文本主题（用于测试 __str__ 截断）"""
    return Topic.objects.create(text="A" * 100, owner=user)


@pytest.fixture
def long_text_entry(topic):
    """创建长文本条目（用于测试 __str__ 截断）"""
    return Entry.objects.create(topic=topic, text="B" * 100)
