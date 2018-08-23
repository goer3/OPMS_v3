from ..models import *
from django import template

register = template.Library()

# 获取最新文档
@register.simple_tag
def Get_Latest_Doc(num=5):
    return Document.objects.filter(status=1).order_by('-update_time')[:num]


# 获取文档数量
@register.simple_tag
def Get_Doc_Nums():
    return Document.objects.filter(status=1).count()

@register.filter
def Get_Tag_Nums(tag_id):
    tag_id = int(tag_id)
    return Document.objects.filter(tags=tag_id, status=1).distinct().count()