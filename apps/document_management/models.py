######################################
# Django 模块
######################################
from django.db import models

######################################
# 系统模块
######################################
import datetime

######################################
# 自定义模块
######################################
from users.models import UserProfile


######################################
# 分类表
######################################
class DocumentTags(models.Model):
    name = models.CharField(verbose_name='分类名称', max_length=30)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '分类表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 文档表
######################################
class Document(models.Model):
    subject = models.CharField(verbose_name='标题', max_length=50)
    tags = models.ManyToManyField(DocumentTags, verbose_name='分类标签')
    content = models.TextField(verbose_name='内容')
    belong = models.PositiveSmallIntegerField(verbose_name='隶属', choices=((1, '文档'), (2, 'Shell脚本'), (3, 'Python脚本'), (4, 'Bat脚本'), (5, 'Bat脚本')))
    add_user = models.ForeignKey(UserProfile, related_name='doc_add_user', verbose_name='添加人', on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='doc_update_user', verbose_name='修改人', on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')))

    class Meta:
        verbose_name = '文档表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.subject



























