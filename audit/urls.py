from django.urls import path
from audit.views import index, topic, process, comment, tag, tag_modify, audit_message

app_name = 'audit'

urlpatterns = [
    path('index/', view=index, name='index'),
    path('topic/', view=topic, name='topic'),
    path('comment/', view=comment, name='comment'),
    path('tag/', view=tag, name='tag'),
    path('process/', view=process, name='process'),
    path('tag_modify/', view=tag_modify, name='tag_modify'),
    path('audit_message/', view=audit_message, name='message')
]
