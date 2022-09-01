from datetime import date

from django.core.cache import cache
from django.db.models import Q, F
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView

from blog.models import Category, Post, Tag
from comment.forms import CommentForm
from comment.models import Comment
from config.models import Sidebar


class CommonViewMixin:
    # get_context_data方法的作用：将要展示的数据传递到模板中
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sidebars': Sidebar.get_all(),
        })
        # update() blog应用中模型Category(分类)中的内容
        context.update(Category.get_navs())
        return context


# 定义index页面的处理逻辑
class IndexView(CommonViewMixin, ListView):
    queryset = Post.latest_posts()            # 通过调用blog应用中模型Post(文章)中的latest_posts()方法获得基础的数据集
    paginate_by = 5                           # paginate_by 分页
    context_object_name = 'post_list'             # context_object_name 返回到模板中的数据集名称
    template_name = 'blog/list.html'          # template_name 模板名称


class PostDetailView(CommonViewMixin, DetailView):
    queryset = Post.objects.filter(status=Post.STATUS_NORMAL)\
        .select_related('owner')\
        .select_related('category')           
    template_name = 'blog/detail.html'         
    context_object_name = 'post'               
    pk_url_kwarg = 'post_id'

    # 计算每篇文章的点击次数，从而来计算文章的阅读量
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.handle_visited()
        return response
    
    def handle_visited(self):
        increase_pv = False
        increase_uv = False
        uid = self.request.uid
        pv_key = 'pv:%s:%s' % (uid, self.request.path)
        uv_key = 'uv:%s:%s:%s' % (uid, str(date.today()), self.request.path)
        if not cache.get(pv_key):
            increase_pv = True
            cache.set(pv_key, 1, 1*60)

        if not cache.get(uv_key):
            increase_uv = True
            cache.set(uv_key, 24*60*60)
        
        if increase_pv and increase_uv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv') + 1,
            uv=F('uv') + 1)

        elif increase_pv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv') + 1)

        elif increase_uv:
            Post.objects.filter(pk=self.object.id).update(pv=F('uv') + 1)


class CategoryView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        context.update({
            'category': category,
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category__id=category_id)


class TagView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_id = self.kwargs.get('tag_id')
        tag = get_object_or_404(Tag, pk=tag_id)
        context.update({
            'tag': tag,
        })
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        tag_id = self.kwargs.get('tag_id')
        return queryset.filter(tag__id=tag_id)


# 查找模型Post(文章)
class SearchView(IndexView):
    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'keyword':self.request.GET.get('keyword', '')
        })
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get('keyword')
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword))


# 作者详情页
class AuthorView(IndexView):
    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.kwargs.get('owner_id')
        return queryset.filter(owner_id=author_id)


def show_remark_change_field(request):
    import json
    import datetime
    from django.http import JsonResponse

    field_name = request.POST.get("field_name", "")
    id = int(request.POST.get("id", ""))
    field_value = request.POST.get("field_value", "")
    result = {"code": 0}

    try:
        if field_name == "remark":
            current_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
            create_man = request.user.username
            obj = Category.objects.get(id=id)
            if obj.remark:
                remark = json.loads(obj.remark) 
                remark[current_time] = {"name": create_man, "content": field_value}
            else:
                remark = {current_time: {"name": create_man, "content": field_value}}
            remark = json.dumps(remark, ensure_ascii=False)
            obj.remark = remark
            obj.save()
            result["code"] = 0
            result["msg"] = "备注成功！"

        else:
            result["code"] = 1
            result["msg"] = "未识别的字段!"
    except Exception as ex:
        result["code"] = 1
        result["msg"] = str(ex)
    return JsonResponse(result)


def show_status(request):
    from blog.models import Category
    from django.http import JsonResponse
    
    id = request.POST.get("id", "")
    status = request.POST.get("change_status", "")
    result = {"msg": "", "code": 200}
    qs = Category.objects.get(id=id)
    if status:
        qs.status = int(status)
        qs.save()
        result["msg"] = "保存成功！"
        result["code"] = 200
    else:
        result["msg"] = "未保存成功！"
        result["code"] = 400
    return JsonResponse(result)


# def login(request):
#     from django.shortcuts import redirect
#     from django.http import JsonResponse
#
#     login = request.POST.get("login_path", "")
#     print("login:", login)
#     result = {"code": 200, "msg": ""}
#     if login:
#         return JsonResponse(result)
#     else:
#         result["code"] = 404
#         result["msg"] = "接口重定向错误！"
#         return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


