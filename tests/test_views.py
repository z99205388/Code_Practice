"""
视图测试
"""

from django.urls import reverse

from learning_logs.models import Entry, Topic


class TestIndexView:
    """首页视图测试"""

    def test_index_accessible(self, client):
        """测试首页可访问"""
        response = client.get(reverse("learning_logs:index"))
        assert response.status_code == 200
        assert "learning_logs/index.html" in [t.name for t in response.templates]

    def test_index_no_login_required(self, client):
        """测试首页不需要登录"""
        response = client.get(reverse("learning_logs:index"))
        assert response.status_code == 200


class TestTopicsView:
    """主题列表视图测试"""

    def test_topics_requires_login(self, client):
        """测试主题列表需要登录"""
        response = client.get(reverse("learning_logs:topics"))
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_topics_authenticated(self, authenticated_client):
        """测试已登录用户可访问主题列表"""
        response = authenticated_client.get(reverse("learning_logs:topics"))
        assert response.status_code == 200
        assert "learning_logs/topics.html" in [t.name for t in response.templates]

    def test_topics_only_user_topics(self, authenticated_client, user, another_user):
        """测试用户只能看到自己的主题"""
        my_topic = Topic.objects.create(text="我的主题", owner=user)
        other_topic = Topic.objects.create(text="别人的主题", owner=another_user)

        response = authenticated_client.get(reverse("learning_logs:topics"))
        topics = response.context["topics"]

        assert my_topic in topics
        assert other_topic not in topics


class TestTopicDetailView:
    """主题详情视图测试"""

    def test_topic_detail_requires_login(self, client, topic):
        """测试主题详情需要登录"""
        response = client.get(reverse("learning_logs:topic", args=[topic.id]))
        assert response.status_code == 302

    def test_topic_detail_authenticated(self, authenticated_client, topic):
        """测试已登录用户可访问自己的主题详情"""
        response = authenticated_client.get(reverse("learning_logs:topic", args=[topic.id]))
        assert response.status_code == 200
        assert response.context["topic"] == topic

    def test_topic_detail_other_user_forbidden(self, another_authenticated_client, topic):
        """测试用户无法访问别人的主题"""
        response = another_authenticated_client.get(reverse("learning_logs:topic", args=[topic.id]))
        assert response.status_code == 404

    def test_topic_detail_nonexistent(self, authenticated_client):
        """测试访问不存在的主题返回 404"""
        response = authenticated_client.get(reverse("learning_logs:topic", args=[99999]))
        assert response.status_code == 404


class TestNewTopicView:
    """新建主题视图测试"""

    def test_new_topic_requires_login(self, client):
        """测试新建主题需要登录"""
        response = client.get(reverse("learning_logs:new_topic"))
        assert response.status_code == 302

    def test_new_topic_get_form(self, authenticated_client):
        """测试获取新建主题表单"""
        response = authenticated_client.get(reverse("learning_logs:new_topic"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_new_topic_post_success(self, authenticated_client, user):
        """测试成功创建主题"""
        data = {"text": "新学习主题"}
        response = authenticated_client.post(reverse("learning_logs:new_topic"), data)

        assert response.status_code == 302
        assert response.url == reverse("learning_logs:topics")

        topic = Topic.objects.get(text="新学习主题")
        assert topic.owner == user

    def test_new_topic_post_empty(self, authenticated_client):
        """测试提交空主题失败"""
        data = {"text": ""}
        response = authenticated_client.post(reverse("learning_logs:new_topic"), data)
        assert response.status_code == 200  # 返回表单显示错误
        assert not Topic.objects.filter(text="").exists()


class TestNewEntryView:
    """新建条目视图测试"""

    def test_new_entry_requires_login(self, client, topic):
        """测试新建条目需要登录"""
        response = client.get(reverse("learning_logs:new_entry", args=[topic.id]))
        assert response.status_code == 302

    def test_new_entry_get_form(self, authenticated_client, topic):
        """测试获取新建条目表单"""
        response = authenticated_client.get(reverse("learning_logs:new_entry", args=[topic.id]))
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["topic"] == topic

    def test_new_entry_post_success(self, authenticated_client, topic):
        """测试成功创建条目"""
        data = {"text": "新的学习笔记"}
        response = authenticated_client.post(reverse("learning_logs:new_entry", args=[topic.id]), data)

        assert response.status_code == 302
        assert Entry.objects.filter(text="新的学习笔记", topic=topic).exists()

    def test_new_entry_other_user_topic(self, another_authenticated_client, topic):
        """测试无法在别人的主题下添加条目"""
        response = another_authenticated_client.get(reverse("learning_logs:new_entry", args=[topic.id]))
        assert response.status_code == 404

    def test_new_entry_nonexistent_topic(self, authenticated_client):
        """测试在不存在的主题下添加条目返回 404"""
        response = authenticated_client.get(reverse("learning_logs:new_entry", args=[99999]))
        assert response.status_code == 404


class TestEditEntryView:
    """编辑条目视图测试"""

    def test_edit_entry_requires_login(self, client, entry):
        """测试编辑条目需要登录"""
        response = client.get(reverse("learning_logs:edit_entry", args=[entry.id]))
        assert response.status_code == 302

    def test_edit_entry_get_form(self, authenticated_client, entry, topic):
        """测试获取编辑条目表单"""
        response = authenticated_client.get(reverse("learning_logs:edit_entry", args=[entry.id]))
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["entry"] == entry
        assert response.context["topic"] == topic

    def test_edit_entry_post_success(self, authenticated_client, entry):
        """测试成功编辑条目"""
        new_text = "更新后的学习笔记"
        data = {"text": new_text}
        response = authenticated_client.post(reverse("learning_logs:edit_entry", args=[entry.id]), data)

        assert response.status_code == 302
        entry.refresh_from_db()
        assert entry.text == new_text

    def test_edit_entry_other_user_forbidden(self, another_authenticated_client, entry):
        """测试无法编辑别人的条目"""
        response = another_authenticated_client.get(reverse("learning_logs:edit_entry", args=[entry.id]))
        # 应该重定向到 topics 页面（无权限）
        assert response.status_code == 302
        assert "/learning_logs/topics/" in response.url

    def test_edit_entry_nonexistent(self, authenticated_client):
        """测试编辑不存在的条目返回 404"""
        response = authenticated_client.get(reverse("learning_logs:edit_entry", args=[99999]))
        assert response.status_code == 404
