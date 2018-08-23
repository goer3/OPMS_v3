from django.db import models
from users.models import UserProfile


######################################
# 用户操作表
######################################
class UserOperationRecord(models.Model):
    op_user = models.ForeignKey(UserProfile, verbose_name='操作用户', related_name='host_op_record_user', on_delete=models.CASCADE)
    belong = models.PositiveSmallIntegerField(verbose_name='归属', choices=((1, '主机管理'), (2, '用户管理'), (3, '用户认证'), (4, '文档管理')))
    operation = models.PositiveSmallIntegerField(verbose_name='操作', choices=((1, '添加'), (2, '修改'), (3, '启用'), (4, '停用'), (5, '登录'), (6, '退出')))
    op_num = models.IntegerField(verbose_name='被操作项目ID')
    action = models.CharField(verbose_name='操作详情', max_length=100)
    status = models.PositiveSmallIntegerField(verbose_name='公开程度', choices=((1, '公开'), (2, '不公开')))
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户操作表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return ("%s - %s") % (self.op_user.username, self.action)


