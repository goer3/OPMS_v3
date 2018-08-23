"""
message app
"""
from django.urls import path, re_path
from .views import *


app_name = 'message'

urlpatterns = [
    # 消息列表
    path('list/<str:web_tag>', MessageListView.as_view(), name='message_list'),

    # 消息详情
    path('detail/<str:web_tag>/<int:msg_id>', MessageDetailView.as_view(), name='message_detail'),

    # 发送消息
    path('send', SendMessageView.as_view(), name='message_send'),

    # 回复消息
    path('replay', ReplayMessageView.as_view(), name='message_replay'),

    # 上传图片消息
    path('image/upload', UploadMessagImageView.as_view(), name='message_img_upload'),

    # 星标消息
    path('star', StarMessageView.as_view(), name='message_star'),

    # 添加已读
    path('add/read', AddMessageReadView.as_view(), name='message_add_read'),

    # 添加所有已读
    path('add/all/read', AddAllMessageReadView.as_view(), name='message_add_all_read'),
]


