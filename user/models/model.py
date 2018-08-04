from django.db import models
from hashlib import sha1
import os


def upload_to(instance, filename):
    """
    因为昵称不可重复,因此作为头像名,存入/static/img/avatar文件夹内.
    :param instance:用户实例
    :param filename:文件名
    :return:
    """

    # legal_type 合法文件类型
    legal_type = ['jpg', 'png']
    # 当头像文件类型不在规定范围内时,返回False不做任何操作.
    suffix = filename.split('.')[1]
    if suffix not in legal_type:
        return False
    # 找到之前保存的头像,删除,跳出循环.
    for i in legal_type:
        old_path = f'./static/img/avatar/{instance.nickname}.{i}'
        if os.path.exists(old_path):
            os.remove(old_path)
            break
    filename = instance.nickname + '.' + suffix
    path = '/'.join(['static/img/avatar', filename])
    return path.replace('\\', '/')


class User(models.Model):
    user = models.CharField(verbose_name='帐号名', max_length=20, unique=True)
    nickname = models.CharField(verbose_name='昵称', max_length=10, unique=True)
    password = models.CharField(verbose_name='密码', max_length=48)
    avatar = models.FileField(verbose_name='用户头像', upload_to=upload_to,
                              default="static/img/default_avatar.jpg")
    signature = models.CharField(verbose_name='个性签名', max_length=48, default='')
    level = models.IntegerField(verbose_name='权限等级', default=0)
    email = models.EmailField(verbose_name='邮箱', max_length=50, null=True,
                              unique=True)
    phone = models.CharField(verbose_name='手机号', max_length=12)
    integral = models.IntegerField(verbose_name='积分', default=10)
    status = models.BooleanField(verbose_name='激活状态', default=False)
    create_time = models.DateTimeField(verbose_name='注册时间', auto_now_add=True)
    login_time = models.DateTimeField(verbose_name='登录时间', auto_now=True)

    # 继承models.Model基类,自定义save方法,再继承基类save方法.完成功能添加.
    # 添加自动加密password字段功能

    def registered(self, *args, **kwargs):
        self.password = sha1((self.password + self.user).encode('utf-8')).hexdigest()
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} -- {self.nickname} -- {self.status}'


class Blacklist(models.Model):
    # 黑名单记录表
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, to_field='user', related_name='b_user',
                             verbose_name='用户')
    to_user = models.ForeignKey(to=User, on_delete=models.CASCADE, to_field='user', related_name='b_to_user',
                                verbose_name='被拉黑用户')

    def __str__(self):
        return f'{self.user.user}->{self.to_user.user}'


class Defense(models.Model):
    # ip防御数据记录
    user_ip = models.CharField(verbose_name='ip地址', max_length=48)
    func_name = models.CharField(verbose_name='函数名', max_length=48)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_time = models.DateTimeField(verbose_name='最后记录时间', auto_now=True)
    interval = models.IntegerField(verbose_name='间隔时间,秒数', default=1)
    frequency = models.IntegerField(verbose_name='记录次数', default=0)
    status = models.BooleanField(verbose_name='状态', default=True)

    def __str__(self):
        return f'ip:{self.user_ip} interval:{self.interval} frequency:{self.frequency}'


class Cookie(models.Model):
    # cookie的sid数据库
    sid = models.CharField(verbose_name='cookie_sid', max_length=48)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, to_field='user', verbose_name='user',
                             related_name='cookie_sid')

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return f'user:{self.user} create_time:{self.create_time}'


class Message(models.Model):
    # 消息存储表
    sender = models.ForeignKey(to=User, on_delete=models.CASCADE, to_field='user', related_name='m_user',
                               verbose_name='发送人')
    addressee = models.ForeignKey(to=User, on_delete=models.CASCADE, to_field='user', related_name='m_to_user',
                                  verbose_name='接收人')
    content = models.TextField(verbose_name='消息内容')
    types = models.CharField(verbose_name='消息类型', max_length=10)
    types_id = models.IntegerField(verbose_name='类型所属表主键', null=True)
    status = models.BooleanField(verbose_name='阅读状态', default=False)
    sender_status = models.BooleanField(verbose_name='发送人删除状态', default=False)
    addressee_status = models.BooleanField(verbose_name='收件人删除状态', default=False)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.sender.user}->{self.addressee.user}'


class VerificationCode(models.Model):
    user = models.CharField(verbose_name='用户帐号', max_length=20, unique=True)
    code = models.CharField(verbose_name='验证码', max_length=200, unique=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.user}  {self.code}'
