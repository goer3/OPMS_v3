######################################
# Django 模块
######################################
from django import forms
from captcha.fields import CaptchaField

######################################
# 自定义模块
######################################
from .models import *


######################################
# 用户登录表单
######################################
class UerLoginForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=4, required=True)
    password = forms.CharField(max_length=20, min_length=6, required=True)
    captcha = CaptchaField(error_messages={'invalid': '验证码错误!'})


######################################
# 用户忘记密码表单
######################################
class UserForgetPasswordForm(forms.Form):
    email = forms.EmailField(required=True)


######################################
# 修改用户信息表单
######################################
class ChangeUserInfoForm(forms.Form):
    english_name = forms.CharField(max_length=20, required=False)
    mobile = forms.CharField(max_length=15, required=False)
    wechat = forms.CharField(max_length=20, required=False)
    qq = forms.CharField(max_length=15, required=False)
    address = forms.CharField(max_length=50, required=False)
    desc = forms.Textarea()


######################################
# 修改用户密码表单
######################################
class ChangeUserPasswordForm(forms.Form):
    cur_password = forms.CharField(min_length=6, max_length=20, required=True)
    new_password = forms.CharField(min_length=6, max_length=20, required=True)
    renew_password = forms.CharField(min_length=6, max_length=20, required=True)


######################################
# 添加用户表单
######################################
class AddUserForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=20, required=True)
    chinese_name = forms.CharField(max_length=20, required=True)
    email = forms.EmailField()
    mobile = forms.CharField(min_length=6, max_length=20, required=True)
    password = forms.CharField(min_length=6, max_length=20, required=True)
    re_password = forms.CharField(min_length=6, max_length=20, required=True)


######################################
# 修改用户表单
######################################
class EditUserForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=20, required=True)
    chinese_name = forms.CharField(max_length=20, required=True)
    email = forms.EmailField()
    mobile = forms.CharField(min_length=6, max_length=20, required=True)









