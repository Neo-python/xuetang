from hashlib import sha1
from .models.model import User, Cookie
import datetime


def verify_login(request, user, password):
    """验证帐号,将账号信息写入session['user]
    :param request:
    :param user:
    :param password:
    :return: 返回验证登录结果
    """
    u = User.objects.filter(user=user, password=sha1((password + user).encode('utf-8')).hexdigest()).first()
    if u:
        d = u.__dict__
        d.pop("_state")
        # 将时间类型数据转为字符串
        for k, v in d.items():
            if k[-4:] == 'time':
                d[k] = str(v)
        request.session['user'] = d

        return True
    else:
        return False


def verification_field(model, unique_field, form, error):
    """排查选定字段,判断唯一性.返回错误字段信息.
    :param model: 查询的模型
    :param unique_field: 需要排查唯一性的字段
    :param form: 用户提交的数据
    :param error: 错误信息{field:message}
    :return: 返回True或False
    """
    fields = []
    unique = True
    # 筛选出用户未填写的字段,不做唯一性排查
    for k in unique_field:
        if len(form[k]):
            fields.append({k: form[k]})
    # 从筛选出的字段集合依次搜索每个字段
    for field in fields:
        u = model.objects.filter(**field).first()
        if u:
            field_name = field.popitem()[0]
            error.update({field_name: u._meta.get_field(field_name).verbose_name + '已存在'})
            unique = False
    return unique


def write_cookie(user):
    """写入cookie到数据库.
    :param user: 用户登录帐号与当前时间相连后再加密
    :return:返回sid 供写入cookie使用
    """
    now = datetime.datetime.now()
    sid = sha1((user + str(now)).encode('utf-8')).hexdigest()
    c = Cookie.objects.filter(user=user).first()
    if c:
        c.sid = sid
    else:
        c = Cookie(sid=sid, user_id=user)
    c.save()
    return sid


def is_self(request, user):
    self = request.session.get('user')
    if not self:
        return True
    self_user = self.get('user')
    return self_user == user.user
