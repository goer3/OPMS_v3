"""
Host management app
"""
from django.urls import path
from .views import *


app_name = 'platform_management'

urlpatterns = [
    # 内部平台列表
    path('company/list', CompanyPlatformListView.as_view(), name='platform_company_list'),

    # 运维平台列表
    path('ops/list', OpsPlatformListView.as_view(), name='platform_ops_list'),

    # 个人平台列表
    path('other/list', OtherPlatformListView.as_view(), name='platform_other_list'),

    # 添加个人平台
    path('other/add', AddOtherPlatformView.as_view(), name='platform_other_add'),

    # 修改平台用户列表
    path('user/edit', EditPlatformUserView.as_view(), name='platform_user_edit'),
]


