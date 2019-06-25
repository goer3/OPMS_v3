from ..models import *
from django import template

register = template.Library()

# 获取平台信息
@register.simple_tag
def Get_PlatForm_Info(uid, pid):
    return PlatformUserInfo.objects.filter(platform_id=int(pid)).filter( user_id=int(uid))


# 获取公共平台信息
@register.simple_tag
def Get_Common_PlatForm_Info(pid):
    return PlatformUserInfo.objects.filter(platform_id=int(pid))
