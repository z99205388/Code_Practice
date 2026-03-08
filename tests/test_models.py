"""
模型测试
"""

from learning_logs.models import Entry, Topic


class TestTopicModel:
    """Topic 模型测试"""

    def test_create_topic(self, db, user):
        """测试创建主题"""
        topic = Topic.objects.create(text="Python 学习", owner=user)
        assert topic.id is not None
        assert topic.text == "Python 学习"
        assert topic.owner == user

    def test_topic_str(self, topic):
        """测试 Topic __str__ 方法"""
        assert str(topic) == "测试主题"

    def test_topic_str_truncation(self, long_text_topic):
        """测试 Topic __str__ 长文本截断"""
        result = str(long_text_topic)
        assert len(result) == 53  # 50 字符 + "..."
        assert result.endswith("...")

    def test_topic_str_empty(self, db, user):
        """测试 Topic __str__ 空文本"""
        topic = Topic(text="", owner=user)
        assert str(topic) == "无内容"

    def test_topic_owner_relationship(self, topic, user):
        """测试主题与用户的关联"""
        assert topic.owner == user
        assert topic in user.topic_set.all()

    def test_topic_date_added_auto(self, db, user):
        """测试主题日期自动设置"""
        topic = Topic.objects.create(text="新主题", owner=user)
        assert topic.date_added is not None

    def test_topic_cascade_delete(self, db, user):
        """测试删除用户时级联删除主题"""
        topic = Topic.objects.create(text="待删除主题", owner=user)
        topic_id = topic.id
        user.delete()
        assert not Topic.objects.filter(id=topic_id).exists()


class TestEntryModel:
    """Entry 模型测试"""

    def test_create_entry(self, topic):
        """测试创建条目"""
        entry = Entry.objects.create(topic=topic, text="学习笔记")
        assert entry.id is not None
        assert entry.text == "学习笔记"
        assert entry.topic == topic

    def test_entry_str(self, entry):
        """测试 Entry __str__ 方法"""
        assert str(entry) == "测试条目内容"

    def test_entry_str_truncation(self, long_text_entry):
        """测试 Entry __str__ 长文本截断"""
        result = str(long_text_entry)
        assert len(result) == 53  # 50 字符 + "..."
        assert result.endswith("...")

    def test_entry_str_empty(self, topic):
        """测试 Entry __str__ 空文本"""
        entry = Entry(topic=topic, text="")
        assert str(entry) == "无内容"

    def test_entry_topic_relationship(self, entry, topic):
        """测试条目与主题的关联"""
        assert entry.topic == topic
        assert entry in topic.entry_set.all()

    def test_entry_date_added_auto(self, topic):
        """测试条目日期时间自动设置"""
        entry = Entry.objects.create(topic=topic, text="新条目")
        assert entry.date_added is not None

    def test_entry_cascade_delete_topic(self, topic):
        """测试删除主题时级联删除条目"""
        entry = Entry.objects.create(topic=topic, text="待删除条目")
        entry_id = entry.id
        topic.delete()
        assert not Entry.objects.filter(id=entry_id).exists()

    def test_entry_cascade_delete_user(self, db, user):
        """测试删除用户时级联删除条目（通过主题）"""
        topic = Topic.objects.create(text="主题", owner=user)
        entry = Entry.objects.create(topic=topic, text="条目")
        entry_id = entry.id
        user.delete()
        assert not Entry.objects.filter(id=entry_id).exists()

    def test_multiple_entries_order(self, topic):
        """测试条目按时间倒序排列"""
        import time

        entry1 = Entry.objects.create(topic=topic, text="第一条")
        time.sleep(0.01)  # 确保时间差
        entry2 = Entry.objects.create(topic=topic, text="第二条")

        entries = list(topic.entry_set.order_by("-date_added"))
        assert entries[0] == entry2
        assert entries[1] == entry1
