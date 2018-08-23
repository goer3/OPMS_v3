from ..models import *
from django import template

register = template.Library()

# 获取主机数量
@register.simple_tag
def Get_Host_Nums():
    return HostInfo.objects.filter(status=1).count()
