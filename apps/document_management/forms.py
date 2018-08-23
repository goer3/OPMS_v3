######################################
# Django 模块
######################################
from django import forms


######################################
# 自定义模块
######################################
from .models import *


######################################
# 添加文章表单
######################################
class AddDocumentForm(forms.Form):
    subject = forms.CharField(min_length=2, max_length=50, required=True)
    content = forms.Textarea()


