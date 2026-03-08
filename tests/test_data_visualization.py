"""
数据可视化模块测试
"""

from django.urls import reverse

from data_visualization.models import Chart


class TestChartModel:
    """Chart 模型测试"""

    def test_create_chart(self, db):
        """测试创建图表"""
        chart = Chart.objects.create(
            title="测试图表",
            description="这是一个测试图表",
            category="test",
            image_path="/media/charts/test.png",
            script_file="/scripts/test.py",
        )
        assert chart.id is not None
        assert chart.title == "测试图表"
        assert chart.category == "test"

    def test_chart_str(self, db):
        """测试 Chart __str__ 方法"""
        chart = Chart.objects.create(
            title="短标题",
            description="描述",
            category="test",
            image_path="/media/test.png",
            script_file="/scripts/test.py",
        )
        assert str(chart) == "短标题"

    def test_chart_str_truncation(self, db):
        """测试 Chart __str__ 长标题截断"""
        chart = Chart.objects.create(
            title="A" * 100,
            description="描述",
            category="test",
            image_path="/media/test.png",
            script_file="/scripts/test.py",
        )
        result = str(chart)
        assert len(result) == 53  # 50 字符 + "..."
        assert result.endswith("...")

    def test_chart_optional_fields(self, db):
        """测试可选字段"""
        chart = Chart.objects.create(
            title="无数据文件图表",
            description="描述",
            category="test",
            image_path="/media/test.png",
            script_file="/scripts/test.py",
            data_file="",  # 可选字段留空
        )
        assert chart.data_file == ""


class TestDataVisualizationViews:
    """数据可视化视图测试"""

    def test_index_view(self, client, db):
        """测试数据可视化首页"""
        response = client.get(reverse("data_visualization:index"))
        assert response.status_code == 200

    def test_charts_view_requires_login(self, client):
        """测试图表列表视图需要登录"""
        response = client.get(reverse("data_visualization:charts"))
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_charts_view_authenticated(self, authenticated_client, db):
        """测试已登录用户可访问图表列表"""
        response = authenticated_client.get(reverse("data_visualization:charts"))
        assert response.status_code == 200

    def test_chart_detail_view_requires_login(self, client, db):
        """测试图表详情视图需要登录"""
        chart = Chart.objects.create(
            title="测试图表",
            description="描述",
            category="test",
            image_path="/media/test.png",
            script_file="/scripts/test.py",
        )
        response = client.get(reverse("data_visualization:chart_detail", args=[chart.id]))
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_chart_detail_view_authenticated(self, authenticated_client, db):
        """测试已登录用户可访问图表详情"""
        chart = Chart.objects.create(
            title="测试图表",
            description="描述",
            category="test",
            image_path="/media/test.png",
            script_file="/scripts/test.py",
        )
        response = authenticated_client.get(reverse("data_visualization:chart_detail", args=[chart.id]))
        assert response.status_code == 200

    def test_process_data_view_requires_login(self, client):
        """测试数据处理视图需要登录"""
        response = client.get(reverse("data_visualization:process_data"))
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_process_data_view_authenticated(self, authenticated_client):
        """测试已登录用户可访问数据处理页面"""
        response = authenticated_client.get(reverse("data_visualization:process_data"))
        assert response.status_code == 200


class TestDataVisualizationURLs:
    """数据可视化 URL 测试"""

    def test_index_url_reverse(self):
        """测试 index URL 反向解析"""
        url = reverse("data_visualization:index")
        assert url == "/data_visualization/"

    def test_charts_url_reverse(self):
        """测试 charts URL 反向解析"""
        url = reverse("data_visualization:charts")
        assert url == "/data_visualization/charts/"

    def test_chart_detail_url_reverse(self):
        """测试 chart_detail URL 反向解析"""
        url = reverse("data_visualization:chart_detail", args=[1])
        assert url == "/data_visualization/charts/1/"

    def test_process_data_url_reverse(self):
        """测试 process_data URL 反向解析"""
        url = reverse("data_visualization:process_data")
        assert url == "/data_visualization/process/"
