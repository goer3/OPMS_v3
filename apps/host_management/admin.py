######################################
# Django 模块
######################################
from django.contrib import admin

######################################
# 自己写的模块
######################################
from .models import *



######################################
# 注册
######################################
admin.site.register(OperatingSystemInfo)
admin.site.register(OperatingEnvironmentInfo)
admin.site.register(IdcInfo)
admin.site.register(UseInfo)
admin.site.register(ProjectInfo)
admin.site.register(HostInfo)
admin.site.register(HostServiceInfo)
admin.site.register(DatabaseInfo)
admin.site.register(DatabaseDBInfo)
admin.site.register(DatabaseUserInfo)
admin.site.register(NetworkDviceInfo)
admin.site.register(PortToPortInfo)
admin.site.register(DomainNameInfo)
admin.site.register(DomainNameResolveInfo)


















