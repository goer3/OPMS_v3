######################################
# Django 模块
######################################
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


######################################
# 用户是否登录检测
######################################
class LoginStatusCheck(object):
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginStatusCheck, self).dispatch(request, *args, **kwargs)

