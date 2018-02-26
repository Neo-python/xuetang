from django.urls import path
from user.views import registered, login, logout, user_index, leave_message, mailbox, get_message, del_message, \
    settings, bind_email, modify_password, application_reset_password, reset_password, modify_personal_information

app_name = 'user'
urlpatterns = [
    path("registered/", view=registered, name='registered'),
    path('login/', view=login, name='login'),
    path('logout/', view=logout, name='logout'),
    path('user_index/<user_nickname>/', view=user_index, name='user_index'),
    path('leave_message/', view=leave_message, name='leave_message'),
    path('mailbox/', view=mailbox, name='mailbox'),
    path('get_message/', view=get_message, name='get_message'),
    path('del_message/', view=del_message, name='del_message'),
    path('settings/', view=settings, name='settings'),
    path('settings/bind_email/', view=bind_email, name='bind_email'),
    path('settings/modify_password/', view=modify_password, name='modify_password'),
    path('settings/modify_personal_information/', view=modify_personal_information, name='modify_personal_information'),
    path('reset_password/application', view=application_reset_password, name='application_reset_password'),
    path('reset_password/<code>', view=reset_password, name='reset_password')
]
