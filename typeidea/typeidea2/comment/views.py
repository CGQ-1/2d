from django.shortcuts import redirect
from django.views.generic import TemplateView

from comment.models import Comment
from comment.forms import CommentForm


# 实现评论功能
class CommentView(TemplateView):
    http_method_names = ['post']              
    template_name = 'comment/result.html'

    def post(self, request):
        comment_form = CommentForm(request.POST)
        target = request.POST.get('target')
        if comment_form.is_valid():
            instance = comment_form.save(commit=False)  # 保存表单内容
            instance.target = target                    # 保存评论对象
            instance.save()
            # succeed = True
            return redirect(target)
        else: 
            succeed = False

        context = {
            'succeed': succeed,
            'form': comment_form,
            'target': target,
        }
        return self.render_to_response(context)


def show_form(request):
    from django.contrib import messages
    from django.http import HttpResponse, JsonResponse
    from django.shortcuts import render

    form_method = request.method
    result = {"code": 200, "msg": ""}

    try:
        if form_method == "GET":
            url = request.get_full_path()
            target = url.split("?")[1]
            # print(target)
            result["target"] = target
            result["msg"] = "GET请求方式"
            result["code"] = 200
            return render(request, "comment/block.html", context=result)
        elif form_method == "POST":    
            target = request.POST.get("target", "")
            nickname = request.POST.get("nickname", "")
            # email = request.POST.get("email", "")
            # website = request.POST.get("website", "")
            content = request.POST.get("content", "")
            # print(target, nickname, email, website, content)
            comment_obj = Comment.objects.create(target=target, nickname=nickname, content=content)
            result["code"] = 200
            result["msg"] = "评论提交成功！"
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        else:
            return HttpResponse("请选择GET或者POST请求方式！")
    except Exception as e:
        return HttpResponse(messages.error(request, "错误原因：{}".format(e)))
