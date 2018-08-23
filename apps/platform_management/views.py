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


######################################
# 内部平台列表
######################################
class CompanyPlatformListView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'platform'
        web_chose_left_2 = 'company'
        web_chose_middle = ''

        title = '内部平台'

        platforms = PlatformInfo.objects.filter(belong=1).filter(is_public=True)

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'title': title,
            'platforms': platforms,
        }
        return render(request, 'platform-management/platform_list.html', context=context)


######################################
# 运维平台列表
######################################
class OpsPlatformListView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'platform'
        web_chose_left_2 = 'ops'
        web_chose_middle = ''

        title = '运维平台'

        platforms = PlatformInfo.objects.filter(belong=2).filter(is_public=True)

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'title': title,
            'platforms': platforms,
        }
        return render(request, 'platform-management/platform_list.html', context=context)


######################################
# 添加平台用户列表
######################################
class EditPlatformUserView(LoginStatusCheck, View):
    def post(self, request):
        try:
            pu_id = request.POST.get('pu_id', '')
            if pu_id != '':
                pu = PlatformUserInfo.objects.get(id=int(pu_id))
                pu.username = request.POST.get('username', '')
                pu.password = request.POST.get('password', '')
                pu.update_user = request.user
                pu.save()
            else:
                platform_id = int(request.POST.get('platform_id'))
                pu = PlatformUserInfo()
                pu.platform_id = platform_id
                pu.username = request.POST.get('username', '')
                pu.password = request.POST.get('password', '')
                pu.user = request.user
                pu.update_user = request.user
                pu.save()

            return HttpResponse('{"status":"success", "msg":"修改用户成功！"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"failed", "msg":"修改用户失败！"}', content_type='application/json')


######################################
# 其它平台列表
######################################
class OtherPlatformListView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'platform'
        web_chose_left_2 = 'other'
        web_chose_middle = ''

        title = '其它平台'

        platforms = PlatformInfo.objects.filter(belong=3).filter(add_user=request.user)

        platform_nums = platforms.count()

        # 判断页码
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # 对取到的数据进行分页，记得定义每页的数量
        p = Paginator(platforms, 17, request=request)

        # 分页处理后的 QuerySet
        platforms = p.page(page)

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'title': title,
            'platforms': platforms,
            'platform_nums': platform_nums,
        }
        return render(request, 'platform-management/user_platform_list.html', context=context)


######################################
# 添加其它平台
######################################
class AddOtherPlatformView(LoginStatusCheck, View):
    def post(self, request):
        try:
            name = request.POST.get("name", "")
            url = request.POST.get("url", "")
            if (name != "") and (url != ""):
                plat_obj = PlatformInfo()
                plat_obj.name = name
                plat_obj.url = url
                plat_obj.belong = 3
                plat_obj.is_public = False
                plat_obj.add_user = request.user
                plat_obj.save()
                return HttpResponse('{"status":"success", "msg":"添加个人平台成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写错误！"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"failed", "msg":"未知错误！"}', content_type='application/json')




















