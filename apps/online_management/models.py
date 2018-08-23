from django.db import models
from users.models import UserProfile
from host_management.models import DomainNameResolveInfo, ProjectInfo


######################################
# 故障标签表
######################################
class TroubleTag(models.Model):
    name = models.CharField(verbose_name='分类名称', max_length=20)

    class Meta:
        verbose_name = '故障标签表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

######################################
# 故障表
######################################
class TroubleRecord(models.Model):
    name = models.CharField(verbose_name='平台名称', max_length=20)
    url = models.ForeignKey(DomainNameResolveInfo, verbose_name='域名', related_name='tr_url', blank=True, null=True, on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectInfo, verbose_name='项目', related_name='tr_project', on_delete=models.CASCADE)
    event = models.CharField(verbose_name='事件和原因', max_length=50)
    tags = models.ManyToManyField(TroubleTag, verbose_name='标签')
    event_time = models.DateTimeField(verbose_name='故障时间')
    handle_user = models.ManyToManyField(UserProfile, verbose_name='处理人')
    handle_way = models.CharField(verbose_name='处理办法', max_length=100)
    handle_time = models.DateTimeField(verbose_name='处理时间')
    handle_result = models.PositiveSmallIntegerField(verbose_name='处理结果', choices=((1, '已处理'), (2, '未处理'), (3, '其它')), default=1)
    desc = models.CharField(verbose_name='备注', max_length=100, blank=True, null=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((0, '关闭'), (1, '开启')), default=1)

    class Meta:
        verbose_name = '故障表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.event


######################################
# 上线表
######################################
class DeployRecord(models.Model):
    name = models.CharField(verbose_name='平台名称', max_length=20)
    url = models.ForeignKey(DomainNameResolveInfo, verbose_name='域名', related_name='dep_url', blank=True, null=True, on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectInfo, verbose_name='项目', related_name='dep_project', on_delete=models.CASCADE)
    deploy_time = models.DateTimeField(verbose_name='上线时间')
    request_user = models.CharField(verbose_name='发起人', max_length=20)
    deploy_user = models.ForeignKey(UserProfile, verbose_name='处理人', related_name='dep_user', on_delete=models.CASCADE)
    deploy_result = models.PositiveSmallIntegerField(verbose_name='上线结果', choices=((1, '成功'), (2, '失败')), default=1)
    desc = models.CharField(verbose_name='备注', max_length=100, blank=True, null=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((0, '关闭'), (1, '开启')), default=1)

    class Meta:
        verbose_name = '上线表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 运维事件表
######################################
class OpsEvent(models.Model):
    name = models.CharField(verbose_name='事件名称', max_length=100)
    start_time = models.DateTimeField(verbose_name='开始时间')
    stop_time = models.DateTimeField(verbose_name='结束时间', blank=True, null=True)
    op_user = models.ManyToManyField(UserProfile, verbose_name='处理人')
    desc = models.CharField(verbose_name='备注', max_length=100, blank=True, null=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((0, '关闭'), (1, '开启')), default=1)

    class Meta:
        verbose_name = '运维事件表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


