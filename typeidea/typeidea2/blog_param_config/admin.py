from django.contrib import admin

from blog_param_config.models import blog_param_config


@admin.register(blog_param_config)
class BlogParamConfigAdmin(admin.ModelAdmin):
    list_display = ['Type', 'TypeDesc', 'TypeName', 'Seq', 'V', 'VDesc', 'UpdateTime']
    ordering = ['id']
