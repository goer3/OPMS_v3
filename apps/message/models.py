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
# 消息表
######################################
class MessageInfo(models.Model):
    send_user = models.ForeignKey(UserProfile, verbose_name='发送者', related_name='ms_send_user', on_delete=models.CASCADE)
    ms_type = models.PositiveSmallIntegerField(choices=((1, '系统消息'), (2, '私信'), (3, '群发')))
    subject = models.CharField(max_length=100, verbose_name='标题', default='无标题')
    content = models.TextField(verbose_name='内容')
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        verbose_name = '消息表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.send_user.chinese_name, self.subject)


######################################
# 回复消息表
######################################
class MessageReplayInfo(models.Model):
    message = models.ForeignKey(MessageInfo, verbose_name='消息', related_name='msrep_message', on_delete=models.CASCADE)
    replay_user = models.ForeignKey(UserProfile, verbose_name='回复者', related_name='msrep_send_user', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='内容')
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '回复消息表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.message.id, self.replay_user.chinese_name)


######################################
# 用户接受消息表
######################################
class MessageUserInfo(models.Model):
    message = models.ForeignKey(MessageInfo, verbose_name='消息', related_name='msu_message', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, verbose_name='用户', related_name='msu_user', on_delete=models.CASCADE)
    is_star = models.BooleanField(default=False, verbose_name='星标')
    is_read = models.BooleanField(default=False, verbose_name='读取')
    status = models.PositiveSmallIntegerField(choices=((1, '保留'), (2, '删除'), (3, '永久删除')), default=1)

    class Meta:
        verbose_name = '用户接受消息表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.message.id, self.user.chinese_name)








