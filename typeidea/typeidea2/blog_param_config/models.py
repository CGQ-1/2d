from django.db import models


class blog_param_config(models.Model):
    Type = models.CharField(u'参数类型', max_length=12, blank=True, null=True, help_text='数字类型编码, 相同的编码表示为统一类型')
    TypeDesc = models.CharField(u'参数类型描述', max_length=32, blank=True, null=True, help_text='一般为英文解释, 表示这一类型的属性')
    TypeName = models.CharField(u'参数类型名称', max_length=32, blank=True, null=True, help_text='一般为中文描述, 表示这一类型的用途')
    Seq = models.IntegerField(u'参数序号', blank=True, null=True, help_text='无实际意义,一般用来排序')
    V = models.CharField(u'参数值', max_length=255, blank=True, null=True, help_text='填写你需要的值,比如类型,姓名等')
    VDesc = models.TextField(u'参数值描述', blank=True, null=True, help_text='填写对你需要值的补充，可以和参数值相同，也可以不同')
    UpdateTime = models.DateTimeField(u'更新时间', auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = u'系统参数配置'
        verbose_name_plural = u'系统参数配置'
        ordering = ['Type', 'Seq']

    def __str__(self):
        return self.Type