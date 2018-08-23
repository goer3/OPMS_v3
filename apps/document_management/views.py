######################################
# Django 模块
######################################
from django.shortcuts import render, HttpResponseRedirect, redirect, reverse, Http404
from django.views import View
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

######################################
# 第三方模块
######################################
from pure_pagination import PageNotAnInteger, Paginator, EmptyPage

######################################
# 系统模块
######################################
import json
import datetime, time
import re

######################################
# 自建模块
######################################
from utils.login_check import LoginStatusCheck
from .forms import *
from .models import *
from operation_record.models import UserOperationRecord


######################################
# 添加文档
######################################
class DocumentAddView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            tags = request.POST.get("tags", "")
            if tags == "":
                return HttpResponse('{"status":"failed", "msg":"标签为必填项！"}', content_type='application/json')

            add_doc_form = AddDocumentForm(request.POST)
            if add_doc_form.is_valid():
                try:
                    if int(request.POST.get("belong")) == 1:
                        title = '文档'
                    else:
                        title = '脚本'

                    doc_obj = Document()
                    doc_obj.subject = request.POST.get("subject")
                    doc_obj.content = request.POST.get("content")
                    doc_obj.belong = int(request.POST.get("belong"))
                    doc_obj.add_user = request.user
                    doc_obj.update_user = request.user
                    doc_obj.status = 1
                    doc_obj.save()

                    tags = request.POST.get('tags')

                    tag_list = tags.split(',')

                    for each in tag_list:
                        if DocumentTags.objects.filter(name=each):
                            # 存在直接加关联
                            tag = DocumentTags.objects.get(name=each)
                            doc_obj.tags.add(tag)
                            doc_obj.save()
                        else:
                            # 不存在添加标签
                            tag_obj = DocumentTags()
                            tag_obj.name = each
                            tag_obj.save()
                            # 加入关联
                            doc_obj.tags.add(tag_obj)
                            doc_obj.save()

                    # 添加操作记录
                    op_record = UserOperationRecord()
                    op_record.op_user = request.user
                    op_record.belong = 4
                    op_record.status = 1
                    op_record.op_num = doc_obj.id
                    op_record.operation = 1
                    op_record.action = "添加%s：%s" % (title, request.POST.get("subject"))
                    op_record.save()
                    return HttpResponse('{"status":"success", "msg":"未知错误！"}', content_type='application/json')
                except Exception as e:
                    return HttpResponse('{"status":"failed", "msg":"未知错误！"}', content_type='application/json')
            else:
                HttpResponse('{"status":"failed", "msg":"填写不合法！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 列表
######################################
class DocumentListView(LoginStatusCheck, View):
    def get(self, request, doc_cate):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'document_management'
            web_chose_left_2 = doc_cate
            docs = Document.objects.filter(status=1).order_by('-update_time')

            # 标签
            user_tag = request.GET.get("tag", "")

            if user_tag != "":
                docs = docs.filter(tags=int(user_tag)).distinct()
                web_chose_middle = 'doc_list'
                title = '文档'
            else:
                # 判断页面
                if doc_cate == 'document':
                    docs = docs.filter(belong=1)
                    web_chose_middle = 'doc_list'
                    title = '文档'
                elif doc_cate == 'script':
                    docs = docs.filter(Q(belong=2) | Q(belong=3) | Q(belong=4) | Q(belong=5))
                    web_chose_middle = 'script_list'
                    title = '脚本'
                else:
                    return HttpResponse(status=404)

            # 用户
            users = UserProfile.objects.all()

            # 判断用户筛选
            check_user = int(request.GET.get('user', '0'))

            if check_user != 0:
                docs = docs.filter(Q(add_user_id=check_user) | Q(update_user_id=check_user))

            # 关键字
            keyword = request.GET.get('keyword', '')
            if keyword != '':
                docs = docs.filter(Q(subject__icontains=keyword) | Q(content__icontains=keyword) | Q(
                    add_user__chinese_name__icontains=keyword) | Q(update_user__chinese_name__icontains=keyword))

            # 记录数量
            doc_nums = docs.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(docs, 16, request=request)

            # 分页处理后的 QuerySet
            docs = p.page(page)

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'docs': docs,
                'users': users,
                'keyword': keyword,
                'doc_nums': doc_nums,
                'check_user': check_user,
                'title': title,
            }
            return render(request, 'document_management/document/doc_list.html', context=context)
        else:
            return HttpResponse(status=403)

######################################
# 文档详情
######################################
class DocumentDetailView(LoginStatusCheck, View):
    def get(self, request, doc_id):
        if request.user.role > 1:
            # 页面选择
            web_chose_left_1 = 'document_management'
            web_chose_left_2 = ''
            web_chose_middle = ''

            doc_info = Document.objects.get(id=int(doc_id))

            if doc_info.belong == 1:
                web_chose_left_2 = 'document'
                doc_cate = 'document'
            else:
                web_chose_left_2 = 'script'
                doc_cate = 'script'

            op_record = UserOperationRecord.objects.filter(belong=4, op_num=int(doc_id)).order_by('-add_time')

            tags = DocumentTags.objects.all()

            context = {
                'web_chose_left_1': web_chose_left_1,
                'web_chose_left_2': web_chose_left_2,
                'web_chose_middle': web_chose_middle,
                'doc_info': doc_info,
                'doc_cate': doc_cate,
                'op_record': op_record,
                'tags': tags,
            }

            return render(request, 'document_management/document/doc_detail.html', context=context)
        else:
            return HttpResponse(status=403)


########################################################################################################################
## CKEDITOR 上传图片
########################################################################################################################
@csrf_protect
def upload_image(request):
    if request.method == 'POST':
        callback = request.GET.get('CKEditorFuncNum')
        try:
            # path 修改上传的路径
            path = "media/ckeditor/image/" + time.strftime("%Y%m%d%H%M%S", time.localtime())
            f = request.FILES["upload"]
            file_name = path + "_" + f.name
            des_origin_f = open(file_name, "wb+")
            # 直接遍历类文件类型就可以生成迭代器了
            for chunk in f:
                des_origin_f.write(chunk)
            des_origin_f.close()
        except Exception as e:
            print(e)
        res = r"<script>window.parent.CKEDITOR.tools.callFunction(" + callback + ",'/" + file_name + "', '');</script>"
        return HttpResponse(res)
    else:
        raise Http404()


######################################
# 编辑文档
######################################
class DocumentEditView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            tags = request.POST.get("tags", "")
            if tags == "":
                return HttpResponse('{"status":"failed", "msg":"标签为必填项！"}', content_type='application/json')

            add_doc_form = AddDocumentForm(request.POST)
            if add_doc_form.is_valid():
                try:
                    doc_id = int(request.POST.get('doc_id'))
                    doc_obj = Document.objects.get(id=doc_id)
                    doc_obj.subject = request.POST.get("subject")
                    doc_obj.content = request.POST.get("content")
                    doc_obj.belong = int(request.POST.get("belong"))
                    doc_obj.update_user = request.user
                    doc_obj.save()

                    if int(request.POST.get("belong")) == 1:
                        title = '文档'
                    else:
                        title = '脚本'

                    # 获取新标签
                    tags = request.POST.get('tags')
                    tag_list = tags.split(',')

                    # 去除旧的标签
                    doc_obj.tags.clear()

                    for each in tag_list:
                        if DocumentTags.objects.filter(name=each):
                            # 存在直接加关联
                            tag = DocumentTags.objects.get(name=each)
                            doc_obj.tags.add(tag)
                            doc_obj.save()
                        else:
                            # 不存在添加标签
                            tag_obj = DocumentTags()
                            tag_obj.name = each
                            tag_obj.save()
                            # 加入关联
                            doc_obj.tags.add(tag_obj)
                            doc_obj.save()

                    # 添加操作记录
                    op_record = UserOperationRecord()
                    op_record.op_user = request.user
                    op_record.belong = 4
                    op_record.status = 1
                    op_record.op_num = doc_obj.id
                    op_record.operation = 2
                    op_record.action = "修改%s：%s" % (title, request.POST.get("subject"))
                    op_record.save()
                    return HttpResponse('{"status":"success", "msg":"修改成功！"}', content_type='application/json')
                except Exception as e:
                    return HttpResponse('{"status":"failed", "msg":"未知错误！"}', content_type='application/json')
            else:
                HttpResponse('{"status":"failed", "msg":"填写不合法！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 删除文档
######################################
class DocumentDeleteView(LoginStatusCheck, View):
    def post(self, request):
        if request.user.role > 1:
            doc_obj = Document.objects.get(id=int(request.POST.get('doc_id')))
            try:
                doc_obj.status = 0
                doc_obj.update_user = request.user
                doc_obj.save()

                if doc_obj.belong == 1:
                    title = '文档'
                else:
                    title = '脚本'

                # 添加操作记录
                op_record = UserOperationRecord()
                op_record.op_user = request.user
                op_record.belong = 4
                op_record.status = 1
                op_record.op_num = doc_obj.id
                op_record.operation = 4
                op_record.action = "删除%s：%s" % (title, doc_obj.subject)
                op_record.save()
                return HttpResponse('{"status":"success", "msg":"删除成功！"}', content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"failed", "msg":"删除失败！"}', content_type='application/json')
        else:
            return HttpResponse(status=403)


######################################
# 下载文档
######################################
class DocumentDownloadView(LoginStatusCheck, View):
    def get(self, request, doc_id):
        if request.user.role > 1:
            doc_info = Document.objects.get(id=int(doc_id))
            time_now = time.strftime("%Y%m%H%M%S", time.localtime())
            filename = doc_info.subject + '_' + time_now

            # 判断文件类型
            if doc_info.belong == 2:
                filename = filename + '.sh'
            elif doc_info.belong == 3:
                filename = filename + '.py'
            elif doc_info.belong == 4:
                filename = filename + '.bat'
            else:
                filename = filename + '.txt'

            # 文件内容获取
            content = doc_info.content
            content_re = re.compile(r'<code .*?>(.*?)</code>', re.S | re.M)
            content = content_re.findall(content)[0]
            content = content.replace("\r\n", '\n')

            # 下载文件
            response = StreamingHttpResponse(content)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment; filename=' + filename.encode('utf-8').decode("ISO-8859-1")
            return response
        else:
            return HttpResponse(status=403)