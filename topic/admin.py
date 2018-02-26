from django.contrib import admin
from topic.models import *


# Register your models here.

class TopicAdmin(admin.ModelAdmin):
    # 显示字段列表
    list_display = ('title', 'area_id', 'user_id', 'status', 'delete_status')
    # 显示链接字段,外键无效
    list_display_links = ('title',)
    # 允许修改字段,外键无效
    list_editable = ('area_id', 'status')
    # 可以筛选字段
    list_filter = ('area_id', 'status', 'delete_status')
    # 每页数据量
    list_per_page = 20
    # 排序字段
    ordering = ('status',)
    # 搜索字段
    search_fields = ('title',)

    # 针对编辑页面
    fields = (
        ('title', 'area_id', 'user'),
        'content',
        ('status',
         'fold_status',
         'solve_status',
         'like',
         'contra',
         'readings'),
        ('create_time', 'modify_time')
    )
    # 编辑页只读字段
    readonly_fields = ('create_time', 'modify_time', 'like', 'contra', 'readings')

    def status_true(self, request, setobj):
        setobj.update(status=True)

    status_true.short_description = '审核通过'

    def status_false(self, request, queryset):
        queryset.update(status=False)

    status_false.short_description = '取消显示状态'
    actions = ('status_true', 'status_false')

    class Media:
        js = (
            '/static/tinymce/js/tinymce/tinymce.min.js',

        )


admin.site.register(Topic, TopicAdmin)
admin.site.register(Area)
admin.site.register(Tag)
