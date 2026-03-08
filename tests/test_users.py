"""
用户认证视图测试
"""

from django.contrib.auth.models import User
from django.urls import reverse


class TestLoginView:
    """登录视图测试"""

    def test_login_page_accessible(self, client):
        """测试登录页面可访问"""
        response = client.get(reverse("users:login"))
        assert response.status_code == 200

    def test_login_success(self, client, user):
        """测试成功登录"""
        response = client.post(
            reverse("users:login"),
            {
                "username": "testuser",
                "password": "testpass123",
            },
        )
        assert response.status_code == 302  # 重定向到首页


class TestLogoutView:
    """登出视图测试"""

    def test_logout_redirect(self, authenticated_client):
        """测试登出后重定向"""
        response = authenticated_client.get(reverse("users:logout"))
        assert response.status_code == 302
        # 登出后重定向到学习日志首页
        assert "/learning_logs/" in response.url


class TestRegisterView:
    """注册视图测试"""

    def test_register_page_accessible(self, client):
        """测试注册页面可访问"""
        response = client.get(reverse("users:register"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_register_success(self, client, db):
        """测试成功注册"""
        data = {
            "username": "newuser",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        response = client.post(reverse("users:register"), data)
        assert response.status_code == 302  # 注册后重定向
        assert User.objects.filter(username="newuser").exists()

    def test_register_password_mismatch(self, client, db):
        """测试密码不匹配注册失败"""
        data = {
            "username": "newuser",
            "password1": "password123",
            "password2": "differentpassword",
        }
        response = client.post(reverse("users:register"), data)
        assert response.status_code == 200  # 返回表单显示错误
        assert not User.objects.filter(username="newuser").exists()

    def test_register_duplicate_username(self, client, user):
        """测试重复用户名注册失败"""
        data = {
            "username": "testuser",  # 已存在的用户名
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        response = client.post(reverse("users:register"), data)
        assert response.status_code == 200  # 返回表单显示错误
