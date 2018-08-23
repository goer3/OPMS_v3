from ..models import *
from django import template

register = template.Library()

# 获取未读信息
@register.filter
def Get_UnreadMsg_Nums(uid):
    return MessageUserInfo.objects.filter(user_id=int(uid)).filter(status=1).filter(is_read=False).count()


# 获取 5 条未读消息
@register.filter
def Get_Unread_Messages(uid):
    return MessageUserInfo.objects.filter(user_id=int(uid), is_read=False)[:5]


# 获取回复数量
@register.filter
def Get_Replay_Nums(msg_id):
    return MessageReplayInfo.objects.filter(message_id=int(msg_id)).count()


# 获取最近一年
@register.simple_tag
def Get_Latest_Year():
    n = 0
    year_list = []
    month_list = []
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month
    new_year = year_now
    new_month = month_now

    while n < 6:
        n += 1
        year_list.append(new_year)
        month_list.append(new_month)
        if (month_now - n) > 0:
            new_month = (month_now - n)

        if (month_now - n) == 0:
            new_year = (year_now - 1)
            new_month = 12

        if (month_now - n) < 0:
            new_month = (12 + (month_now - n))

        year_list = list(reversed(year_list))
        month_list = list(reversed(month_list))
        y_m_ziped = zip(year_list, month_list)

    return reversed(sorted(y_m_ziped))


# 获取年月数量
@register.simple_tag
def Get_Archives_Nums(uid, year, month):
    return MessageUserInfo.objects.filter(user_id=uid, message__add_time__year=year, message__add_time__month=month).count()


# 获取年月数量
@register.simple_tag
def Get_YM_Str(year, month):
    return (str(year) + str(month))


# 获取消息数量
@register.filter
def Get_Message_Nums(uid):
    return MessageUserInfo.objects.filter(user_id=int(uid)).count()











