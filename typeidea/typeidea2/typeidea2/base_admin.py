from django.contrib import admin
from blog_param_config.models import blog_param_config

from typeidea2.magic_number import BlogParamConfig


class BaseOwnerAdmin(admin.ModelAdmin):
    # 抽象出一个基类
    # 重写save()方法, 将owner = request.user, 获取当前user名为作者名
    # 重写get_queryset方法
    exclude = ('owner', )

    def get_queryset(self, request):
        qs = super(BaseOwnerAdmin, self).get_queryset(request)
        user_name = request.user.username

        user_name_list = list(blog_param_config.objects.filter(Type=BlogParamConfig.Blog_Param_Config_1.value).values_list("V", flat=True))

        if user_name in user_name_list:
            pass
        else:
            qs = qs.filter(owner=request.user)
        return qs
    
    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(BaseOwnerAdmin, self).save_model(request, obj, form, change)
