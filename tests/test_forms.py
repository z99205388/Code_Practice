"""
表单测试
"""

from learning_logs.forms import EntryForm, TopicForm


class TestTopicForm:
    """TopicForm 表单测试"""

    def test_topic_form_valid(self):
        """测试有效主题表单"""
        data = {"text": "Python 学习笔记"}
        form = TopicForm(data=data)
        assert form.is_valid()

    def test_topic_form_empty_text(self):
        """测试空文本主题表单无效"""
        data = {"text": ""}
        form = TopicForm(data=data)
        assert not form.is_valid()
        assert "text" in form.errors

    def test_topic_form_fields(self):
        """测试主题表单字段"""
        form = TopicForm()
        assert "text" in form.fields
        assert list(form.Meta.fields) == ["text"]

    def test_topic_form_labels(self):
        """测试主题表单标签"""
        form = TopicForm()
        assert form.fields["text"].label == ""


class TestEntryForm:
    """EntryForm 表单测试"""

    def test_entry_form_valid(self):
        """测试有效条目表单"""
        data = {"text": "今天学习了 Django 测试"}
        form = EntryForm(data=data)
        assert form.is_valid()

    def test_entry_form_empty_text(self):
        """测试空文本条目表单无效"""
        data = {"text": ""}
        form = EntryForm(data=data)
        assert not form.is_valid()
        assert "text" in form.errors

    def test_entry_form_fields(self):
        """测试条目表单字段"""
        form = EntryForm()
        assert "text" in form.fields
        assert list(form.Meta.fields) == ["text"]

    def test_entry_form_labels(self):
        """测试条目表单标签"""
        form = EntryForm()
        assert form.fields["text"].label == ""

    def test_entry_form_widget(self):
        """测试条目表单使用 Textarea 小部件"""
        form = EntryForm()
        from django import forms

        assert isinstance(form.fields["text"].widget, forms.Textarea)

    def test_entry_form_widget_cols(self):
        """测试条目表单 Textarea 列数"""
        form = EntryForm()
        assert form.fields["text"].widget.attrs.get("cols") == 80
