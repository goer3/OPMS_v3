######################################
# Django 模块
######################################
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q


######################################
# 系统模块
######################################
import datetime


######################################
# 公司表
######################################
class UserCompany(models.Model):
    name = models.CharField(verbose_name='公司名称', max_length=30)
    leader = models.CharField(verbose_name='管理', max_length=10)
    desc = models.CharField(verbose_name='描述', max_length=200, blank=True, null=True)
    address = models.CharField(verbose_name='地址', max_length=50, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '公司'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 部门表
######################################
class UserDepartment(models.Model):
    name = models.CharField(verbose_name='部门名称', max_length=20)
    company = models.ForeignKey(UserCompany, verbose_name='公司', on_delete=models.CASCADE)
    leader = models.CharField(verbose_name='主管', max_length=10)
    desc = models.CharField(verbose_name='描述', max_length=200, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s - %s" % (self.company.name, self.name)


######################################
# 职位表
######################################
class UserPosition(models.Model):
    name = models.CharField(verbose_name='名称', max_length=20)
    department = models.ForeignKey(UserDepartment, verbose_name='部门', on_delete=models.CASCADE)
    desc = models.CharField(verbose_name='描述', max_length=200, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '职位'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s - %s - %s" % (self.department.company.name, self.department.name, self.name)


######################################
# 用户扩展表
######################################
class UserProfile(AbstractUser):
    role = models.PositiveSmallIntegerField(verbose_name='角色', choices=((1, '普通用户'), (2, '管理员'), (3, '超级管理员')), default=1)
    chinese_name = models.CharField(verbose_name='中文名', max_length=10)
    english_name = models.CharField(verbose_name='英文名', max_length=20, blank=True, null=True)
    wechat = models.CharField(verbose_name='微信', max_length=30, blank=True, null=True)
    qq = models.CharField(verbose_name='QQ', max_length=20, blank=True, null=True)
    mobile = models.CharField(verbose_name='手机号', max_length=20)
    avatar = models.ImageField(verbose_name='用户头像', max_length=200, upload_to='users/avatar/%Y/%m',
                               default='users/avatar/default.png', null=True, blank=True)
    birthday = models.DateField(verbose_name='生日', blank=True, null=True)
    gender = models.CharField(verbose_name='性别', choices=(('male', '男'), ('female', '女')), default='male',
                              max_length=10)
    address = models.CharField(verbose_name='地址', max_length=50, blank=True, null=True)
    position = models.ForeignKey(UserPosition, verbose_name='职位', on_delete=models.CASCADE, blank=True, null=True)
    desc = models.CharField(verbose_name='描述', max_length=200, blank=True, null=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (2, '停用')), default=1)
    stop_time = models.DateTimeField(verbose_name='停用时间', blank=True, null=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    # 获取账户添加时间
    def get_join_days(self):
        join_days = ((datetime.datetime.now() - self.date_joined).days + 1)
        return join_days


######################################
# 邮箱验证码表
######################################
class UserEmailVirificationCode(models.Model):
    code = models.CharField(verbose_name='验证码', max_length=20)
    email = models.EmailField(verbose_name='接收邮箱')
    purpose = models.CharField(verbose_name='用途', choices=(
    ('register', '注册'), ('forget', '忘记密码'), ('change_email', '修改邮箱绑定'), ('active', '用户激活')), max_length=20)
    is_use = models.BooleanField(verbose_name='是否被使用', default=False)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '邮箱验证码'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.email


######################################
# 用户登录信息表
######################################
class UserLoginInfo(models.Model):
    action = models.PositiveSmallIntegerField(verbose_name='动作', choices=((1, '登录'), (2, '注销')), default=1)
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    agent = models.CharField(verbose_name='客户端', max_length=200)
    ip = models.GenericIPAddressField(verbose_name='IP地址')
    address = models.CharField(verbose_name='登录地区', max_length=100)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户登录信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


######################################
# 用户反馈
######################################
class UserAskHelp(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='发送者', related_name='ah_user', on_delete=models.CASCADE)
    subject = models.CharField(verbose_name='标题', max_length=100)
    content = models.TextField(verbose_name='正文')
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户反馈'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username

