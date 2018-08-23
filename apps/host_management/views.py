######################################
# Django 模块
######################################
from django.shortcuts import render, HttpResponseRedirect, redirect, reverse
from django.views import View
from django.http import HttpResponse
from django.db.models import Q
from django.urls import reverse

######################################
# 第三方模块
######################################
from pure_pagination import PageNotAnInteger, Paginator, EmptyPage

######################################
# 系统模块
######################################
import json
import datetime

######################################
# 自建模块
######################################
from utils.login_check import LoginStatusCheck
from .forms import *
from .models import *
from operation_record.models import UserOperationRecord
from opms.settings import WEBSSH_IP, WEBSSH_PORT


##############################################################################
# 主机资产模块
##############################################################################

######################################
# 主机列表
######################################
class HostListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'host_management'
            web_chose_left_2 = 'host'
            web_chose_middle = ''

            # 操作系统
            systems = OperatingSystemInfo.objects.filter(status=1)

            # 项目
            projects = ProjectInfo.objects.filter(status=1)

            # 机房
            idcs = IdcInfo.objects.filter(status=1)

            # 环境
            envs = OperatingEnvironmentInfo.objects.filter(status=1)

            # 用途
            uses = UseInfo.objects.filter(status=1)

            # 用户
            users = UserProfile.objects.filter(status=1)

            # 获取主机记录
            host_records = HostInfo.objects.filter(status=1).order_by('-update_time')

            # 筛选条件
            project = int(request.GET.get('project', '0'))
            if project != 0:
                host_records = host_records.filter(project_id=project)

            idc = int(request.GET.get('idc', '0'))
            if idc != 0:
                host_records = host_records.filter(idc_id=idc)

            env = int(request.GET.get('env', '0'))
            if env != 0:
                host_records = host_records.filter(op_env_id=env)

            use = int(request.GET.get('use', '0'))
            if use != 0:
                host_records = host_records.filter(use_id=use)

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                host_records = host_records.filter(Q(hostname__icontains=keyword) | Q(
                    use__name__icontains=keyword) | Q(project__name__icontains=keyword) | Q(desc__icontains=keyword))

            # 记录数量
            record_nums = host_records.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(host_records, 16, request=request)

            # 分页处理后的 QuerySet
            host_records = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'systems': systems,
                'projects': projects,
                'idcs': idcs,
                'envs': envs,
                'uses': uses,
                'users': users,
                'project': project,
                'idc': idc,
                'env': env,
                'use': use,
                'keyword': keyword,
                'host_records': host_records,
                'record_nums': record_nums,
                'WEBSSH_IP': WEBSSH_IP,
                'WEBSSH_PORT': WEBSSH_PORT,
            }
            return render(request, 'host_management/host/host_list.html', context=context)
        else:
            return HttpResponse(status=403)


########################################################################################################################
## wessh主机视图
########################################################################################################################
class WebSSHView(LoginStatusCheck, View):
    def post(self, request, host_id):
        host = HostInfo.objects.get(id=int(host_id))
        ret = {}
        try:
            if host.out_ip:
                ip = host.out_ip
            else:
                ip = host.in_ip

            port = host.ssh_port

            if host.normal_user:
                username = host.normal_user
                password = host.normal_pass
            else:
                username = host.admin_user
                password = host.admin_pass

            ret = {"ip": ip, 'port': port, "username": username, 'password': password, "static": True}
        except Exception as e:
            ret['status'] = False
            ret['error'] = '请求错误,{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


######################################
# 添加主机
######################################
class AddHostInfoView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_host_info_form = AddHostInfoForm(request.POST)
            if add_host_info_form.is_valid():
                in_ip = request.POST.get('in_ip')

                if HostInfo.objects.filter(in_ip=in_ip).filter(status=1):
                    return HttpResponse('{"status":"failed", "msg":"该 IP 的主机已经存在，请检查！"}',
                                        content_type='application/json')

                host = HostInfo()
                host.in_ip = request.POST.get('in_ip')
                host.out_ip = request.POST.get('out_ip', '')
                host.system_id = int(request.POST.get('system'))
                host.hostname = request.POST.get('hostname')
                host.cpu = request.POST.get('cpu')
                host.disk = int(request.POST.get('disk'))
                host.memory = int(request.POST.get('memory'))
                host.network = int(request.POST.get('network'))
                host.ssh_port = int(request.POST.get('ssh_port'))
                host.root_ssh = request.POST.get('root_ssh')
                host.op_env_id = int(request.POST.get('op_env'))
                host.use_id = int(request.POST.get('use'))
                host.project_id = int(request.POST.get('project'))
                host.idc_id = int(request.POST.get('idc'))
                host.admin_user = request.POST.get('admin_user')
                host.admin_pass = request.POST.get('admin_pass')
                host.normal_user = request.POST.get('normal_user', '')
                host.normal_pass = request.POST.get('normal_pass', '')
                host.op_user_id = int(request.POST.get('op_user'))
                host.update_user = request.user
                host.desc = request.POST.get('desc', '')
                host.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = host.id
                op_record.operation = 1
                op_record.action = "添加 [ %s ] 机房主机：%s" % (host.idc.name, host.in_ip)
                op_record.save()
                return HttpResponse('{"status":"success", "msg":"主机信息添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"主机信息填写错误，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 主机详情
######################################
class HostInfoView(LoginStatusCheck, View):
    def get(self, request, host_id):
        # 页面选择
        web_chose_left_1 = 'host_management'
        web_chose_left_2 = 'host'
        web_chose_middle = ''

        # 操作系统
        systems = OperatingSystemInfo.objects.filter(status=1)

        # 项目
        projects = ProjectInfo.objects.filter(status=1)

        # 机房
        idcs = IdcInfo.objects.filter(status=1)

        # 环境
        envs = OperatingEnvironmentInfo.objects.filter(status=1)

        # 用途
        uses = UseInfo.objects.filter(status=1)

        # 用户
        users = UserProfile.objects.filter(status=1)

        # 信息
        records = HostInfo.objects.get(id=host_id)

        # 服务
        services = HostServiceInfo.objects.filter(host_id=host_id).filter(status=1)

        # 判断是否添加数据库
        is_install_db = DatabaseInfo.objects.filter(host_id=int(host_id)).filter(status=1)

        if is_install_db:
            for each in is_install_db:
                have_db_id = each.id
        else:
            have_db_id = ''

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'records': records,
            'systems': systems,
            'projects': projects,
            'idcs': idcs,
            'envs': envs,
            'uses': uses,
            'users': users,
            'services': services,
            'have_db_id': have_db_id,
        }
        return render(request, 'host_management/host/host_info.html', context=context)


######################################
# 删除主机
######################################
class DeleteHostView(LoginStatusCheck, View):
    def post(self, request):
        try:
            host_id = request.POST.get('host_id')
            host = HostInfo.objects.get(id=int(host_id))
            host.update_user = request.user
            host.status = 0
            host.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = host.id
            op_record.operation = 4
            op_record.action = "停用 [ %s ] 机房主机：%s" % (host.idc.name, host.in_ip)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"主机删除成功！"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"falied", "msg":"主机删除失败！"}', content_type='application/json')


######################################
# 修改主机
######################################
class EditHostInfoView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_host_info_form = EditHostInfoForm(request.POST)
            if edit_host_info_form.is_valid():

                # 获取主机
                host_id = int(request.POST.get('host_id'))
                host = HostInfo.objects.get(id=host_id)

                host.in_ip = request.POST.get('in_ip')
                host.out_ip = request.POST.get('out_ip', '')
                host.system_id = int(request.POST.get('system'))
                host.hostname = request.POST.get('hostname')
                host.cpu = request.POST.get('cpu')
                host.disk = int(request.POST.get('disk'))
                host.memory = int(request.POST.get('memory'))
                host.network = int(request.POST.get('network'))
                host.ssh_port = int(request.POST.get('ssh_port'))
                host.root_ssh = request.POST.get('root_ssh')
                host.op_env_id = int(request.POST.get('op_env'))
                host.use_id = int(request.POST.get('use'))
                host.project_id = int(request.POST.get('project'))
                host.idc_id = int(request.POST.get('idc'))
                host.admin_user = request.POST.get('admin_user')
                host.admin_pass = request.POST.get('admin_pass')
                host.normal_user = request.POST.get('normal_user', '')
                host.normal_pass = request.POST.get('normal_pass', '')
                host.op_user_id = int(request.POST.get('op_user'))
                host.update_user = request.user
                host.desc = request.POST.get('desc', '')
                host.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = host.id
                op_record.operation = 2
                op_record.action = "修改 [ %s ] 机房主机：%s" % (host.idc.name, host.in_ip)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"主机信息修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"主机信息填写错误，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 数据库列表
######################################
class DatabaseListView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'host_management'
        web_chose_left_2 = 'database'
        web_chose_middle = ''

        # 主机列表
        hosts = HostInfo.objects.filter(status=1)

        # 机房
        idcs = IdcInfo.objects.filter(status=1)

        # 环境
        envs = OperatingEnvironmentInfo.objects.filter(status=1)

        # 用户
        users = UserProfile.objects.filter(status=1)

        # 数据库记录
        db_records = DatabaseInfo.objects.filter(status=1).order_by('-update_time')

        # 筛选条件
        idc = int(request.GET.get('idc', '0'))
        if idc != 0:
            db_records = db_records.filter(host__idc_id=idc)

        env = int(request.GET.get('env', '0'))
        if env != 0:
            db_records = db_records.filter(host__op_env_id=env)

        # 关键字
        keyword = request.GET.get('keyword', '')
        if keyword != '':
            db_records = db_records.filter(Q(host__in_ip=keyword))

        # 记录数量
        record_nums = db_records.count()

        # 判断页码
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # 对取到的数据进行分页，记得定义每页的数量
        p = Paginator(db_records, 16, request=request)

        # 分页处理后的 QuerySet
        db_records = p.page(page)

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'hosts': hosts,
            'idcs': idcs,
            'envs': envs,
            'idc': idc,
            'env': env,
            'users': users,
            'keyword': keyword,
            'record_nums': record_nums,
            'db_records': db_records,
        }
        return render(request, 'host_management/host/db_list.html', context=context)


######################################
# 数据库详情
######################################
class DatabaseInfoView(LoginStatusCheck, View):
    def get(self, request, db_id):
        # 页面选择
        web_chose_left_1 = 'host_management'
        web_chose_left_2 = 'database'
        web_chose_middle = ''

        # 数据库基本信息
        db_records = DatabaseInfo.objects.get(id=int(db_id))

        # 数据库库信息
        db_db_records = DatabaseDBInfo.objects.filter(db_id=int(db_id)).filter(status=1).order_by('-update_time')

        # 数据库用户信息
        db_user_records = DatabaseUserInfo.objects.filter(db_id=int(db_id)).filter(status=1).order_by('-update_time')

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'db_records': db_records,
            'db_db_records': db_db_records,
            'db_user_records': db_user_records,
        }
        return render(request, 'host_management/host/db_info.html', context=context)


######################################
# 添加数据库记录
######################################
class AddDatabaseInfoView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            if DatabaseInfo.objects.filter(host_id=int(request.POST.get('host_id'))).filter(status=1):
                return HttpResponse('{"status":"failed", "msg":"该主机的记录已经存在，请检查！"}', content_type='application/json')

            add_db_info_form = AddDatabaseInfoForm(request.POST)

            if add_db_info_form.is_valid():
                db_info = DatabaseInfo()
                db_info.host_id = int(request.POST.get('host_id'))
                db_info.db_name = request.POST.get('db_name')
                db_info.db_version = request.POST.get('db_version')
                db_info.db_admin_user = request.POST.get('db_admin_user')
                db_info.db_admin_pass = request.POST.get('db_admin_pass')
                db_info.desc = request.POST.get('desc', '')
                db_info.add_user = request.user
                db_info.update_user = request.user
                db_info.status = 1
                db_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = db_info.id
                op_record.operation = 1
                op_record.action = "添加数据库记录：%s" % (db_info.host.in_ip)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 修改数据库记录
######################################
class EditDatabaseInfoView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_db_info_form = EditDatabaseInfoForm(request.POST)
            if edit_db_info_form.is_valid():
                db_info = DatabaseInfo.objects.get(id=int(request.POST.get('db_id')))

                # 判断记录是否重复
                db_host = int(request.POST.get('host_id'))

                if db_info.host_id != db_host:
                    if DatabaseInfo.objects.filter(host_id=db_host).filter(status=1):
                        return HttpResponse('{"status":"failed", "msg":"该主机的记录已经存在，请检查！"}',
                                            content_type='application/json')

                # 不重复继续修改
                db_info.host_id = db_host
                db_info.db_name = request.POST.get('db_name')
                db_info.db_version = request.POST.get('db_version')
                db_info.db_admin_user = request.POST.get('db_admin_user')
                db_info.db_admin_pass = request.POST.get('db_admin_pass')
                db_info.desc = request.POST.get('desc', '')
                db_info.update_user = request.user
                db_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = db_info.id
                op_record.operation = 2
                op_record.action = "修改数据库记录：%s" % (db_info.host.in_ip)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除数据库记录
######################################
class DeleteDatabaseInfoView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            db_info = DatabaseInfo.objects.get(id=int(request.POST.get('db_id')))
            db_info.status = 0
            db_info.update_user = request.user
            db_info.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = db_info.id
            op_record.operation = 4
            op_record.action = "停用数据库记录：%s" % (db_info.host.in_ip)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"删除成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 添加数据库库
######################################
class AddDatabaseDBView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            if DatabaseDBInfo.objects.filter(db_id=int(request.POST.get('db_id'))).filter(
                    name=request.POST.get('name')).filter(status=1):
                return HttpResponse('{"status":"failed", "msg":"该记录已经存在，请检查！"}', content_type='application/json')

            add_db_form = AddDatabaseDBForm(request.POST)

            if add_db_form.is_valid():
                db_info = DatabaseDBInfo()
                db_info.db_id = int(request.POST.get('db_id'))
                db_info.name = request.POST.get('name')
                db_info.use = request.POST.get('use')
                db_info.desc = request.POST.get('desc', '')
                db_info.add_user = request.user
                db_info.update_user = request.user
                db_info.status = 1
                db_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = db_info.id
                op_record.operation = 1
                op_record.action = "添加主机 [ %s ] 的数据库：%s" % (db_info.db.host.in_ip, db_info.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑数据库库
######################################
class EditDatabaseDBView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            db_info = DatabaseDBInfo.objects.get(id=int(request.POST.get('db_id')))

            # 判断记录是否存在
            if db_info.name != request.POST.get('name'):
                if DatabaseDBInfo.objects.filter(db_id=int(request.POST.get('db_db_id'))).filter(
                        name=request.POST.get('name')).filter(status=1):
                    return HttpResponse('{"status":"failed", "msg":"该记录已经存在，请检查！"}', content_type='application/json')

            edit_db_form = EditDatabaseDBForm(request.POST)

            if edit_db_form.is_valid():
                db_info.db_id = int(request.POST.get('db_db_id'))
                db_info.name = request.POST.get('name')
                db_info.use = request.POST.get('use')
                db_info.desc = request.POST.get('desc', '')
                db_info.update_user = request.user
                db_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = db_info.id
                op_record.operation = 2
                op_record.action = "修改主机 [ %s ] 的数据库：%s" % (db_info.db.host.in_ip, db_info.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除数据库库
######################################
class DeleteDatabaseDBView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            db_info = DatabaseDBInfo.objects.get(id=int(request.POST.get('db_id')))
            db_info.update_user = request.user
            db_info.status = 0
            db_info.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.operation = 4
            op_record.action = "删除主机 [ %s ] 的数据库：%s" % (db_info.db.host.in_ip, db_info.name)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"删除成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 添加数据库用户
######################################
class AddDatabaseUserView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            # 判断用户
            db_user = DatabaseUserInfo.objects.filter(db_id=int(request.POST.get('db_id'))).filter(
                username=request.POST.get('username'))
            if db_user:
                return HttpResponse('{"status":"failed", "msg":"该用户已存在，请检查！"}', content_type='application/json')

            add_db_user_form = AddDatabaseUserForm(request.POST)
            if add_db_user_form.is_valid():
                db_user = DatabaseUserInfo()
                db_user.db_id = int(request.POST.get('db_id'))
                db_user.username = request.POST.get('username')
                db_user.password = request.POST.get('password')
                db_user.grant_login = request.POST.get('grant_login')
                db_user.desc = request.POST.get('desc', '')
                db_user.add_user = request.user
                db_user.update_user = request.user
                db_user.status = 1
                db_user.save()

                for each in request.POST.getlist('dbs'):
                    db = DatabaseDBInfo.objects.get(id=int(each))
                    db_user.grant_db.add(db)
                    db_user.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = db_user.id
                op_record.operation = 1
                op_record.action = "添加主机 [ %s ] 的数据库用户：%s" % (db_user.db.host.in_ip, db_user.username)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑数据库用户
######################################
class EditDatabaseUserView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            # 判断用户
            db_user = DatabaseUserInfo.objects.get(id=int(request.POST.get('db_user_id')))

            new_username = request.POST.get('username')

            if db_user.username != new_username:
                if DatabaseUserInfo.objects.filter(username=new_username).filter(status=1):
                    return HttpResponse('{"status":"failed", "msg":"该用户已存在，请检查！"}', content_type='application/json')

            edit_db_user_form = EditDatabaseUserForm(request.POST)
            if edit_db_user_form.is_valid():
                db_user.username = request.POST.get('username')
                db_user.password = request.POST.get('password')
                db_user.grant_login = request.POST.get('grant_login')
                db_user.desc = request.POST.get('desc', '')
                db_user.update_user = request.user
                db_user.grant_db.clear()
                db_user.save()

                for each in request.POST.getlist('dbs'):
                    db = DatabaseDBInfo.objects.get(id=int(each))
                    db_user.grant_db.add(db)
                    db_user.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = db_user.id
                op_record.operation = 2
                op_record.action = "修改主机 [ %s ] 的数据库用户：%s" % (db_user.db.host.in_ip, db_user.username)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除数据库用户
######################################
class DeleteDatabaseUserView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            # 判断用户
            db_user = DatabaseUserInfo.objects.get(id=int(request.POST.get('db_user_id')))
            db_user.status = 0
            db_user.update_user = request.user
            db_user.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = db_user.id
            op_record.operation = 4
            op_record.action = "停用主机 [ %s ] 的数据库用户：%s" % (db_user.db.host.in_ip, db_user.username)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"删除成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


##############################################################################
# 基础配置模块
##############################################################################


######################################
# 添加系统服务
######################################
class AddHostServiceView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_service_form = AddHostServiceForm(request.POST)
            if add_service_form.is_valid():
                service = HostServiceInfo()
                host = int(request.POST.get('host_id'))
                service.host_id = host
                service.name = request.POST.get('name')
                service.version = request.POST.get('version')
                service.listen_user = request.POST.get('listen_user')
                service.listen_port = request.POST.get('listen_port')
                service.ins_path = request.POST.get('ins_path')
                service.log_path = request.POST.get('log_path')
                service.backup_path = request.POST.get('backup_path', '')
                service.start_cmd = request.POST.get('start_cmd')
                service.desc = request.POST.get('desc', '')
                service.add_user = request.user
                service.update_user = request.user
                service.status = 1
                service.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = service.id
                op_record.operation = 1
                op_record.action = "添加主机 [ %s ] 的服务：%s" % (service.host.in_ip, service.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"主机服务添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"主机服务填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑系统服务
######################################
class EditHostServiceView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_service_form = EditHostServiceForm(request.POST)
            if edit_service_form.is_valid():
                service = HostServiceInfo.objects.get(id=int(request.POST.get('ser_id')))
                service.name = request.POST.get('name')
                service.version = request.POST.get('version')
                service.listen_user = request.POST.get('listen_user')
                service.listen_port = request.POST.get('listen_port')
                service.ins_path = request.POST.get('ins_path')
                service.log_path = request.POST.get('log_path')
                service.backup_path = request.POST.get('backup_path', '')
                service.start_cmd = request.POST.get('start_cmd')
                service.desc = request.POST.get('desc', '')
                service.update_user = request.user
                service.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = service.id
                op_record.operation = 2
                op_record.action = "修改主机 [ %s ] 的服务：%s" % (service.host.in_ip, service.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"主机服务修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"主机服务填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除服务
######################################
class DeleteHostServiceView(LoginStatusCheck, View):
    def post(self, request):
        try:
            ser_id = request.POST.get('ser_id')
            service = HostServiceInfo.objects.get(id=int(ser_id))
            service.update_user = request.user
            service.status = 0
            service.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = service.id
            op_record.operation = 4
            op_record.action = "停用主机 [ %s ] 的服务：%s" % (service.host.in_ip, service.name)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"服务删除成功！"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"falied", "msg":"服务删除失败！"}', content_type='application/json')


######################################
# 操作系统
######################################
class OSListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'basic_setting'
            web_chose_left_2 = 'os'
            web_chose_middle = ''

            # 获取操作系统
            systems = OperatingSystemInfo.objects.filter(status=1).order_by('-update_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                systems = systems.filter(
                    Q(name__icontains=keyword) | Q(version__icontains=keyword) | Q(desc__icontains=keyword) | Q(
                        add_user__chinese_name__icontains=keyword) | Q(update_user__chinese_name__icontains=keyword))

            # 数量
            system_nums = systems.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(systems, 16, request=request)

            # 分页处理后的 QuerySet
            systems = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'systems': systems,
                'keyword': keyword,
                'system_nums': system_nums,
            }
            return render(request, 'host_management/other/system_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加操作系统
######################################
class AddOSView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_os_form = AddOsForm(request.POST)
            if add_os_form.is_valid():
                # 判断是否有相同的记录
                name = request.POST.get('name')
                version = request.POST.get('version')
                bit = int(request.POST.get('bit'))
                check_os = OperatingSystemInfo.objects.filter(name=name).filter(version=version).filter(bit=bit).filter(
                    status=1)
                if check_os:
                    return HttpResponse('{"status":"failed", "msg":"该记录已经存在，请检查！"}', content_type='application/json')

                # 添加记录
                os = OperatingSystemInfo()
                os.name = name
                os.version = version
                os.bit = bit
                os.desc = request.POST.get('desc', '')
                os.add_user = request.user
                os.update_user = request.user
                os.status = 1
                os.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = os.id
                op_record.operation = 1
                op_record.action = "添加操作系统：%s %s ( %s )" % (os.name, os.version, os.bit)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"操作系统添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑操作系统
######################################
class EditOSView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_os_form = EditOsForm(request.POST)
            if edit_os_form.is_valid():
                os = OperatingSystemInfo.objects.get(id=int(request.POST.get('sys_id')))
                os.name = request.POST.get('name')
                os.version = request.POST.get('version')
                os.bit = int(request.POST.get('bit'))
                os.desc = request.POST.get('desc', '')
                os.update_user = request.user
                os.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = os.id
                op_record.operation = 2
                op_record.action = "修改操作系统：%s %s ( %s )" % (os.name, os.version, os.bit)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"操作系统修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除操作系统
######################################
class DeleteOSView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            os = OperatingSystemInfo.objects.get(id=int(request.POST.get('sys_id')))
            os.status = 0
            os.update_user = request.user
            os.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = os.id
            op_record.operation = 4
            op_record.action = "停用操作系统：%s %s ( %s )" % (os.name, os.version, os.bit)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"操作系统删除成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 机房管理
######################################
class IdcListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'basic_setting'
            web_chose_left_2 = 'idc'
            web_chose_middle = ''

            # 获取操作系统
            idcs = IdcInfo.objects.filter(status=1).order_by('-update_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                idcs = idcs.filter(
                    Q(name__icontains=keyword) | Q(address__icontains=keyword) | Q(desc__icontains=keyword) | Q(
                        add_user__chinese_name__icontains=keyword) | Q(update_user__chinese_name__icontains=keyword))

            # 数量
            idc_nums = idcs.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(idcs, 16, request=request)

            # 分页处理后的 QuerySet
            idcs = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'idcs': idcs,
                'keyword': keyword,
                'idc_nums': idc_nums,
            }
            return render(request, 'host_management/other/idc_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加机房
######################################
class AddIDCView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_idc_form = AddIdcForm(request.POST)
            if add_idc_form.is_valid():
                # 判断是否有相同的记录
                name = request.POST.get('name')
                address = request.POST.get('address')
                check_idc = IdcInfo.objects.filter(name=name).filter(address=address).filter(status=1)
                if check_idc:
                    return HttpResponse('{"status":"failed", "msg":"该记录已经存在，请检查！"}', content_type='application/json')

                # 添加记录
                idc = IdcInfo()
                idc.name = name
                idc.address = address
                idc.desc = request.POST.get('desc', '')
                idc.add_user = request.user
                idc.update_user = request.user
                idc.status = 1
                idc.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = idc.id
                op_record.operation = 1
                op_record.action = "添加机房：%s" % (idc.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"机房添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑机房
######################################
class EditIDCView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_idc_form = EditIdcForm(request.POST)
            if edit_idc_form.is_valid():
                idc = IdcInfo.objects.get(id=int(request.POST.get('idc_id')))
                idc.name = request.POST.get('name')
                idc.address = request.POST.get('address')
                idc.desc = request.POST.get('desc', '')
                idc.update_user = request.user
                idc.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = idc.id
                op_record.operation = 2
                op_record.action = "修改机房：%s" % (idc.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"机房修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除机房
######################################
class DeleteIDCView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            idc = IdcInfo.objects.get(id=int(request.POST.get('idc_id')))
            idc.status = 0
            idc.update_user = request.user
            idc.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = idc.id
            op_record.operation = 4
            op_record.action = "停用机房：%s" % (idc.name)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"机房删除成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 项目管理
######################################
class ProjectListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'basic_setting'
            web_chose_left_2 = 'project'
            web_chose_middle = ''

            # 人员
            users = UserProfile.objects.filter(status=1)

            # 获取操作系统
            projects = ProjectInfo.objects.filter(status=1).order_by('-update_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                projects = projects.filter(
                    Q(name__icontains=keyword) | Q(run_env__icontains=keyword) | Q(pro_user__icontains=keyword) | Q(
                        add_user__chinese_name__icontains=keyword) | Q(
                        update_user__chinese_name__icontains=keyword) | Q(op_user__chinese_name__icontains=keyword))

            # 数量
            project_nums = projects.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(projects, 16, request=request)

            # 分页处理后的 QuerySet
            projects = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'users': users,
                'projects': projects,
                'keyword': keyword,
                'project_nums': project_nums,
            }
            return render(request, 'host_management/other/project_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加项目
######################################
class AddProjectView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_project_form = AddProjectForm(request.POST)
            if add_project_form.is_valid():
                # 判断是否有相同的记录
                name = request.POST.get('name')
                check_pro = ProjectInfo.objects.filter(name=name).filter(status=1)
                if check_pro:
                    return HttpResponse('{"status":"failed", "msg":"该记录已经存在，请检查！"}', content_type='application/json')

                # 添加记录
                pro = ProjectInfo()
                pro.name = name
                pro.pro_user = request.POST.get('pro_user')
                pro.op_user_id = int(request.POST.get('op_user'))
                pro.run_env = request.POST.get('run_env')
                pro.add_user = request.user
                pro.update_user = request.user
                pro.status = 1
                pro.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = pro.id
                op_record.operation = 1
                op_record.action = "添加项目：%s" % (pro.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"项目添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑项目
######################################
class EditProjectView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_project_form = EditProjectForm(request.POST)
            if edit_project_form.is_valid():
                pro = ProjectInfo.objects.get(id=int(request.POST.get('pro_id')))
                pro.name = request.POST.get('name')
                pro.pro_user = request.POST.get('pro_user')
                pro.op_user_id = int(request.POST.get('op_user'))
                pro.run_env = request.POST.get('run_env')
                pro.update_user = request.user
                pro.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = pro.id
                op_record.operation = 2
                op_record.action = "修改项目：%s" % (pro.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"项目修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除项目
######################################
class DeleteProjectView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            pro = ProjectInfo.objects.get(id=int(request.POST.get('pro_id')))
            pro.status = 0
            pro.update_user = request.user
            pro.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = pro.id
            op_record.operation = 4
            op_record.action = "停用项目：%s" % (pro.name)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"项目删除成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 环境管理
######################################
class OpEnvListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'basic_setting'
            web_chose_left_2 = 'env'
            web_chose_middle = ''

            # 获取环境
            openvs = OperatingEnvironmentInfo.objects.filter(status=1).order_by('-update_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                openvs = openvs.filter(
                    Q(name__icontains=keyword) | Q(desc__icontains=keyword) | Q(
                        add_user__chinese_name__icontains=keyword) | Q(
                        update_user__chinese_name__icontains=keyword))

            # 数量
            openv_nums = openvs.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(openvs, 16, request=request)

            # 分页处理后的 QuerySet
            openvs = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'openvs': openvs,
                'keyword': keyword,
                'openv_nums': openv_nums,
            }
            return render(request, 'host_management/other/openv_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加环境
######################################
class AddOpEnvView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_openv_form = AddOpEnvForm(request.POST)
            if add_openv_form.is_valid():
                # 判断是否有相同的记录
                name = request.POST.get('name')
                check_openv = OperatingEnvironmentInfo.objects.filter(name=name).filter(status=1)
                if check_openv:
                    return HttpResponse('{"status":"failed", "msg":"该记录已经存在，请检查！"}', content_type='application/json')

                # 添加记录
                openv = OperatingEnvironmentInfo()
                openv.name = name
                openv.desc = request.POST.get('desc', '')
                openv.add_user = request.user
                openv.update_user = request.user
                openv.status = 1
                openv.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = openv.id
                op_record.operation = 1
                op_record.action = "添加环境：%s" % (openv.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"环境添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑环境
######################################
class EditOpEnvView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_openv_form = EditOpEnvForm(request.POST)
            if edit_openv_form.is_valid():
                openv = OperatingEnvironmentInfo.objects.get(id=int(request.POST.get('env_id')))
                openv.name = request.POST.get('name')
                openv.desc = request.POST.get('desc', '')
                openv.update_user = request.user
                openv.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = openv.id
                op_record.operation = 2
                op_record.action = "修改环境：%s" % (openv.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"环境修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除环境
######################################
class DeleteOpEnvView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            openv = OperatingEnvironmentInfo.objects.get(id=int(request.POST.get('env_id')))
            openv.status = 0
            openv.update_user = request.user
            openv.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = openv.id
            op_record.operation = 4
            op_record.action = "停用环境：%s" % (openv.name)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"环境删除成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 用途管理
######################################
class UseListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'basic_setting'
            web_chose_left_2 = 'use'
            web_chose_middle = ''

            # 获取环境
            uses = UseInfo.objects.filter(status=1).order_by('-update_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                uses = uses.filter(
                    Q(name__icontains=keyword) | Q(desc__icontains=keyword) | Q(
                        add_user__chinese_name__icontains=keyword) | Q(
                        update_user__chinese_name__icontains=keyword))

            # 数量
            use_nums = uses.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(uses, 16, request=request)

            # 分页处理后的 QuerySet
            uses = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'uses': uses,
                'keyword': keyword,
                'use_nums': use_nums,
            }
            return render(request, 'host_management/other/use_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加用途
######################################
class AddUseView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_use_form = AddUseForm(request.POST)
            if add_use_form.is_valid():
                # 判断是否有相同的记录
                name = request.POST.get('name')
                check_use = UseInfo.objects.filter(name=name).filter(status=1)
                if check_use:
                    return HttpResponse('{"status":"failed", "msg":"该记录已经存在，请检查！"}', content_type='application/json')

                # 添加记录
                use = UseInfo()
                use.name = name
                use.desc = request.POST.get('desc', '')
                use.add_user = request.user
                use.update_user = request.user
                use.status = 1
                use.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = use.id
                op_record.operation = 1
                op_record.action = "添加用途：%s" % (use.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"用途添加成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑用途
######################################
class EditUseView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_use_form = EditUseForm(request.POST)
            if edit_use_form.is_valid():
                use = UseInfo.objects.get(id=int(request.POST.get('use_id')))
                use.name = request.POST.get('name')
                use.desc = request.POST.get('desc', '')
                use.update_user = request.user
                use.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = use.id
                op_record.operation = 2
                op_record.action = "修改用途：%s" % (use.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"用途修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除用途
######################################
class DeleteUseView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            use = UseInfo.objects.get(id=int(request.POST.get('use_id')))
            use.status = 0
            use.update_user = request.user
            use.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = use.id
            op_record.operation = 4
            op_record.action = "停用用途：%s" % (use.name)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"用途删除成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 主机操作记录
######################################
class HostOperationView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'log_management'
            web_chose_left_2 = 'op_log'
            web_chose_middle = ''

            records = UserOperationRecord.objects.filter(belong=1).order_by('-add_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                records = records.filter(
                    Q(op_user__chinese_name=keyword) | Q(action__icontains=keyword))

            # 用户选择
            user_check = request.GET.get('user_check', 'all')

            # 添加
            if user_check == 'add':
                records = records.filter(operation=1)

            # 修改
            if user_check == 'edit':
                records = records.filter(operation=2)

            # 启用
            if user_check == 'up':
                records = records.filter(operation=3)

            # 停用
            if user_check == 'down':
                records = records.filter(operation=4)

            # 数量
            record_nums = records.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(records, 19, request=request)

            # 分页处理后的 QuerySet
            records = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'records': records,
                'keyword': keyword,
                'record_nums': record_nums,
                'user_check': user_check,
            }
            return render(request, 'host_management/other/host_op_record.html', context=context)
        else:
            return HttpResponse(status=403)


##############################################################################
# 网络资产模块
##############################################################################


######################################
# 网络设备列表
######################################
class NetworkDviceListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'host_management'
            web_chose_left_2 = 'net_dvice'
            web_chose_middle = ''

            records = NetworkDviceInfo.objects.filter(status=1).order_by('-update_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                records = records.filter(
                    Q(category__icontains=keyword) | Q(name__icontains=keyword) | Q(desc__icontains=keyword))

            # 数量
            record_nums = records.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(records, 16, request=request)

            # 分页处理后的 QuerySet
            records = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'records': records,
                'keyword': keyword,
                'record_nums': record_nums,
            }
            return render(request, 'host_management/port/network_dvice_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加网络设备
######################################
class AddNetworkDviceView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            name = request.POST.get('name')
            ip_in = request.POST.get('ip_in')
            if NetworkDviceInfo.objects.filter(name=name).filter(ip_in=ip_in).filter(status=1):
                return HttpResponse('{"status":"failed", "msg":"该记录已存在，请检查！"}', content_type='application/json')

            add_net_dvice_form = AddNetDviceForm(request.POST)

            if add_net_dvice_form.is_valid():
                net_dvice = NetworkDviceInfo()
                net_dvice.category = request.POST.get('name')
                net_dvice.name = name
                net_dvice.ip_in = request.POST.get('ip_in')
                net_dvice.ip_out = request.POST.get('ip_out', '')
                net_dvice.address = request.POST.get('address')
                net_dvice.admin_user = request.POST.get('admin_user')
                net_dvice.admin_pass = request.POST.get('admin_pass')
                net_dvice.desc = request.POST.get('desc', '')
                net_dvice.add_user = request.user
                net_dvice.update_user = request.user
                net_dvice.status = 1
                net_dvice.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = net_dvice.id
                op_record.operation = 1
                op_record.action = "添加网络设备：%s [ %s ]" % (net_dvice.name, net_dvice.ip_in)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"添加设备成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑网络设备
######################################
class EditNetworkDviceView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            net_dvice = NetworkDviceInfo.objects.get(id=int(request.POST.get('dv_id')))

            name = request.POST.get('name')
            ip_in = request.POST.get('ip_in')

            # 判断记录是否存在
            if net_dvice.name != name:
                if NetworkDviceInfo.objects.filter(name=name).filter(ip_in=ip_in).filter(status=1):
                    return HttpResponse('{"status":"failed", "msg":"该记录已存在，请检查！"}', content_type='application/json')

            edit_net_dvice_form = EditNetDviceForm(request.POST)

            if edit_net_dvice_form.is_valid():
                net_dvice.category = request.POST.get('name')
                net_dvice.name = name
                net_dvice.ip_in = request.POST.get('ip_in')
                net_dvice.ip_out = request.POST.get('ip_out', '')
                net_dvice.address = request.POST.get('address')
                net_dvice.admin_user = request.POST.get('admin_user')
                net_dvice.admin_pass = request.POST.get('admin_pass')
                net_dvice.desc = request.POST.get('desc', '')
                net_dvice.update_user = request.user
                net_dvice.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = net_dvice.id
                op_record.operation = 2
                op_record.action = "修改网络设备：%s [ %s ]" % (net_dvice.name, net_dvice.ip_in)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"修改设备成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除设备
######################################
class DeleteNetworkDviceView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            net_dvice = NetworkDviceInfo.objects.get(id=int(request.POST.get('dv_id')))
            net_dvice.status = 0
            net_dvice.update_user = request.user
            net_dvice.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = net_dvice.id
            op_record.operation = 4
            op_record.action = "停用网络设备：%s [ %s ]" % (net_dvice.name, net_dvice.ip_in)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"设备删除成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 端口映射列表
######################################
class PortToPortListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'port_domain'
            web_chose_left_2 = 'port_port'
            web_chose_middle = ''

            records = PortToPortInfo.objects.filter(status=1).order_by('-update_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                records = records.filter(
                    Q(ip_in=keyword) | Q(port_in=keyword) | Q(ip_out=keyword) | Q(port_out=keyword) | Q(
                        use__icontains=keyword) | Q(desc__icontains=keyword))

            # 数量
            record_nums = records.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(records, 16, request=request)

            # 分页处理后的 QuerySet
            records = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'records': records,
                'keyword': keyword,
                'record_nums': record_nums,
            }
            return render(request, 'host_management/port/port_to_port_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加映射
######################################
class AddPortToPortView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            ip_in = request.POST.get('ip_in')
            port_in = request.POST.get('port_in')

            if PortToPortInfo.objects.filter(ip_in=ip_in).filter(port_in=port_in).filter(status=1):
                return HttpResponse('{"status":"failed", "msg":"该记录已存在，请检查！"}', content_type='application/json')

            add_port_to_port_form = AddPortToPortForm(request.POST)

            if add_port_to_port_form.is_valid():
                port_info = PortToPortInfo()
                port_info.ip_out = request.POST.get('ip_out', '')
                port_info.port_out = request.POST.get('port_out')
                port_info.ip_in = ip_in
                port_info.port_in = port_in
                port_info.use = request.POST.get('use')
                port_info.desc = request.POST.get('desc', '')
                port_info.add_user = request.user
                port_info.update_user = request.user
                port_info.status = 1
                port_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = port_info.id
                op_record.operation = 1
                op_record.action = "添加 [ %s:%s ] 映射：[ %s:%s ]" % (port_info.ip_out, port_info.port_out, port_info.ip_in, port_info.port_in)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"添加映射成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 编辑映射
######################################
class EditPortToPortView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            port_info = PortToPortInfo.objects.get(id=int(request.POST.get('p_id')))

            ip_in = request.POST.get('ip_in')
            port_in = request.POST.get('port_in')

            if (port_info.ip_in != ip_in) and (port_info.port_in != port_in):
                if PortToPortInfo.objects.filter(ip_in=ip_in).filter(port_in=port_in).filter(status=1):
                    return HttpResponse('{"status":"failed", "msg":"该记录已存在，请检查！"}', content_type='application/json')

            edit_port_to_port_form = EditPortToPortForm(request.POST)

            if edit_port_to_port_form.is_valid():
                port_info.ip_out = request.POST.get('ip_out', '')
                port_info.port_out = request.POST.get('port_out')
                port_info.ip_in = ip_in
                port_info.port_in = port_in
                port_info.use = request.POST.get('use')
                port_info.desc = request.POST.get('desc', '')
                port_info.update_user = request.user
                port_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = port_info.id
                op_record.operation = 2
                op_record.action = "编辑 [ %s:%s ] 映射：[ %s:%s ]" % (port_info.ip_out, port_info.port_out, port_info.ip_in, port_info.port_in)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"编辑映射成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除映射
######################################
class DeletePortToPortView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            port_info = PortToPortInfo.objects.get(id=int(request.POST.get('p_id')))
            port_info.update_user = request.user
            port_info.status = 0
            port_info.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = port_info.id
            op_record.operation = 4
            op_record.action = "停用 [ %s:%s ] 映射：[ %s:%s ]" % (port_info.ip_out, port_info.port_out, port_info.ip_in, port_info.port_in)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"停用映射成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 域名列表
######################################
class DomainNameListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'port_domain'
            web_chose_left_2 = 'domain_name'
            web_chose_middle = ''

            records = DomainNameInfo.objects.filter(status=1).order_by('-update_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                records = records.filter(
                    Q(name__icontains=keyword) | Q(desc__icontains=keyword))

            # 数量
            record_nums = records.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(records, 16, request=request)

            # 分页处理后的 QuerySet
            records = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'records': records,
                'keyword': keyword,
                'record_nums': record_nums,
            }
            return render(request, 'host_management/port/domain_name_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加域名
######################################
class AddDomainNameView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            name = request.POST.get('name')

            if DomainNameInfo.objects.filter(name=name).filter(status=1):
                return HttpResponse('{"status":"failed", "msg":"该记录已存在，请检查！"}', content_type='application/json')

            add_domain_name_form = AddDomainNameForm(request.POST)

            if add_domain_name_form.is_valid():
                domain_info = DomainNameInfo()
                domain_info.name = request.POST.get('name')
                domain_info.desc = request.POST.get('desc', '')
                domain_info.add_user = request.user
                domain_info.update_user = request.user
                domain_info.status = 1
                domain_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = domain_info.id
                op_record.operation = 1
                op_record.action = "添加域名：%s" % domain_info.name
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"添加域名成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 修改域名
######################################
class EditDomainNameView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            domain_info = DomainNameInfo.objects.get(id=int(request.POST.get('do_id')))

            name = request.POST.get('name')

            if domain_info.name != name:
                if DomainNameInfo.objects.filter(name=name).filter(status=1):
                    return HttpResponse('{"status":"failed", "msg":"该记录已存在，请检查！"}', content_type='application/json')

            edit_domain_name_form = EditDomainNameForm(request.POST)

            if edit_domain_name_form.is_valid():
                domain_info.name = request.POST.get('name')
                domain_info.desc = request.POST.get('desc', '')
                domain_info.update_user = request.user
                domain_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = domain_info.id
                op_record.operation = 2
                op_record.action = "修改域名：%s" % domain_info.name
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"修改域名成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除域名
######################################
class DeleteDomainNameView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            domain_info = DomainNameInfo.objects.get(id=int(request.POST.get('do_id')))
            domain_info.update_user = request.user
            domain_info.status = 0
            domain_info.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = domain_info.id
            op_record.operation = 4
            op_record.action = "停用域名：%s" % domain_info.name
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"停用域名成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 域名解析列表
######################################
class DomainNameResolveListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'port_domain'
            web_chose_left_2 = 'domain_resolve'
            web_chose_middle = ''

            records = DomainNameResolveInfo.objects.filter(status=1).order_by('-update_time')

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                records = records.filter(Q(ip=keyword) | Q(domain_name__name__icontains=keyword) | Q(desc__icontains=keyword))

            # 数量
            record_nums = records.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(records, 16, request=request)

            # 分页处理后的 QuerySet
            records = p.page(page)

            domains = DomainNameInfo.objects.filter(status=1)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'records': records,
                'keyword': keyword,
                'record_nums': record_nums,
                'domains': domains,
            }
            return render(request, 'host_management/port/domain_name_resolve_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加域名解析
######################################
class AddDomainNameResolveView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            name = request.POST.get('name')
            domain_name_id = int(request.POST.get('domain_name'))

            if DomainNameResolveInfo.objects.filter(name=name).filter(domain_name_id=domain_name_id).filter(status=1):
                return HttpResponse('{"status":"failed", "msg":"该记录已存在，请检查！"}', content_type='application/json')

            add_domain_resolve_form = AddDomainNameResolveForm(request.POST)

            if add_domain_resolve_form.is_valid():
                domain_info = DomainNameResolveInfo()
                domain_info.name = name
                domain_info.domain_name_id = domain_name_id
                domain_info.desc = request.POST.get('desc', '')
                domain_info.ip = request.POST.get('ip')
                domain_info.add_user = request.user
                domain_info.update_user = request.user
                domain_info.status = 1
                domain_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = domain_info.id
                op_record.operation = 1
                op_record.action = "添加域名解析：%s.%s" % (domain_info.name, domain_info.domain_name.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"添加域名解析成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 修改域名解析
######################################
class EditDomainNameResolveView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            domain_info = DomainNameResolveInfo.objects.get(id=int(request.POST.get('do_id')))

            name = request.POST.get('name')
            domain_name_id = int(request.POST.get('domain_name'))

            if (domain_info.name != name) and (domain_info.domain_name_id != domain_name_id):
                if DomainNameResolveInfo.objects.filter(name=name).filter(domain_name_id=domain_name_id).filter(status=1):
                    return HttpResponse('{"status":"failed", "msg":"该记录已存在，请检查！"}', content_type='application/json')

            edit_domain_reslove_form = EditDomainNameResolveForm(request.POST)

            if edit_domain_reslove_form.is_valid():
                domain_info.name = name
                domain_info.domain_name_id = domain_name_id
                domain_info.ip = request.POST.get('ip')
                domain_info.desc = request.POST.get('desc', '')
                domain_info.update_user = request.user
                domain_info.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 1
                op_record.status = 1
                op_record.op_num = domain_info.id
                op_record.operation = 2
                op_record.action = "修改域名解析：%s.%s" % (domain_info.name, domain_info.domain_name.name)
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"修改域名解析成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不合法，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除域名解析
######################################
class DeleteDomainNameResolveView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            domain_info = DomainNameResolveInfo.objects.get(id=int(request.POST.get('do_id')))
            domain_info.update_user = request.user
            domain_info.status = 0
            domain_info.save()

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = request.user
            op_record.belong = 1
            op_record.status = 1
            op_record.op_num = domain_info.id
            op_record.operation = 4
            op_record.action = "停用域名解析：%s.%s" % (domain_info.name, domain_info.domain_name.name)
            op_record.save()

            return HttpResponse('{"status":"success", "msg":"停用域名成功！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)









