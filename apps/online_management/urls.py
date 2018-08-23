"""
Online management app
"""
from django.urls import path
from online_management.views import *

app_name = 'online_management'

urlpatterns = [
    # 故障列表
    path('trouble/list', TroubleListView.as_view(), name='tr_list'),

    # 添加故障
    path('trouble/add', AddTroubleRecordView.as_view(), name='add_tr'),

    # 修改故障
    path('trouble/edit', EditTroubleRecordView.as_view(), name='edit_tr'),

    # 删除故障
    path('trouble/delete', DeleteTroubleRecordView.as_view(), name='del_tr'),

    # 添加故障
    path('tag/add', AddTroubleTagView.as_view(), name='add_tr_tag'),

    # 发布列表
    path('deploy/list', DeployListView.as_view(), name='dep_list'),

    # 添加发布
    path('deploy/add', AddDeployRecordView.as_view(), name='add_dep'),

    # 修改发布
    path('deploy/edit', EditDeployRecordView.as_view(), name='edit_dep'),

    # 删除发布
    path('deploy/delete', DeleteDeployRecordView.as_view(), name='del_dep'),

    # 运维事件列表
    path('opevent/list', OpEventListView.as_view(), name='opevent_list'),

    # 添加运维事件
    path('opevent/add', AddOpEventView.as_view(), name='add_opevent'),

    # 修改运维事件
    path('opevent/edit', EditOpEventView.as_view(), name='edit_opevent'),

    # 删除运维事件
    path('opevent/delete', DeleteOpEventView.as_view(), name='del_opevent'),
]


