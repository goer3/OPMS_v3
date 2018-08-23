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
import datetime, time
import os, xlwt
from io import StringIO, BytesIO

######################################
# 自建模块
######################################
from utils.login_check import LoginStatusCheck
from .forms import *
from .models import *


######################################
# 故障列表
######################################
class TroubleListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'online_management'
            web_chose_left_2 = 'trouble'

            web_title = "故障列表"

            users = UserProfile.objects.filter(status=1)
            tags = TroubleTag.objects.all()
            projects = ProjectInfo.objects.filter(status=1)
            urls = DomainNameResolveInfo.objects.all()

            records = TroubleRecord.objects.filter(status=1).order_by('-event_time')

            # 搜索，导出条件筛选
            start_time = request.GET.get("start_time", "")
            stop_time = request.GET.get("stop_time", "")
            project_list = request.GET.getlist("project_check", "")
            tag_list = request.GET.getlist("tag_check", "")
            user_list = request.GET.getlist("user_check", "")
            result_list = request.GET.getlist("result_check", "")

            export_data = ""

            # 判断用户操作
            action = request.GET.get("action", "")
            if action != "":
                if (action == "search") or (action == "export_search"):
                    if start_time != "":
                        records = records.filter(event_time__gte=start_time)

                    if stop_time != "":
                        records = records.filter(event_time__lte=stop_time)

                    if project_list != "":
                        records = records.filter(project__in=project_list).distinct()

                    if tag_list != "":
                        records = records.filter(tags__in=tag_list).distinct()

                    if user_list != "":
                        records = records.filter(handle_user__in=user_list).distinct()

                    if result_list != "":
                        records = records.filter(handle_result__in=result_list).distinct()

                    web_title = '故障查询'

                    if action == "export_search":
                        export_data = records

                if (action == "export_all"):
                    export_data = records

                if (action == "export_search") or (action == "export_all"):
                    # 创建 excel
                    new_excel = xlwt.Workbook(encoding='utf-8')
                    excel_page = new_excel.add_sheet(u'故障记录')

                    # 插入第一行标题
                    excel_page.write(0, 0, u'平台名称')
                    excel_page.write(0, 1, u'域名')
                    excel_page.write(0, 2, u'项目')
                    excel_page.write(0, 3, u'事件原因')
                    excel_page.write(0, 4, u'标签')
                    excel_page.write(0, 5, u'故障时间')
                    excel_page.write(0, 6, u'处理人')
                    excel_page.write(0, 7, u'处理办法')
                    excel_page.write(0, 8, u'处理时间')
                    excel_page.write(0, 9, u'处理结果')
                    excel_page.write(0, 10, u'备注')

                    # 初始行
                    excel_row = 1

                    if (export_data != '') and export_data:
                        for each in export_data:
                            name_excel = each.name

                            url_excel = ''
                            if each.url:
                                url_excel = each.url.name + '.' + each.url.domain_name.name

                            project_excel = each.project.name
                            event_excel = each.event

                            # 标签
                            tag_excel = ''

                            if each.tags.all().exists():
                                for each_tag in each.tags.all():
                                    tag_excel = tag_excel + each_tag.name + ', '

                            event_time_excel = each.event_time

                            # 人员
                            handle_user_excel = ''

                            if each.handle_user.all().exists():
                                for each_user in each.handle_user.all():
                                    handle_user_excel = handle_user_excel + each_user.chinese_name + ', '

                            handle_way_excel = each.handle_way
                            handle_time_excel = each.handle_time

                            if each.handle_result == 1:
                                handle_result_excel = '已处理'

                            if each.handle_result == 2:
                                handle_result_excel = '未处理'

                            if each.handle_result == 3:
                                handle_result_excel = '其它'

                            desc_excel = each.desc

                            # 定义时间格式
                            time_style = 'YYYY/MM/DD HH:mm'
                            style = xlwt.XFStyle()
                            style.num_format_str = time_style

                            # 写数据
                            excel_page.write(excel_row, 0, name_excel)
                            excel_page.write(excel_row, 1, url_excel)
                            excel_page.write(excel_row, 2, project_excel)
                            excel_page.write(excel_row, 3, event_excel)
                            excel_page.write(excel_row, 4, tag_excel)
                            excel_page.write(excel_row, 5, event_time_excel, style)
                            excel_page.write(excel_row, 6, handle_user_excel)
                            excel_page.write(excel_row, 7, handle_way_excel)
                            excel_page.write(excel_row, 8, handle_time_excel, style)
                            excel_page.write(excel_row, 9, handle_result_excel)
                            excel_page.write(excel_row, 10, desc_excel)

                            # 行数加1
                            excel_row += 1

                        # 导出文件
                        time_now = time.strftime("%Y%m%d%H%M%S", time.localtime())
                        filename = '故障记录_' + time_now + '.xls'
                        response = HttpResponse(content_type='application/vnd.ms-excel')
                        response['Content-Disposition'] = 'attachment;filename={}'.format(
                            filename.encode('utf-8').decode("ISO-8859-1"))
                        output = BytesIO()
                        new_excel.save(output)
                        output.seek(0)
                        response.write(output.getvalue())
                        return response

            # 搜索
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                records = records.filter(
                    Q(name__icontains=keyword) | Q(event__icontains=keyword) | Q(handle_way__icontains=keyword) | Q(
                        desc__icontains=keyword))

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
                'web_title': web_title,
                'users': users,
                'tags': tags,
                'projects': projects,
                'urls': urls,
                'records': records,
                'keyword': keyword,
                'record_nums': record_nums,
                'start_time': start_time,
                'stop_time': stop_time,
                'project_list': project_list,
                'tag_list': tag_list,
                'user_list': user_list,
                'result_list': result_list,
            }

            return render(request, 'online_namagement/trouble/trouble_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加故障记录
######################################
class AddTroubleRecordView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_tr_form = AddTroubleRecordForm(request.POST)
            if add_tr_form.is_valid():
                try:
                    # 获取数据
                    name = request.POST.get("name")
                    url = request.POST.get("url", "")
                    project = int(request.POST.get("project"))
                    event = request.POST.get("event")
                    tags = request.POST.getlist("tags")
                    event_time = request.POST.get("event_time")
                    handle_user = request.POST.getlist("handle_user")
                    handle_way = request.POST.get("handle_way")
                    handle_time = request.POST.get("handle_time")
                    handle_result = int(request.POST.get("handle_result"))
                    desc = request.POST.get("desc", "")

                    if tags:
                        # 添加记录
                        tr_obj = TroubleRecord()
                        tr_obj.name = name

                        # 判断 url 是否有
                        if url != '':
                            tr_obj.url_id = int(url)

                        tr_obj.project_id = project
                        tr_obj.event = event
                        tr_obj.event_time = event_time
                        tr_obj.handle_way = handle_way
                        tr_obj.handle_time = handle_time
                        tr_obj.handle_result = handle_result
                        tr_obj.desc = desc
                        tr_obj.status = 1
                        tr_obj.save()

                        # 添加标签
                        for each in tags:
                            tr_obj.tags.add(TroubleTag.objects.get(id=int(each)))
                            tr_obj.save()

                        # 添加用户
                        if handle_user:
                            for each in handle_user:
                                tr_obj.handle_user.add(UserProfile.objects.get(id=int(each)))
                                tr_obj.save()
                        else:
                            tr_obj.handle_user.add(request.user)
                            tr_obj.save()

                        return HttpResponse('{"status":"success", "msg":"添加成功！"}', content_type='application/json')
                    else:
                        return HttpResponse('{"status":"failed", "msg":"标签为必选项！"}', content_type='application/json')
                except Exception as e:
                    return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 修改故障记录
######################################
class EditTroubleRecordView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_tr_form = AddTroubleRecordForm(request.POST)
            if edit_tr_form.is_valid():
                try:
                    # 获取数据
                    name = request.POST.get("name")
                    url = request.POST.get("url", "")
                    project = int(request.POST.get("project"))
                    event = request.POST.get("event")
                    tags = request.POST.getlist("tags")
                    event_time = request.POST.get("event_time")
                    handle_user = request.POST.getlist("handle_user")
                    handle_way = request.POST.get("handle_way")
                    handle_time = request.POST.get("handle_time")
                    handle_result = int(request.POST.get("handle_result"))
                    desc = request.POST.get("desc", "")

                    if tags:
                        # 添加记录
                        tr_obj = TroubleRecord.objects.get(id=int(request.POST.get("record_id")))
                        tr_obj.name = name

                        # 判断 url 是否有
                        if url != '':
                            tr_obj.url_id = int(url)

                        tr_obj.project_id = project
                        tr_obj.event = event
                        tr_obj.event_time = event_time
                        tr_obj.handle_way = handle_way
                        tr_obj.handle_time = handle_time
                        tr_obj.handle_result = handle_result
                        tr_obj.desc = desc
                        tr_obj.save()

                        # 添加标签
                        tr_obj.tags.clear()
                        for each in tags:
                            tr_obj.tags.add(TroubleTag.objects.get(id=int(each)))
                            tr_obj.save()

                        # 添加用户
                        tr_obj.handle_user.clear()
                        if handle_user:
                            for each in handle_user:
                                tr_obj.handle_user.add(UserProfile.objects.get(id=int(each)))
                                tr_obj.save()
                        else:
                            tr_obj.handle_user.add(request.user)
                            tr_obj.save()

                        return HttpResponse('{"status":"success", "msg":"修改成功！"}', content_type='application/json')
                    else:
                        return HttpResponse('{"status":"failed", "msg":"标签为必选项！"}', content_type='application/json')
                except Exception as e:
                    return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除故障记录
######################################
class DeleteTroubleRecordView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            try:
                tr_obj = TroubleRecord.objects.get(id=int(request.POST.get("record_id")))
                tr_obj.status = 0
                tr_obj.save()
                return HttpResponse('{"status":"success", "msg":"删除成功！"}', content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"failed", "msg":"未知错误！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 添加标签
######################################
class AddTroubleTagView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            try:
                # 获取数据
                name = request.POST.get("name", "")
                if name != "":
                    if TroubleTag.objects.filter(name=name):
                        return HttpResponse('{"status":"failed", "msg":"该标签已经存在！"}', content_type='application/json')
                    else:
                        tag_obj = TroubleTag()
                        tag_obj.name = name
                        tag_obj.save()
                        return HttpResponse('{"status":"success", "msg":"添加成功！"}', content_type='application/json')
                else:
                    return HttpResponse('{"status":"failed", "msg":"标签不能为空！"}', content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"failed", "msg":"未知错误！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 上线列表
######################################
class DeployListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'online_management'
            web_chose_left_2 = 'deploy'

            users = UserProfile.objects.filter(status=1)
            projects = ProjectInfo.objects.filter(status=1)
            urls = DomainNameResolveInfo.objects.all()

            records = DeployRecord.objects.filter(status=1).order_by("-deploy_time")

            # 搜索
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                records = records.filter(Q(name__icontains=keyword) | Q(request_user__icontains=keyword) | Q(
                    deploy_user__chinese_name__icontains=keyword) | Q(desc__icontains=keyword))

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
                'users': users,
                'projects': projects,
                'urls': urls,
                'keyword': keyword,
                'records': records,
                'record_nums': record_nums,
            }

            return render(request, 'online_namagement/deploy/deploy_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加发布记录
######################################
class AddDeployRecordView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_dep_form = AddDeployRecordForm(request.POST)
            if add_dep_form.is_valid():
                try:
                    # 获取数据
                    name = request.POST.get("name")
                    url = request.POST.get("url", "")
                    project = int(request.POST.get("project"))
                    deploy_time = request.POST.get("deploy_time")
                    request_user = request.POST.get("request_user")
                    deploy_user = request.POST.get("deploy_user")
                    deploy_result = int(request.POST.get("deploy_result"))
                    desc = request.POST.get("desc", "")

                    # 添加记录
                    dep_obj = DeployRecord()
                    dep_obj.name = name

                    # 判断 url 是否有
                    if url != '':
                        dep_obj.url_id = int(url)

                    dep_obj.project_id = project
                    dep_obj.deploy_time = deploy_time
                    dep_obj.request_user = request_user
                    dep_obj.deploy_user = UserProfile.objects.get(id=int(deploy_user))
                    dep_obj.deploy_result = deploy_result
                    dep_obj.desc = desc
                    dep_obj.status = 1
                    dep_obj.save()

                    return HttpResponse('{"status":"success", "msg":"添加成功！"}', content_type='application/json')
                except Exception as e:
                    return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 修改发布记录
######################################
class EditDeployRecordView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_dep_form = AddDeployRecordForm(request.POST)
            if edit_dep_form.is_valid():
                try:
                    # 获取数据
                    name = request.POST.get("name")
                    url = request.POST.get("url", "")
                    project = int(request.POST.get("project"))
                    deploy_time = request.POST.get("deploy_time")
                    request_user = request.POST.get("request_user")
                    deploy_user = request.POST.get("deploy_user")
                    deploy_result = int(request.POST.get("deploy_result"))
                    desc = request.POST.get("desc", "")

                    # 添加记录
                    dep_obj = DeployRecord.objects.get(id=int(request.POST.get("record_id")))
                    dep_obj.name = name

                    # 判断 url 是否有
                    if url != '':
                        dep_obj.url_id = int(url)

                    dep_obj.project_id = project
                    dep_obj.deploy_time = deploy_time
                    dep_obj.request_user = request_user
                    dep_obj.deploy_user = UserProfile.objects.get(id=int(deploy_user))
                    dep_obj.deploy_result = deploy_result
                    dep_obj.desc = desc
                    dep_obj.save()

                    return HttpResponse('{"status":"success", "msg":"修改成功！"}', content_type='application/json')
                except Exception as e:
                    return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除发布记录
######################################
class DeleteDeployRecordView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            try:
                dep_obj = DeployRecord.objects.get(id=int(request.POST.get("record_id")))
                dep_obj.status = 0
                dep_obj.save()
                return HttpResponse('{"status":"success", "msg":"删除成功！"}', content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"failed", "msg":"未知错误！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 运维事件列表
######################################
class OpEventListView(LoginStatusCheck, View):
    def get(self, request):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'online_management'
            web_chose_left_2 = 'op_event'

            users = UserProfile.objects.filter(status=1)

            records = OpsEvent.objects.filter(status=1).order_by('-start_time')

            # 搜索
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                records = records.filter(Q(name__icontains=keyword) | Q(desc__icontains=keyword))

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
                'users': users,
                'keyword': keyword,
                'records': records,
                'record_nums': record_nums,
            }

            return render(request, 'online_namagement/opevent/opevent_list.html', context=context)
        else:
            return HttpResponse(status=403)


######################################
# 添加运维事件
######################################
class AddOpEventView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_op_event_form = AddOpEventForm(request.POST)
            if add_op_event_form.is_valid():
                try:
                    # 获取数据
                    name = request.POST.get("name")
                    start_time = request.POST.get("start_time")
                    stop_time  = request.POST.get("stop_time", "")
                    desc = request.POST.get("desc", "")

                    # 添加记录
                    event_obj = OpsEvent()
                    event_obj.name = name
                    event_obj.start_time = start_time
                    if stop_time != "":
                        event_obj.stop_time = stop_time
                    event_obj.desc = desc
                    event_obj.status = 1
                    event_obj.save()

                    users = request.POST.getlist("op_user")

                    if users:
                        for each in users:
                            event_obj.op_user.add(UserProfile.objects.get(id=int(each)))
                            event_obj.save()
                    else:
                        event_obj.op_user = request.user

                    return HttpResponse('{"status":"success", "msg":"添加成功！"}', content_type='application/json')
                except Exception as e:
                    return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 修改运维事件
######################################
class EditOpEventView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_op_event_form = AddOpEventForm(request.POST)
            if edit_op_event_form.is_valid():
                try:
                    # 获取数据
                    name = request.POST.get("name")
                    start_time = request.POST.get("start_time")
                    stop_time = request.POST.get("stop_time", "")
                    desc = request.POST.get("desc", "")

                    # 添加记录
                    event_obj = OpsEvent.objects.get(id=int(request.POST.get("record_id")))
                    event_obj.name = name
                    event_obj.start_time = start_time
                    if stop_time != "":
                        event_obj.stop_time = stop_time
                    event_obj.desc = desc
                    event_obj.status = 1
                    event_obj.save()

                    event_obj.op_user.clear()
                    users = request.POST.getlist("op_user", "")

                    if users != "":
                        for each in users:
                            event_obj.op_user.add(UserProfile.objects.get(id=int(each)))
                            event_obj.save()
                    else:
                        event_obj.op_user = request.user

                    return HttpResponse('{"status":"success", "msg":"修改成功！"}', content_type='application/json')
                except Exception as e:
                    return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写不正确！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除运维事件
######################################
class DeleteOpEventView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            try:
                event_obj = OpsEvent.objects.get(id=int(request.POST.get("record_id")))
                event_obj.status = 0
                event_obj.save()
                return HttpResponse('{"status":"success", "msg":"删除成功！"}', content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"failed", "msg":"未知错误！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)