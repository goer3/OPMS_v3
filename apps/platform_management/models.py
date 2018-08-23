######################################
# Django 模块
######################################
from django.db import models
from django.db.models import Q

######################################
# 系统模块
######################################
import datetime

######################################
# 自定义模块
######################################
from users.models import UserProfile


######################################
# 平台表
######################################
class PlatformInfo(models.Model):
    name = models.CharField(verbose_name='平台名称', max_length=30)
    logo = models.CharField(verbose_name='logo', max_length=100, blank=True, null=True)
    url = models.CharField(verbose_name='url', max_length=200)
    belong = models.PositiveSmallIntegerField(verbose_name='隶属', choices=((1, '公司平台'), (2, '运维平台'), (3, '其它平台')))
    is_public = models.BooleanField(verbose_name='公开', default=True)
    add_user = models.ForeignKey(UserProfile, verbose_name='添加人', related_name='pl_user', on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name = '平台表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 平台用户表
######################################
class PlatformUserInfo(models.Model):
    platform = models.ForeignKey(PlatformInfo, verbose_name='平台', related_name='pu_plat', on_delete=models.CASCADE)
    username = models.CharField(verbose_name='平台名称', max_length=30, blank=True, null=True)
    password = models.CharField(verbose_name='平台密码', max_length=50, blank=True, null=True)
    user = models.ForeignKey(UserProfile, verbose_name='用户', related_name='pu_user', on_delete=models.CASCADE)
    update_user = models.ForeignKey(UserProfile, related_name='platform_update_user', verbose_name='修改人',on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        verbose_name = '平台用户表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.platform.name, self.username)





