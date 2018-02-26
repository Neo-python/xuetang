from django.contrib import admin
from .models.model import User, Defense


# Register your models here.
# 注册model到后台admin管理界面
admin.site.register(User)
admin.site.register(Defense)
