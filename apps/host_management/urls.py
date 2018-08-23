"""
Host management app
"""
from django.urls import path
from host_management.views import *


app_name = 'host_management'

urlpatterns = [
    # 主机列表
    path('list', HostListView.as_view(), name='host_list'),

    # webssh
    path(r'webssh/<int:host_id>', WebSSHView.as_view(), name='web_ssh'),

    # 主机详情
    path('info/<int:host_id>', HostInfoView.as_view(), name='host_info'),

    # 添加主机
    path('info/add', AddHostInfoView.as_view(), name='add_host'),

    # 删除主机
    path('info/delete', DeleteHostView.as_view(), name='del_host'),

    # 修改主机
    path('info/edit', EditHostInfoView.as_view(), name='edit_host'),

    # 添加主机服务
    path('service/add', AddHostServiceView.as_view(), name='add_host_service'),

    # 修改主机服务
    path('service/edit', EditHostServiceView.as_view(), name='edit_host_service'),

    # 删除主机服务
    path('service/delete', DeleteHostServiceView.as_view(), name='del_host_service'),

    # 操作系统列表
    path('os/list', OSListView.as_view(), name='os_List'),

    # 添加系统
    path('os/add', AddOSView.as_view(), name='add_os'),

    # 修改系统
    path('os/edit', EditOSView.as_view(), name='edit_os'),

    # 删除系统
    path('os/delete', DeleteOSView.as_view(), name='del_os'),

    # 机房列表
    path('idc/list', IdcListView.as_view(), name='idc_List'),

    # 添加机房
    path('idc/add', AddIDCView.as_view(), name='add_idc'),

    # 修改机房
    path('idc/edit', EditIDCView.as_view(), name='edit_idc'),

    # 删除机房
    path('idc/delete', DeleteIDCView.as_view(), name='del_idc'),

    # 项目列表
    path('project/list', ProjectListView.as_view(), name='project_List'),

    # 添加机房
    path('project/add', AddProjectView.as_view(), name='add_project'),

    # 修改机房
    path('project/edit', EditProjectView.as_view(), name='edit_project'),

    # 删除机房
    path('project/delete', DeleteProjectView.as_view(), name='del_project'),

    # 环境列表
    path('openv/list', OpEnvListView.as_view(), name='openv_List'),

    # 添加环境
    path('openv/add', AddOpEnvView.as_view(), name='add_openv'),

    # 修改环境
    path('openv/edit', EditOpEnvView.as_view(), name='edit_openv'),

    # 删除环境
    path('openv/delete', DeleteOpEnvView.as_view(), name='del_openv'),

    # 用途列表
    path('use/list', UseListView.as_view(), name='use_List'),

    # 添加用途
    path('use/add', AddUseView.as_view(), name='add_use'),

    # 修改用途
    path('use/edit', EditUseView.as_view(), name='edit_use'),

    # 删除用途
    path('use/delete', DeleteUseView.as_view(), name='del_use'),

    # 数据库列表
    path('database/list', DatabaseListView.as_view(), name='db_list'),

    # 数据库详情
    path('database/info/<int:db_id>', DatabaseInfoView.as_view(), name='db_info'),

    # 添加数据库信息
    path('database/add', AddDatabaseInfoView.as_view(), name='add_db'),

    # 修改数据库信息
    path('database/edit', EditDatabaseInfoView.as_view(), name='edit_db'),

    # 删除数据库信息
    path('database/delete', DeleteDatabaseInfoView.as_view(), name='del_db'),

    # 添加数据库库
    path('database/db/add', AddDatabaseDBView.as_view(), name='add_db_db'),

    # 修改数据库库
    path('database/db/edit', EditDatabaseDBView.as_view(), name='edit_db_db'),

    # 删除数据库库
    path('database/db/delete', DeleteDatabaseDBView.as_view(), name='del_db_db'),

    # 添加数据库用户
    path('database/user/add', AddDatabaseUserView.as_view(), name='add_db_user'),

    # 修改数据库用户
    path('database/user/edit', EditDatabaseUserView.as_view(), name='edit_db_user'),

    # 删除数据库用户
    path('database/user/delete', DeleteDatabaseUserView.as_view(), name='del_db_user'),

    # 操作记录
    path('operation/record', HostOperationView.as_view(), name='host_op_record'),

    # 网络设备列表
    path('network/dvice/list', NetworkDviceListView.as_view(), name='net_dvice_list'),

    # 添加网络设备
    path('network/dvice/add', AddNetworkDviceView.as_view(), name='net_dvice_add'),

    # 编辑设备
    path('network/dvice/edit', EditNetworkDviceView.as_view(), name='net_dvice_edit'),

    # 删除设备
    path('network/dvice/delete', DeleteNetworkDviceView.as_view(), name='net_dvice_del'),

    # 端口映射列表
    path('port/to/port/list', PortToPortListView.as_view(), name='port_port_list'),

    # 添加端口映射
    path('port/to/port/add', AddPortToPortView.as_view(), name='port_port_add'),

    # 修改端口映射
    path('port/to/port/edit', EditPortToPortView.as_view(), name='port_port_edit'),

    # 删除端口映射
    path('port/to/port/delete', DeletePortToPortView.as_view(), name='port_port_del'),

    # 域名列表
    path('domainname/list', DomainNameListView.as_view(), name='domain_name_list'),

    # 添加域名
    path('domainname/add', AddDomainNameView.as_view(), name='domain_name_add'),

    # 编辑域名
    path('domainname/edit', EditDomainNameView.as_view(), name='domain_name_edit'),

    # 删除域名
    path('domainname/delete', DeleteDomainNameView.as_view(), name='domain_name_del'),

    # 域名解析列表
    path('domainname/resolve/list', DomainNameResolveListView.as_view(), name='domain_resolve_list'),

    # 添加域名解析
    path('domainname/resolve/add', AddDomainNameResolveView.as_view(), name='domain_resolve_add'),

    # 编辑域名解析
    path('domainname/resolve/edit', EditDomainNameResolveView.as_view(), name='domain_resolve_edit'),

    # 删除域名解析
    path('domainname/resolve/delete', DeleteDomainNameResolveView.as_view(), name='domain_resolve_del'),
]


