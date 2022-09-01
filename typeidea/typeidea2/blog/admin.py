from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin

from django.urls import reverse
from django.utils.html import format_html

from .adminforms import PostAdminForm
from .models import Post, Category, Tag
from typeidea2.base_admin import BaseOwnerAdmin
from typeidea2.custom_site import custom_site
import json
from django.utils.safestring import mark_safe
from django.template import loader

admin.site.site_header = '博客管理系统'
admin.site.index_title = '博客管理系统'
admin.site.site_title = '博客管理系统'


class PostInline(admin.TabularInline):
    fields = ('title', 'desc')
    extra = 1
    model = Post
    

@admin.register(Category)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline, ]
    list_display = ('name', 'show_status', 'is_nav', 'created_time', 'owner', 'post_count', 'show_remark')
    fields = ('name', 'status', 'is_nav')
    ordering = ['id']

    def show_status(self, obj):
        func_name = "show_status"
        id = obj.id
        status_num = obj.status
        if status_num:
            status = "正常"
        else:
            status = "删除"
        return mark_safe(loader.render_to_string('blog/show_status_js.html', locals()))
    show_status.short_description = '状态'
    
    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = '文章数量'

    def show_remark(self, obj):
        func_name = "show_remark"
        id = obj.id
        remark = json.loads(obj.remark) if obj.remark else ""
        return mark_safe(loader.render_to_string('blog/show_remark_js.html', locals()))
    show_remark.short_description = '备注信息'


@admin.register(Tag)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time', 'owner')
    fields = ('name', 'status')


# 设置分类过滤器
class CategoryOwnerFilter(admin.SimpleListFilter):
    title = '分类过滤器'
    parameter_name = 'owner_category'

    # 在分类中筛选出当前作者的文章
    def lookups(self, request, model_name):
        # 从Category表中找出以当前用户为作者的 分类id 和 分类name
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    # 筛选出queryset
    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset
    

@admin.register(Post)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm                       # 自定义Post(文章)下的form表单
    list_display = [
        'title', 'category', 'status',
        'created_time', 'owner', 'operator'
    ]
    
    list_filter = [CategoryOwnerFilter]
    search_fields = ['title', 'category__name']

    actions_on_top = True                      
    actions_on_bottom = True

    save_on_top = True

    exclude = ['owner']

    # fields和fieldsets只能存在一个
    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (
                ('title', 'category'),
                'status',
            ),
        }),

        ('内容信息', {
            'fields': (
                'desc',
                'content',
            ),
        }),

        ('额外信息', {
            'classes': ('collapse',),
            'fields': ('tag',),
        }),
    )

  
    # 用来显示多对多字段展示的配置 filter_horizontal
    filter_vertical = ('tag', )             

    # 添加"编辑"按钮，可以对每个Post(文章)对象进行"编辑"操作
    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            # reverse方式获取后台地址,
            reverse('admin:blog_post_change', args=(obj.id, ))
        )
    operator.short_description = '操作'


    


