from django.db import models

# Create your models here.

class Chart(models.Model):
    """数据可视化图表"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)  # 图表类别：温度、随机漫步等
    image_path = models.CharField(max_length=500)  # 图表图片路径
    date_added = models.DateTimeField(auto_now_add=True)
    data_file = models.CharField(max_length=500, blank=True)  # 数据文件路径
    script_file = models.CharField(max_length=500)  # 生成图表的脚本文件路径

    def __str__(self):
        """返回模型的字符串表示"""
        return self.title[:50] + "..." if len(self.title) > 50 else self.title
