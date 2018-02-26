"""xuetang URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from xuetang.views import home, upload, get_verification, send_code

urlpatterns = [
    path("user/", include("user.urls")),
    path('topic/', include('topic.urls')),
    path('audit/', include('audit.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('admin/', admin.site.urls),
    path('', view=home, name="home"),
    path('home/', view=home, name="home"),
    path('upload/', view=upload, name='upload'),
    path("get_verification/", view=get_verification, name='get_verification'),
    path('send_code/', view=send_code, name='send_code')
]
