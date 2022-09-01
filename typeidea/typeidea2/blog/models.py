import mistune

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils.functional import cached_property


class Category(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(u'书类名', max_length=50, default='', null=True)
    status = models.PositiveIntegerField(u'状态', default=STATUS_NORMAL, choices=STATUS_ITEMS, null=True)
    is_nav = models.BooleanField(u'是否为导航', default=False, null=True)
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE, null=True)
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    remark = models.CharField(u'备注信息', max_length=125, default='', null=True)

    class Meta:
        verbose_name = verbose_name_plural = '分类'

    def __str__(self):
        return self.name

    @classmethod
    def get_navs(cls):
        categories = cls.objects.filter(status=cls.STATUS_NORMAL)
        nav_categories = []
        normal_categories = []
        for cate in categories:
            if cate.is_nav:
                nav_categories.append(cate)
            else:
                normal_categories.append(cate)
      
        return {
            'navs': nav_categories,
            'categories': normal_categories,
        }
    

class Tag(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(u'标签名', max_length=50, default='', null=True)
    status = models.PositiveIntegerField(u'状态', default=STATUS_NORMAL, choices=STATUS_ITEMS, null=True)
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE, null=True)
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name = verbose_name_plural = '标签'

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_DRAFT, '草稿'),
    )

    title = models.CharField(u'标题', max_length=225, default='', null=True)
    desc = models.CharField(u'摘要', max_length=1024, default='', null=True)
    content = models.TextField(verbose_name="正文", help_text="正文必须是MarkDown格式", default='', null=True)
    content_html = models.TextField(u'正文html代码', blank=True, editable=False)
    status = models.PositiveIntegerField(u'状态', default=STATUS_NORMAL, choices=STATUS_ITEMS, null=True)
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag, u'标签')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    is_md = models.BooleanField(u'markdown语法', default=False)
    pv = models.PositiveIntegerField(default=1)
    uv = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = verbose_name_plural = "文章"
        ordering = ['-id'] 
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.is_md:
            self.content_html = mistune.markdown(self.content)
        else:
            self.content_html = self.content
        super().save(*args, **kwargs)

    @cached_property
    def tags(self):
        return ','.join(self.tag.values_list('name', flat=True))

    @staticmethod
    def get_by_tag(tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            tag = None
            post_list = []
        else:
            post_list = tag.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')
        
        return post_list, tag
    
    @staticmethod
    def get_by_category(category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            category = None
            post_list = []
        else:
            post_list = category.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')
        return post_list, category
    
    # 利用filter获取status=cls.STATUS_NORMAL的Post(文章), 并返回queryset
    @classmethod
    def latest_posts(cls):
        queryset = cls.objects.filter(status=cls.STATUS_NORMAL)
        return queryset
    
    # 获取blog应用中模型Post(文章)中的最热文章
    @classmethod
    def hot_posts(cls):
        result = cache.get('hot_posts')
        if not result:
            result = cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-pv')
            cache.set('hot_posts', result, 10 * 60)
        return result
    