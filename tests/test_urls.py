"""
URL 路由测试
"""

from django.urls import resolve, reverse

from learning_logs.views import edit_entry, index, new_entry, new_topic, topic, topics
from users.views import logout_view, register


class TestLearningLogsURLs:
    """learning_logs 应用 URL 测试"""

    def test_index_url_reverse(self):
        """测试 index URL 反向解析"""
        url = reverse("learning_logs:index")
        assert url == "/learning_logs/"

    def test_index_url_resolve(self):
        """测试 index URL 解析到正确视图"""
        view = resolve("/learning_logs/")
        assert view.func == index

    def test_topics_url_reverse(self):
        """测试 topics URL 反向解析"""
        url = reverse("learning_logs:topics")
        assert url == "/learning_logs/topics/"

    def test_topics_url_resolve(self):
        """测试 topics URL 解析到正确视图"""
        view = resolve("/learning_logs/topics/")
        assert view.func == topics

    def test_topic_detail_url_reverse(self):
        """测试 topic detail URL 反向解析"""
        url = reverse("learning_logs:topic", args=[1])
        assert url == "/learning_logs/topics/1/"

    def test_topic_detail_url_resolve(self):
        """测试 topic detail URL 解析到正确视图"""
        view = resolve("/learning_logs/topics/1/")
        assert view.func == topic
        assert view.kwargs["topic_id"] == 1

    def test_new_topic_url_reverse(self):
        """测试 new_topic URL 反向解析"""
        url = reverse("learning_logs:new_topic")
        assert url == "/learning_logs/new_topic/"

    def test_new_topic_url_resolve(self):
        """测试 new_topic URL 解析到正确视图"""
        view = resolve("/learning_logs/new_topic/")
        assert view.func == new_topic

    def test_new_entry_url_reverse(self):
        """测试 new_entry URL 反向解析"""
        url = reverse("learning_logs:new_entry", args=[5])
        assert url == "/learning_logs/new_entry/5"

    def test_new_entry_url_resolve(self):
        """测试 new_entry URL 解析到正确视图"""
        view = resolve("/learning_logs/new_entry/5")
        assert view.func == new_entry
        assert view.kwargs["topic_id"] == 5

    def test_edit_entry_url_reverse(self):
        """测试 edit_entry URL 反向解析"""
        url = reverse("learning_logs:edit_entry", args=[10])
        assert url == "/learning_logs/edit_entry/10"

    def test_edit_entry_url_resolve(self):
        """测试 edit_entry URL 解析到正确视图"""
        view = resolve("/learning_logs/edit_entry/10")
        assert view.func == edit_entry
        assert view.kwargs["entry_id"] == 10


class TestUsersURLs:
    """users 应用 URL 测试"""

    def test_login_url_reverse(self):
        """测试 login URL 反向解析"""
        url = reverse("users:login")
        assert url == "/users/login/"

    def test_logout_url_reverse(self):
        """测试 logout URL 反向解析"""
        url = reverse("users:logout")
        assert url == "/users/logout/"

    def test_logout_url_resolve(self):
        """测试 logout URL 解析到正确视图"""
        view = resolve("/users/logout/")
        assert view.func == logout_view

    def test_register_url_reverse(self):
        """测试 register URL 反向解析"""
        url = reverse("users:register")
        assert url == "/users/register/"

    def test_register_url_resolve(self):
        """测试 register URL 解析到正确视图"""
        view = resolve("/users/register/")
        assert view.func == register


class TestRootURLs:
    """根 URL 测试"""

    def test_admin_url_reverse(self):
        """测试 admin URL 反向解析"""
        url = reverse("admin:index")
        assert url == "/admin/"

    def test_root_redirect(self, client):
        """测试根 URL 重定向到学习日志首页"""
        response = client.get("/")
        assert response.status_code == 302
        assert "/learning_logs/" in response.url
