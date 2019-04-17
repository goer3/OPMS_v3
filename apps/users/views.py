######################################
# Django 模块
######################################
from django.shortcuts import render, HttpResponseRedirect, redirect, reverse
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.urls import reverse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.sessions.models import Session
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

######################################
# 第三方模块
######################################
from pure_pagination import PageNotAnInteger, Paginator, EmptyPage

######################################
# 系统模块
######################################
import json
import datetime
import urllib

######################################
# 自建模块
######################################
from utils.login_check import LoginStatusCheck
from .forms import *
from .models import *
from operation_record.models import UserOperationRecord
from utils.send_email import send_email_verificode
from utils.user_func import get_ip_location
from opms.settings import GAODE_API_KEY, CITY_ID, DEVELPER_EMAIL_ADDRESS, EMAIL_HOST_USER
from online_management.models import TroubleRecord, DeployRecord


######################################
# 首页
######################################
class IndexView(LoginStatusCheck, View):
    def get(self, request):
        web_chose_left_1 = 'index'
        web_chose_left_2 = ''
        web_chose_middle = ''

        # 客户端 IP
        # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        # if x_forwarded_for:
        #     agent_ip = x_forwarded_for.split(',')[-1].strip()
        # else:
        #     agent_ip = request.META.get('REMOTE_ADDR')
        #
        # # 获取城市
        # url = "http://ip.taobao.com/service/getIpInfo.php?ip="
        # data = urllib.request.urlopen(url + agent_ip).read().decode("utf-8")
        # datadict = json.loads(data)
        # for oneinfo in datadict:
        #     if "code" == oneinfo:
        #         if datadict[oneinfo] == 0:
        #             county = datadict["data"]["city"]
        #             if county != '内网IP':
        #                 city_id = datadict["data"]["city_id"]
        #             else:
        #                 city_id = CITY_ID

        # 获取天气
        # url = "https://restapi.amap.com/v3/weather/weatherInfo?city=%s&key=%s" % (city_id, GAODE_API_KEY)
        # data = urllib.request.urlopen(url).read().decode("utf-8")
        # datadict = json.loads(data)
        # weather_name = datadict["lives"][0]["weather"]
        # temperature = datadict["lives"][0]["temperature"]

        # API 天气列表
        # rain_list = ['阵雨', '小雨', '中雨', '大雨', '暴雨', '大暴雨', '特大暴雨', '冻雨', '小雨-中雨', '中雨-大雨', '大雨-暴雨', '暴雨-大暴雨', '大暴雨-特大暴雨']
        # thunder_list = ['雷阵雨', '雷阵雨并伴有冰雹']
        # snow_list = ['雨夹雪', '阵雪', '小雪', '中雪', '大雪', '暴雪', '小雪-中雪', '中雪-大雪', '大雪-暴雪', '弱高吹雪']
        # sun_list = ['晴', ]
        # cloud_list = ['阴', '多云', '雾', '沙尘暴', '浮尘', '扬沙', '强沙尘暴', '飑', '龙卷风', '轻雾', '霾']

        # 判断天气
        # if weather_name in rain_list:
        #     weather = 'rain'
        # elif weather_name in thunder_list:
        #     weather = 'thunder'
        # elif weather_name in snow_list:
        #     weather = 'snow'
        # elif weather_name in sun_list:
        #     weather = 'sun'
        # elif weather_name in cloud_list:
        #     weather = 'cloud'
        # else:
        #     weather = 'unknow'

        weather_name = '晴'
        weather = 'sun'
        temperature = '0'

        # 获取年月列表
        ym_list = []
        tr_list = []
        dep_list = []
        y_now = datetime.datetime.now().year
        m_now = datetime.datetime.now().month
        i = 0
        while (i < 12):
            ym_list.append(str(y_now) + '-' + str(m_now))
            tr_list.append(TroubleRecord.objects.filter(event_time__year=y_now, event_time__month=m_now).count())
            dep_list.append(DeployRecord.objects.filter(deploy_time__year=y_now, deploy_time__month=m_now).count())

            m_now = m_now - 1
            if m_now == 0:
                m_now = 12
                y_now = y_now - 1

            i += 1

        tr_list = list(reversed(tr_list))
        ym_list = list(reversed(ym_list))
        dep_list = list(reversed(dep_list))

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'weather_name': weather_name,
            'weather': weather,
            'temperature': temperature,
            'ym_list': ym_list,
            'tr_list': tr_list,
            'dep_list': dep_list,
        }

        return render(request, 'users/index.html', context=context)


######################################
# 登录
######################################
class LoginView(View):
    def get(self, request):
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        user_login_form = UerLoginForm()
        context = {
            'user_login_form': user_login_form
        }
        return render(request, 'users/login/login.html', locals())

    def post(self, request):
        user_login_form = UerLoginForm(request.POST)

        # 输入合法
        if user_login_form.is_valid():
            # 获取提交的登录信息
            login_username = request.POST.get('username')
            login_password = request.POST.get('password')

            # 认证用户
            user = authenticate(username=login_username, password=login_password)

            # 判断用户是否正确
            if user is not None:
                if not user.is_active:
                    return HttpResponseRedirect(reverse('users:send_active_email'))
                elif (user.status != 1):
                    msg = '用户已停用，请联系管理员！'
                else:
                    uid1 = UserProfile.objects.get(username=login_username).id

                    # 判断用户是否登录
                    # all_session = Session.objects.all()
                    #
                    # if all_session is not None:
                    #     for session in all_session:
                    #         uid2 = session.get_decoded().get('_auth_user_id')
                    #         if uid1 == uid2:
                    #             session.delete()

                    login(request, user)

                    # 保存登录信息
                    login_record = UserLoginInfo()
                    login_record.action = 1
                    login_record.user = user
                    login_record.agent = request.META['HTTP_USER_AGENT']
                    login_record.ip = request.META['REMOTE_ADDR']
                    login_record.address = '中国 广东 深圳'
                    # login_record.address = get_ip_location(request.META['REMOTE_ADDR'])
                    login_record.save()

                    # 添加操作记录
                    op_record = UserOperationRecord()
                    op_record.op_user = user
                    op_record.belong = 3
                    op_record.status = 1
                    op_record.op_num = user.id
                    op_record.operation = 5
                    op_record.action = "用户 [ %s ] 登录了系统" % user.chinese_name
                    op_record.save()

                    return HttpResponseRedirect(reverse('users:index'))
            else:
                msg = '用户名或密码错误！'

            # 账户有问题的情况
            context = {
                'msg': msg,
                'user_login_form': user_login_form,
            }
            return render(request, 'users/login/login.html', context=context)
        else:
            # msg = '用户账户或密码不满足长度要求！'
            context = {
                # 'msg': msg,
                'user_login_form': user_login_form,
            }
            return render(request, 'users/login/login.html', context=context)


######################################
# 邮箱登录
######################################
class OtherLoginBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 增加邮箱验证
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


######################################
# 登出
######################################
class LogoutView(LoginStatusCheck, View):
    def get(self, request):
        # 保存登录信息
        login_record = UserLoginInfo()
        login_record.action = 2
        login_record.user = request.user
        login_record.agent = request.META['HTTP_USER_AGENT']
        login_record.ip = request.META['REMOTE_ADDR']
        # login_record.address = get_ip_location(request.META['REMOTE_ADDR'])
        login_record.address = '中国 广东 深圳'
        login_record.save()

        # 添加操作记录
        op_record = UserOperationRecord()
        op_record.op_user = request.user
        op_record.belong = 3
        op_record.status = 1
        op_record.op_num = request.user.id
        op_record.operation = 6
        op_record.action = "用户 [ %s ] 退出了系统" % request.user.chinese_name
        op_record.save()

        logout(request)

        return HttpResponseRedirect(reverse('users:login'))


######################################
# 用户激活请求
######################################
class SendActiveUserEmailView(View):
    def get(self, request):
        context = {}
        return render(request, 'users/login/active_user.html', context=context)

    def post(self, request):
        email = request.POST.get('email')

        if UserProfile.objects.filter(email=email):
            user = UserProfile.objects.get(email=email)
            if user.is_active:
                msg = '该用户已经激活！'
            else:
                # 发送邮件
                send_status = send_email_verificode(email, 'active')
                if send_status:
                    msg = '邮件已发送，请注意查收！'
                    context = {
                        'msg': msg,
                    }
                    return render(request, 'users/login/login.html', context=context)
                else:
                    msg = '邮件发送失败，请检查！'
        else:
            msg = '该邮箱不存在，请检查！'

        context = {
            'msg': msg,
        }
        return render(request, 'users/login/active_user.html', context=context)


######################################
# 用户激活处理
######################################
class ActiveUserView(View):
    def get(self, request, active_code):
        code_record = UserEmailVirificationCode.objects.filter(code=active_code).filter(purpose='active').latest(
            'add_time')
        if code_record:
            user = UserProfile.objects.get(email=code_record.email)
            user.is_active = True
            user.save()

            msg = '用户激活成功！'
            context = {
                'msg': msg,
            }

            # 添加操作记录
            op_record = UserOperationRecord()
            op_record.op_user = user
            op_record.belong = 2
            op_record.status = 1
            op_record.op_num = user.id
            op_record.operation = 3
            op_record.action = "用户 [ %s ] 激活成功" % user.chinese_name
            op_record.save()

            return render(request, 'users/login/login.html', context=context)
        else:
            msg = '地址有误，请重新发送重置邮件！'
            context = {
                'msg': msg,
            }
            return render(request, 'users/login/active_user.html', context=context)


######################################
# 忘记密码
######################################
class ForgetPasswordView(View):
    def get(self, request):
        context = {}
        return render(request, 'users/login/forget_password.html', context=context)

    def post(self, request):
        user_forget_password_form = UserForgetPasswordForm(request.POST)

        if user_forget_password_form.is_valid():
            email = request.POST.get('email')
            if UserProfile.objects.filter(email=email):
                # 发送邮件
                send_status = send_email_verificode(email, 'forget')
                if send_status:
                    msg = '邮件已发送，请注意查收！'
                else:
                    msg = '邮件发送失败，请检查！'
            else:
                msg = '该邮箱不存在，请检查！'
        else:
            msg = '邮箱格式不合法，请检查！'

        context = {
            'msg': msg,
        }
        return render(request, 'users/login/forget_password.html', context=context)


######################################
# 重置密码
######################################
class ResetPasswordView(View):
    def get(self, request, reset_code):
        code_record = UserEmailVirificationCode.objects.filter(code=reset_code).filter(purpose='forget').latest(
            'add_time')
        if code_record:
            if not code_record.is_use:
                if (datetime.datetime.now() - code_record.add_time).seconds > 300:
                    msg = '验证码已过期！'
                    context = {
                        'msg': msg,
                    }
                    return render(request, 'users/login/forget_password.html', context=context)
                else:
                    context = {
                        'reset_code': reset_code
                    }
                    return render(request, 'users/login/reset_password.html', context=context)
            else:
                msg = '验证码已被使用！'
                context = {
                    'msg': msg,
                }
                return render(request, 'users/login/forget_password.html', context=context)
        else:
            msg = '地址有误，请重新发送重置邮件！'
            context = {
                'msg': msg,
            }
            return render(request, 'users/login/forget_password.html', context=context)


######################################
# 重置修改密码
######################################
class ModifyPasswordView(View):
    def post(self, request):
        new_password = request.POST.get('new_password')
        renew_password = request.POST.get('renew_password')
        reset_code = request.POST.get('reset_code')
        if new_password != renew_password:
            msg = '密码不一致！'
            context = {
                'msg': msg,
                'reset_code': reset_code
            }
            return render(request, 'users/login/reset_password.html', context=context)
        elif (len(new_password) < 6) or (len(new_password) > 20):
            msg = '密码长度不符合要求！'
            context = {
                'msg': msg,
                'reset_code': reset_code
            }
            return render(request, 'users/login/reset_password.html', context=context)
        else:
            # 获取相应的用户
            code_record = UserEmailVirificationCode.objects.filter(code=reset_code).latest('add_time')
            email = code_record.email
            user = UserProfile.objects.get(email=email)

            # 修改密码
            try:
                user.password = make_password(new_password)
                user.save()

                # 修改验证码状态
                code_record.is_use = True
                code_record.save()

                msg = '密码重置成功！'
                context = {
                    'msg': msg,
                }
                return render(request, 'users/login/login.html', context=context)
            except Exception as e:
                msg = '密码重置失败，请重试！'
                context = {
                    'msg': msg,
                    'reset_code': reset_code
                }
                return render(request, 'users/login/reset_password.html', context=context)


######################################
# 用户信息
######################################
class UserInfoView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'user_management'
        web_chose_left_2 = 'user_info'
        web_chose_middle = 'user_info'

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
        }

        return render(request, 'users/user/user_info.html', context=context)


######################################
# 他人信息
######################################
class OtherUserInfoView(LoginStatusCheck, View):
    def get(self, request, uid):
        # 页面选择
        web_chose_left_1 = 'user_management'
        web_chose_left_2 = 'user_info'
        web_chose_middle = 'user_info'

        user_info = UserProfile.objects.get(id=int(uid))

        if request.user.id == int(uid):
            return HttpResponseRedirect(reverse('users:user_info'))

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'user_info': user_info,
        }

        return render(request, 'users/user/user_info_other.html', context=context)


######################################
# 修改用户信息
######################################
class ChangeUserInfoView(LoginStatusCheck, View):
    def post(self, request):
        # 验证提交的表单
        change_user_info_form = ChangeUserInfoForm(request.POST)

        if change_user_info_form.is_valid():
            user = request.user
            user.english_name = request.POST.get('english_name')
            user.mobile = request.POST.get('mobile')
            user.wechat = request.POST.get('wechat')
            user.qq = request.POST.get('qq')
            birthday = request.POST.get('birthday', "")
            if birthday != '':
                user.birthday = birthday
            user.address = request.POST.get('address')
            user.desc = request.POST.get('desc')
            # 保存修改
            user.save()
            return HttpResponse('{"status":"success", "msg":"用户资料修改成功！"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"failed", "msg":"用户资料修改失败，请检查！"}', content_type='application/json')


######################################
# 用户头像
######################################
class UserAvatarView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'user_management'
        web_chose_left_2 = 'user_info'
        web_chose_middle = 'user_avatar'

        for_round = range(1, 11)

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'for_round': for_round,
        }

        return render(request, 'users/user/user_change_avatar.html', context=context)


######################################
# 上传修改用户头像
######################################
class ChangeUserAvatarUploadView(LoginStatusCheck, View):
    def post(self, request):
        avatar_pic = request.FILES.get('img')
        if avatar_pic:
            user = request.user
            user.avatar = avatar_pic
            user.save()
            return HttpResponse('{"status":"success", "msg":"用户头像上传修改成功！"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"falied", "msg":"用户头像上传修改失败！"}', content_type='application/json')


######################################
# 选择修改用户头像
######################################
class ChangeUserAvatarChoseView(LoginStatusCheck, View):
    def post(self, request):
        user = request.user
        new_avatar = request.POST.get('avatar')

        if new_avatar:
            user.avatar = new_avatar
            # 保存修改
            user.save()
            return HttpResponse('{"status":"success", "msg":"用户头像修改成功！"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"falied", "msg":"用户头像修改失败！"}', content_type='application/json')


######################################
# 用户密码
######################################
class UserPasswordView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'user_management'
        web_chose_left_2 = 'user_info'
        web_chose_middle = 'user_password'

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
        }

        return render(request, 'users/user/user_change_passwd.html', context=context)


######################################
# 修改用户密码
######################################
class ChangeUserPasswordView(LoginStatusCheck, View):
    def post(self, request):
        change_user_password_form = ChangeUserPasswordForm(request.POST)
        if change_user_password_form.is_valid():
            cur_password = request.POST.get('cur_password')
            new_password = request.POST.get('new_password')
            renew_password = request.POST.get('renew_password')

            if new_password != renew_password:
                msg = '两次密码不一致！'
            elif authenticate(username=request.user.username, password=cur_password) is None:
                msg = '当前密码不正确！'
            else:
                request.user.password = make_password(new_password)
                request.user.save()
                return HttpResponseRedirect(reverse('users:login'))
        else:
            msg = '输入不合法，密码最小长度为 6 位！'

        context = {
            'msg': msg
        }
        return render(request, 'users/user/user_change_passwd.html', context=context)


######################################
# 用户邮箱
######################################
class UserEmailView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'user_management'
        web_chose_left_2 = 'user_info'
        web_chose_middle = 'user_email'

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
        }
        return render(request, 'users/user/user_change_email.html', context=context)


######################################
# 发送修改用户邮箱验证码
######################################
class SendChangeUserEmailCodeView(LoginStatusCheck, View):
    def post(self, request):
        email = request.POST.get('email')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"status":"falied", "msg":"该邮箱已经被绑定为其它用户！"}', content_type='application/json')
        else:
            send_status = send_email_verificode(email, 'change_email')
            if send_status:
                return HttpResponse('{"status":"success", "msg":"邮件已发送，请注意查收！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"邮件发送失败，请检查！"}', content_type='application/json')


######################################
# 修改用户邮箱
######################################
class ChangeUserEmailView(LoginStatusCheck, View):
    def post(self, request):
        email = request.POST.get('email')
        code = request.POST.get('code')

        if (email is not None) and (email != ''):
            if (code is not None) and (code != ''):
                if (len(code) == 4):
                    code_record = UserEmailVirificationCode.objects.filter(code=code).latest('add_time')
                    if code_record is not None:
                        if code_record.email == email:
                            if (datetime.datetime.now() - code_record.add_time).seconds < 300:
                                user = request.user
                                user.email = email
                                user.save()
                                return HttpResponse('{"status":"success", "msg":"邮箱修改成功！"}',
                                                    content_type='application/json')
                            else:
                                return HttpResponse('{"status":"failed", "msg":"验证码已过期！"}',
                                                    content_type='application/json')
                        else:
                            return HttpResponse('{"status":"failed", "msg":"邮箱错误！"}', content_type='application/json')
                    else:
                        return HttpResponse('{"status":"failed", "msg":"验证码错误！"}', content_type='application/json')
                else:
                    return HttpResponse('{"status":"failed", "msg":"验证码错误！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"验证码不能为空！"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"failed", "msg":"邮箱不能为空！"}', content_type='application/json')


######################################
# 用户列表
######################################
class UserListView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'user_management'
        web_chose_left_2 = 'user_list'
        web_chose_middle = ''

        # 职位列表
        positions = UserPosition.objects.all()

        # 用户记录
        users = UserProfile.objects.all().order_by('-date_joined')

        # 用户选择
        user_check = request.GET.get('user_check', 'all')

        # 激活
        if user_check == 'active':
            users = users.filter(is_active=True)

        # 未激活
        if user_check == 'notactive':
            users = users.filter(is_active=False)

        # 正常
        if user_check == 'up':
            users = users.filter(status=1)

        # 停用
        if user_check == 'down':
            users = users.filter(status=2)

        # 男性
        if user_check == 'male':
            users = users.filter(gender='male')

        # 女性
        if user_check == 'female':
            users = users.filter(gender='female')

        # 查询
        keyword = request.GET.get('keyword', '')

        if keyword != '':
            users = users.filter(
                Q(username__icontains=keyword) | Q(email__icontains=keyword) | Q(chinese_name__icontains=keyword) | Q(
                    english_name__icontains=keyword) | Q(mobile__icontains=keyword) | Q(wechat__icontains=keyword) | Q(
                    qq__icontains=keyword) | Q(address__icontains=keyword) | Q(desc__icontains=keyword) | Q(
                    position__name__icontains=keyword) | Q(position__department__name__icontains=keyword) | Q(
                    position__department__company__name__icontains=keyword)
            )

        # 判断页码
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # 对取到的数据进行分页，记得定义每页的数量
        p = Paginator(users, 12, request=request)

        # 分页处理后的 QuerySet
        users = p.page(page)

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'positions': positions,
            'users': users,
            'user_check': user_check,
            'keyword': keyword,
        }
        return render(request, 'users/user/user_list.html', context=context)


######################################
# 添加用户
######################################
class AddUserView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            add_user_form = AddUserForm(request.POST)
            if add_user_form.is_valid():
                username = request.POST.get('username')
                email = request.POST.get('email')
                password = request.POST.get('password')
                re_password = request.POST.get('re_password')

                if UserProfile.objects.filter(username=username):
                    return HttpResponse('{"status":"failed", "msg":"该用户名已经被另外的用户使用！"}', content_type='application/json')

                if UserProfile.objects.filter(email=email):
                    return HttpResponse('{"status":"failed", "msg":"该邮箱已经被另外的用户使用！"}', content_type='application/json')

                if password != re_password:
                    return HttpResponse('{"status":"failed", "msg":"两次密码不一致，请检查！"}', content_type='application/json')

                # 获取信息
                chinese_name = request.POST.get('chinese_name')
                mobile = request.POST.get('mobile')
                gender = request.POST.get('gender')
                position = request.POST.get('position')
                role = request.POST.get('role')
                status = request.POST.get('status')

                # 添加用户
                user = UserProfile()
                user.username = username
                user.chinese_name = chinese_name
                user.email = email
                user.mobile = mobile
                user.gender = gender
                user.position = UserPosition.objects.get(id=int(position))
                user.role = int(role)
                user.status = int(status)
                user.password = make_password(password)
                user.is_active = False
                user.save()

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 2
                op_record.status = 1
                op_record.op_num = user.id
                op_record.operation = 1
                op_record.action = "新增用户 [ %s ]" % chinese_name
                op_record.save()

                return HttpResponse('{"status":"success", "msg":"用户添加成功，但未激活，请知悉！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写的内容不正确，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 修改用户
######################################
class EditUserView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            edit_user_form = EditUserForm(request.POST)
            if edit_user_form.is_valid():
                # 被修改的用户
                uid = int(request.POST.get('uid'))
                edit_user = UserProfile.objects.get(id=uid)

                # 判断修改用户名
                username = request.POST.get('username')
                if edit_user.username != username:
                    if UserProfile.objects.filter(username=username):
                        return HttpResponse('{"status":"failed", "msg":"该用户名已经被另外的用户使用！"}',
                                            content_type='application/json')
                    else:
                        edit_user.username = username

                # 判断修改邮箱
                email = request.POST.get('email')
                if edit_user.email != email:
                    if UserProfile.objects.filter(email=email):
                        return HttpResponse('{"status":"failed", "msg":"该邮箱已经被另外的用户使用！"}',
                                            content_type='application/json')
                    else:
                        edit_user.email = email

                # 修改密码
                password = request.POST.get('password', '')
                re_password = request.POST.get('re_password', '')
                if password != '':
                    if password != re_password:
                        return HttpResponse('{"status":"failed", "msg":"两次密码不一致，请检查！"}',
                                            content_type='application/json')
                    else:
                        edit_user.password = make_password(password)

                # 获取其它信息
                chinese_name = request.POST.get('chinese_name')
                mobile = request.POST.get('mobile')
                gender = request.POST.get('gender')
                position = request.POST.get('position')
                role = request.POST.get('role')
                status = request.POST.get('status')

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 2
                op_record.status = 1
                op_record.operation = 2
                op_record.op_num = edit_user.id
                op_record.action = "修改用户 [ %s ]" % chinese_name

                # 判断是否修改用户状态，保存操作记录
                if edit_user.status != int(status):

                    # 启用
                    if int(status) == 1:
                        op_record.operation = 3
                        op_record.action = "启用用户 [ %s ]" % chinese_name

                    # 停用
                    if int(status) == 2:
                        op_record.operation = 4
                        op_record.action = "停用用户 [ %s ]" % chinese_name

                op_record.save()

                # 修改其它信息
                edit_user.chinese_name = chinese_name
                edit_user.mobile = mobile
                edit_user.gender = gender
                edit_user.position_id = int(position)
                edit_user.role = int(role)
                edit_user.status = int(status)

                # 保存修改
                edit_user.save()

                return HttpResponse('{"status":"success", "msg":"用户修改成功！"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"failed", "msg":"填写的内容不正确，请检查！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 用户登录信息
######################################
class UserLoginRecordView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'log_management'
        web_chose_left_2 = 'login_log'
        web_chose_middle = ''

        user_check = 'all'

        # 登录日志记录
        records = UserLoginInfo.objects.filter(user=request.user).order_by('-add_time')

        # 查询
        keyword = request.GET.get('keyword', '')

        if keyword != '':
            records = records.filter(
                Q(ip__icontains=keyword) | Q(agent__icontains=keyword) | Q(address__icontains=keyword)
            )

        if request.GET.get('user_check'):
            if request.GET.get('user_check') == 'login':
                records = records.filter(action=1)
                user_check = 'login'

            if request.GET.get('user_check') == 'logout':
                records = records.filter(action=2)
                user_check = 'logout'

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
            'record_nums': record_nums,
            'keyword': keyword,
            'user_check': user_check,
        }
        return render(request, 'users/user/user_login_record.html', context=context)


######################################
# 用户操作信息
######################################
class UserOperationRecordView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'log_management'
        web_chose_left_2 = 'user_log'
        web_chose_middle = ''

        # 日志记录
        records = UserOperationRecord.objects.filter(belong=2).order_by('-add_time')

        # 查询
        keyword = request.GET.get('keyword', '')

        if keyword != '':
            records = records.filter(Q(op_user__chinese_name__icontains=keyword) | Q(action__icontains=keyword))

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
            'record_nums': record_nums,
            'keyword': keyword,
            'user_check': user_check,
        }
        return render(request, 'users/user/user_op_record.html', context=context)


######################################
# 获取帮助
######################################
class AskHelpView(LoginStatusCheck, View):
    def get(self, request):
        # 页面选择
        web_chose_left_1 = 'ask_help'
        web_chose_left_2 = ''
        web_chose_middle = ''

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,

        }
        return render(request, 'users/help.html', context=context)

    def post(self, request):
        # 页面选择
        web_chose_left_1 = 'ask_help'
        web_chose_left_2 = ''
        web_chose_middle = ''

        subject = request.POST.get("subject", "")
        content = request.POST.get("content", "")

        if (subject != "") and (content != ""):
            user = request.user

            ask_help = UserAskHelp()
            ask_help.user = user
            ask_help.subject = subject
            ask_help.content = content
            ask_help.save()

            send_status = send_mail(subject, content, EMAIL_HOST_USER, [DEVELPER_EMAIL_ADDRESS,])
            if send_status:
                msg = '反馈成功！'
            else:
                msg = '反馈邮件发送失败！'
        else:
            msg = '主题和内容都为必填项！'

        context = {
            'web_chose_left_1': web_chose_left_1,
            'web_chose_left_2': web_chose_left_2,
            'web_chose_middle': web_chose_middle,
            'msg': msg,
        }
        return render(request, 'users/help.html', context=context)


# 错误页面
def page_not_found(request):
    return render(request, 'error/404.html')


def page_error(request):
    return render(request, 'error/500.html')


def permission_denied(request):
    return render(request, 'error/403.html')

