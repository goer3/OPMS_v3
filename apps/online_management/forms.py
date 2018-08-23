######################################
# Django 模块
######################################
from django import forms


######################################
# 自定义模块
######################################
from .models import *


######################################
# 添加故障记录
######################################
class AddTroubleRecordForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    event = forms.CharField(max_length=50, required=True)
    event_time = forms.DateTimeField()
    handle_way = forms.CharField(max_length=100, required=True)
    handle_time = forms.DateTimeField()


######################################
# 添加发布记录
######################################
class AddDeployRecordForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    request_user = forms.CharField(max_length=50, required=True)
    deploy_time = forms.DateTimeField()


######################################
# 添加运维事件
######################################
class AddOpEventForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    start_time = forms.DateTimeField()
