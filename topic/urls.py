from django.urls import path
from topic.views import release, topic_index, discuss, comment, get_reply, collection, comment_loc, topic_loc, \
    search_topic, modify

app_name = 'topic'

urlpatterns = [
    path('release/', view=release, name='release'),
    path('modify/', view=modify, name='modify'),
    path('area/<area>/', view=topic_index, name='topic_index'),
    path('search/', view=search_topic, name='search_topic'),
    path('discuss/<topic_id>/', view=discuss, name='discuss'),
    path('comment/<topic_id>/add', view=comment, name='comment'),
    path('get_reply/', view=get_reply, name='get_reply'),
    path('collection/', view=collection, name='collection'),
    path('comment_loc/', view=comment_loc, name='comment_loc'),
    path('topic_loc/', view=topic_loc, name='topic_loc'),
]
