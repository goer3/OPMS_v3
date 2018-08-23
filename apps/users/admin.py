######################################
# Django 模块
######################################
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

######################################
# 自己写的模块
######################################
from .models import *


class UserAdmin(UserAdmin):
    fieldsets = ()


######################################
# 注册
######################################
admin.site.register(UserCompany)
admin.site.register(UserDepartment)
admin.site.register(UserPosition)
admin.site.register(UserProfile, UserAdmin)
admin.site.register(UserEmailVirificationCode)
admin.site.register(UserLoginInfo)