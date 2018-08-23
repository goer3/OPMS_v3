######################################
# Django 模块
######################################
from users.models import UserEmailVirificationCode
from django.core.mail import send_mail, EmailMultiAlternatives

######################################
# 自己写的模块
######################################
from opms.settings import SERVER_URL, EMAIL_HOST_USER

######################################
# 系统模块
######################################
import random
import datetime
import time


######################################
# 生成随机字符串
######################################
def make_random_code(code_length=4):
    chars = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789'
    random_code = ''
    random_length = len(chars) - 1
    for each_code in range(code_length):
        random_code += chars[random.randint(0, random_length)]

    return random_code


######################################
# 发送验证码
######################################
def send_email_verificode(email_to, purpose='register'):
    # 判断用户请求的需求
    if purpose == 'change_email':
        code = make_random_code(code_length=4)
    else:
        code = make_random_code(code_length=16)

    # 保存生成的数据
    user_email_verifycode = UserEmailVirificationCode()
    user_email_verifycode.code = code
    user_email_verifycode.email = email_to
    user_email_verifycode.purpose = purpose
    user_email_verifycode.save()

    # 发送重置密码邮件
    body_str = '''
        <div style="background-color: lightgrey; height: 500px; padding-bottom: 100px;">
            <div style="padding-top: 100px;">
                <div style="background-color: white; width: 600px; height: 400px; margin: 0 auto;">
                    <div style="padding: 10px;">
                        <div style="background-color: #1c2b36; height: 100px; line-height: 100px;text-align: center;font-size: 30px;color: white;font-weight: bolder;">
                            <span>{}</span>
                        </div>
                        <div style="padding-left: 20px; padding-right: 20px;font-size: 14px;">
                            <p>尊敬的用户您好：</p>
                            <p>这是一封来自于 OPMS 系统的{}邮件，{}：</p>
                            <p style="text-align: center">
                                <a href="" style="text-decoration: none;color: red; font-size: 16px; font-weight: bolder;" target="_blank">{}</a>
                            </p>
                            <p>{}，或不是您本人发起的请求，只需忽略该邮件即可！</p>
                            <p>最后，OPMS 团队感谢您长久以来的支持，愿您顺颂商祺！</p>
                            <div style="text-align: right;">
                                <p>OPMS 研发团队</p>
                                <p>{}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    '''

    if purpose == 'forget':
        # 定制消息
        mail_content_title = '重 置 密 码'
        mail_content_purpose = '重置密码'
        mail_content_use = '您可使用下面链接来修改您的密码'
        mail_content_msg = (SERVER_URL + '/reset/' + code)
        mail_content_else = '若您不希望修改您的密码'
        mail_content_date = (str(datetime.datetime.now().year) + '年' + str(datetime.datetime.now().month) + '月' + str(datetime.datetime.now().day) + '日 ' + time.strftime("%H:%M:%S"))

        # 消息内容
        email_title = '[ OPMS ] 重 置 密 码 ！（ 有效期 5 分钟 ）'
        email_body = body_str.format(mail_content_title, mail_content_purpose, mail_content_use, mail_content_msg, mail_content_else, mail_content_date)

        msg = EmailMultiAlternatives(email_title, email_body, EMAIL_HOST_USER, [email_to, ])

        # 消息格式
        msg.content_subtype = 'html'

        # 发送消息
        send_status = msg.send()
        return send_status

    if purpose == 'active':
        # 定制消息
        mail_content_title = '用 户 激 活'
        mail_content_purpose = '用户激活'
        mail_content_use = '您可使用下面链接来激活您的用户'
        mail_content_msg = (SERVER_URL + '/active/' + code)
        mail_content_else = '若您不希望激活您的用户'
        mail_content_date = (str(datetime.datetime.now().year) + '年' + str(datetime.datetime.now().month) + '月' + str(datetime.datetime.now().day) + '日 ' + time.strftime("%H:%M:%S"))

        # 消息内容
        email_title = '[ OPMS ] 用 户 激 活 ！'
        email_body = body_str.format(mail_content_title, mail_content_purpose, mail_content_use, mail_content_msg, mail_content_else, mail_content_date)

        msg = EmailMultiAlternatives(email_title, email_body, EMAIL_HOST_USER, [email_to, ])

        # 消息格式
        msg.content_subtype = 'html'

        # 发送消息
        send_status = msg.send()
        return send_status

    if purpose == 'change_email':
        mail_content_title = '修 改 邮 箱 绑 定'
        mail_content_purpose = '修改邮箱绑定'
        mail_content_use = '您可用下面验证码来修改邮箱'
        mail_content_msg = code
        mail_content_else = '若您不希望修改您的邮箱绑定'
        mail_content_date = (str(datetime.datetime.now().year) + '年' + str(datetime.datetime.now().month) + '月' + str(
        datetime.datetime.now().day) + '日 ' + time.strftime("%H:%M:%S"))

        # 消息内容
        email_title = '[ OPMS ] 修 改 邮 箱 绑 定 ！（ 有效期 5 分钟 ）'
        email_body = body_str.format(mail_content_title, mail_content_purpose, mail_content_use, mail_content_msg,
                                     mail_content_else, mail_content_date)

        msg = EmailMultiAlternatives(email_title, email_body, EMAIL_HOST_USER, [email_to, ])

        # 消息格式
        msg.content_subtype = 'html'

        # 发送消息
        send_status = msg.send()
        return send_status































