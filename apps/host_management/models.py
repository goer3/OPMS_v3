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
# 操作系统表
######################################
class OperatingSystemInfo(models.Model):
    name = models.CharField(verbose_name='系统名称', max_length=30)
    version = models.CharField(verbose_name='系统版本', max_length=10)
    bit = models.PositiveSmallIntegerField(verbose_name='位数', choices=((32, '32位'), (64, '64位')), default=64)
    add_user = models.ForeignKey(UserProfile, related_name='os_add_user', verbose_name='添加人', on_delete=models.CASCADE)
    desc = models.CharField(verbose_name='描述', max_length=200, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='os_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')))

    class Meta:
        verbose_name = '操作系统'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 服务环境表
######################################
class OperatingEnvironmentInfo(models.Model):
    name = models.CharField(verbose_name='环境名称', max_length=30)
    add_user = models.ForeignKey(UserProfile, related_name='env_add_user', verbose_name='添加人', on_delete=models.CASCADE)
    desc = models.CharField(verbose_name='描述', max_length=200, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='env_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')))

    class Meta:
        verbose_name = '服务环境'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 机房表
######################################
class IdcInfo(models.Model):
    name = models.CharField(verbose_name='机房名称', max_length=30)
    address = models.CharField(verbose_name='地址', max_length=100)
    add_user = models.ForeignKey(UserProfile, related_name='idc_add_user', verbose_name='添加人', on_delete=models.CASCADE)
    desc = models.CharField(verbose_name='描述', max_length=200, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='idc_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')))

    class Meta:
        verbose_name = '机房'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 用途表
######################################
class UseInfo(models.Model):
    name = models.CharField(verbose_name='用途', max_length=30)
    add_user = models.ForeignKey(UserProfile, related_name='use_add_user', verbose_name='添加人', on_delete=models.CASCADE)
    desc = models.CharField(verbose_name='描述', max_length=200, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='use_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')))

    class Meta:
        verbose_name = '用途'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 项目表
######################################
class ProjectInfo(models.Model):
    name = models.CharField(verbose_name='项目名称', max_length=30)
    pro_user = models.CharField(verbose_name='开发人员', max_length=30)
    op_user = models.ForeignKey(UserProfile, related_name='pro_op_user', verbose_name='运维人员', on_delete=models.CASCADE)
    run_env = models.CharField(verbose_name='运行环境', max_length=100)
    add_user = models.ForeignKey(UserProfile, related_name='pro_add_user', verbose_name='添加人', on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='pro_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')))

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 主机信息表
######################################
class HostInfo(models.Model):
    in_ip = models.GenericIPAddressField(verbose_name='内外IP')
    out_ip = models.GenericIPAddressField(verbose_name='外外IP', blank=True, null=True)
    system = models.ForeignKey(OperatingSystemInfo, verbose_name='操作系统', on_delete=models.CASCADE)
    hostname = models.CharField(verbose_name='主机名', max_length=30)
    cpu = models.CharField(verbose_name='CPU', max_length=50)
    disk = models.IntegerField(verbose_name='磁盘')
    memory = models.IntegerField(verbose_name='内存')
    network = models.IntegerField(verbose_name='带宽', blank=True, null=True)
    ssh_port = models.IntegerField(verbose_name='远程端口')
    root_ssh = models.BooleanField(verbose_name='是否允许 root 远程', default=True)
    op_env = models.ForeignKey(OperatingEnvironmentInfo, verbose_name='服务环境', on_delete=models.CASCADE)
    use = models.ForeignKey(UseInfo, verbose_name='用途', on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectInfo, verbose_name='项目', on_delete=models.CASCADE)
    idc = models.ForeignKey(IdcInfo, verbose_name='机房', on_delete=models.CASCADE)
    admin_user = models.CharField(verbose_name='管理员用户', max_length=20)
    admin_pass = models.CharField(verbose_name='管理员密码', max_length=50)
    normal_user = models.CharField(verbose_name='普通用户', max_length=20, blank=True, null=True)
    normal_pass = models.CharField(verbose_name='普通用户密码', max_length=50, blank=True, null=True)
    op_user = models.ForeignKey(UserProfile, related_name='host_op_user', verbose_name='负责人', on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='host_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    desc = models.CharField(verbose_name='备注', max_length=200, blank=True, null=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')), default=1)

    class Meta:
        verbose_name = '主机信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.in_ip


######################################
# 服务信息表
######################################
class HostServiceInfo(models.Model):
    host = models.ForeignKey(HostInfo, verbose_name='主机', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='服务名称', max_length=30)
    version = models.CharField(verbose_name='服务版本', max_length=20)
    listen_user = models.CharField(verbose_name='监听用户', max_length=20)
    listen_port = models.CharField(verbose_name='监听端口', max_length=30)
    ins_path = models.CharField(verbose_name='安装路径', max_length=100)
    log_path = models.CharField(verbose_name='日志路径', max_length=100)
    backup_path = models.CharField(verbose_name='备份路径', max_length=100, blank=True, null=True)
    start_cmd = models.CharField(verbose_name='启动命令', max_length=100)
    desc = models.CharField(verbose_name='备注', max_length=200, blank=True, null=True)
    add_user = models.ForeignKey(UserProfile, related_name='se_add_user', verbose_name='添加人', on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='se_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')))

    class Meta:
        verbose_name = '主机服务信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 数据库表
######################################
class DatabaseInfo(models.Model):
    host = models.ForeignKey(HostInfo, verbose_name='主机', related_name='db_host', on_delete=models.CASCADE)
    db_name = models.CharField(verbose_name='数据库名称', max_length=20)
    db_version = models.CharField(verbose_name='数据库版本', max_length=20)
    db_admin_user = models.CharField(verbose_name='数据库管理员', max_length=20)
    db_admin_pass = models.CharField(verbose_name='数据库管理员密码', max_length=50)
    add_user = models.ForeignKey(UserProfile, related_name='db_add_user', verbose_name='添加人', on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='db_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    desc = models.CharField(verbose_name='备注', max_length=200, blank=True, null=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')), default=1)

    class Meta:
        verbose_name = '数据库信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.host.in_ip


######################################
# 数据库库表
######################################
class DatabaseDBInfo(models.Model):
    db = models.ForeignKey(DatabaseInfo, verbose_name='数据库', related_name='db_db_db', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='库名', max_length=20)
    use = models.CharField(verbose_name='用途', max_length=20)
    desc = models.CharField(verbose_name='备注', max_length=100, blank=True, null=True)
    add_user = models.ForeignKey(UserProfile, related_name='db_db_add_user', verbose_name='添加人',
                                 on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='db_db_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')), default=1)

    class Meta:
        verbose_name = '数据库库表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return ("%s - %s") % (self.db.host.in_ip, self.name)


######################################
# 数据库用户表
######################################
class DatabaseUserInfo(models.Model):
    db = models.ForeignKey(DatabaseInfo, verbose_name='数据库', related_name='user_db', on_delete=models.CASCADE)
    username = models.CharField(verbose_name='用户名', max_length=20)
    password = models.CharField(verbose_name='密码', max_length=50)
    grant_login = models.CharField(verbose_name='授权登录', max_length=50, default='localhost')
    grant_db = models.ManyToManyField(DatabaseDBInfo, verbose_name='授权库')
    add_user = models.ForeignKey(UserProfile, related_name='user_add_user', verbose_name='添加人',
                                 on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='user_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    desc = models.CharField(verbose_name='备注', max_length=200, blank=True, null=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')), default=1)

    def get_grant_list(self):
        grant_list = []
        for each in self.grant_db.all():
            grant_list.append(each.id)
        return grant_list

    class Meta:
        verbose_name = '数据库用户表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return ("%s - %s") % (self.db.host.in_ip, self.username)


######################################
# 网络设备表
######################################
class NetworkDviceInfo(models.Model):
    category = models.CharField(verbose_name='设备分类', max_length=20)
    name = models.CharField(verbose_name='设备型号', max_length=20)
    address = models.CharField(verbose_name='设备地址', max_length=20)
    ip_in = models.GenericIPAddressField(verbose_name='内网 IP')
    ip_out = models.GenericIPAddressField(verbose_name='公网 IP', null=True, blank=True)
    admin_user = models.CharField(verbose_name='管理用户', max_length=20)
    admin_pass = models.CharField(verbose_name='管理密码', max_length=50)
    desc = models.TextField(verbose_name='备注', null=True, blank=True)
    add_user = models.ForeignKey(UserProfile, related_name='net_add_user', verbose_name='添加人',
                                 on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='net_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')), default=1)

    class Meta:
        verbose_name = '网络设备表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return ("%s - %s") % (self.name, self.ip_in)


######################################
# 端口映射表
######################################
class PortToPortInfo(models.Model):
    ip_out = models.GenericIPAddressField(verbose_name='公网 IP', null=True, blank=True)
    port_out = models.IntegerField(verbose_name='外网端口')
    ip_in = models.GenericIPAddressField(verbose_name='内网 IP')
    port_in = models.IntegerField(verbose_name='内网端口')
    use = models.CharField(verbose_name='用途', max_length=20)
    desc = models.TextField(verbose_name='备注', null=True, blank=True)
    add_user = models.ForeignKey(UserProfile, related_name='port_add_user', verbose_name='添加人',
                                 on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='port_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')), default=1)

    class Meta:
        verbose_name = '端口映射表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return ("%s - %s") % (self.ip_in, self.port_in)


######################################
# 域名表
######################################
class DomainNameInfo(models.Model):
    name = models.CharField(verbose_name='名称', max_length=50)
    desc = models.TextField(verbose_name='备注', null=True, blank=True)
    add_user = models.ForeignKey(UserProfile, related_name='dom_add_user', verbose_name='添加人',
                                 on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='dom_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')), default=1)

    class Meta:
        verbose_name = '域名表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


######################################
# 域名解析表
######################################
class DomainNameResolveInfo(models.Model):
    name = models.CharField(verbose_name='二级域名', max_length=20)
    domain_name = models.ForeignKey(DomainNameInfo, verbose_name='域名', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(verbose_name='IP地址')
    desc = models.TextField(verbose_name='备注', null=True, blank=True)
    add_user = models.ForeignKey(UserProfile, related_name='dom_res_add_user', verbose_name='添加人',
                                 on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_user = models.ForeignKey(UserProfile, related_name='dom_res_update_user', verbose_name='修改人',
                                    on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=((1, '正常'), (0, '停用')), default=1)

    class Meta:
        verbose_name = '域名解析表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s.%s' % (self.name, self.domain_name)





