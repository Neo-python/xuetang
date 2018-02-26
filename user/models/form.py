from django import forms
from django.core import validators


class UserForm(forms.Form):
    user = forms.CharField(label='登入账号', max_length=20, min_length=1,
                           validators=[validators.RegexValidator(regex='^[a-zA-Z0-9_\w]+$', message='包含非法字符')],
                           error_messages={'max_length': '登入账号不能超过20个字符'})
    nickname = forms.CharField(label='昵称', max_length=20, min_length=1, error_messages={'required': '昵称必须填写'},
                               validators=[validators.RegexValidator(regex='^[a-zA-Z0-9_\w]+$', message='包含非法字符')])
    password = forms.CharField(label='密码', min_length=1, max_length=48)
    email = forms.EmailField(label='邮箱', required=False)


class LoginForm(forms.Form):
    user = forms.CharField(label='登入账号', max_length=20, min_length=1,
                           validators=[validators.RegexValidator(regex='^[a-zA-Z0-9_\w]+$', message='包含非法字符')],
                           error_messages={'max_length': '帐号最大长度为20个字符!'})
    password = forms.CharField(label='密码', min_length=1, max_length=48)
