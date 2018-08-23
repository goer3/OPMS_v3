from django import template
from ..models import *

register = template.Library()

# 转义
@register.filter
def Change_Str(str_value):
    return str(str_value)


# 获取最新记录
@register.simple_tag
def Get_Latest_Trouble(num=5):
    return TroubleRecord.objects.filter(status=1).order_by("-event_time")[:num]


@register.simple_tag
def Get_Latest_Deploy(num=5):
    return DeployRecord.objects.filter(status=1).order_by("-deploy_time")[:num]


# 获取故障梳理
@register.simple_tag
def Get_Trouble_Nums():
    return TroubleRecord.objects.filter(status=1).count()
