from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from blog.views import CommonViewMixin
from .models import Link


class LinkListView(CommonViewMixin, ListView):
    queryset = Link.objects.filter(status=Link.STATUS_NORMAL)
    template_name = 'config/links.html'
    context_object_name = 'link_list'


@csrf_exempt
def page_not_found(request, exception):
    data = {"msg": "页面不存在", "status": 404}
    return render(request, "error/404.html", context=data)
