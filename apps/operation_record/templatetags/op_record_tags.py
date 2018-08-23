from ..models import *
from django import template

register = template.Library()

# 获取最新记录
@register.simple_tag
def Cet_Latest_Record(num=25):
    return UserOperationRecord.objects.all().order_by('-add_time')[:num]

