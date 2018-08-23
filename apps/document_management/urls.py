"""
Document management app
"""
from django.urls import path
from document_management.views import *

app_name = 'document_management'

urlpatterns = [
    # 文档列表
    path('list/<str:doc_cate>', DocumentListView.as_view(), name='doc_list'),

    # 添加文档
    path('add', DocumentAddView.as_view(), name='doc_add'),

    # 文档详情
    path('detail/<int:doc_id>', DocumentDetailView.as_view(), name='doc_detail'),

    # 修改文档
    path('edit', DocumentEditView.as_view(), name='doc_edit'),

    # 删除文档
    path('delete', DocumentDeleteView.as_view(), name='doc_del'),

    # 脚本下载
    path('script/download/<int:doc_id>', DocumentDownloadView.as_view(), name='doc_script_download'),
]
