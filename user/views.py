from django.shortcuts import render, reverse, Http404, HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import Count
from xuetang.config import DOMAIN_NAME
from xuetang.views import get_verification
from xuetang.plug_ins import ip_defense, get_user, judgment_code, send_mail, generate_code, save_img
from .plug_ins import verify_login, verification_field, write_cookie, is_self
from topic.plug_ins import get_paginator
from .models.form import UserForm, LoginForm
from .models.model import Defense, User, Cookie, Message
from topic.models.model import Topic


# Create your views here.

def login(request):
    """
    接收登录请求,验证.
    登录成功:将用户信息写入session.
            用户勾选remember则生成cookie:sid信息返回前台,在前台完成cookie写入.
    失败:通知前台,登录失败.
    :param request:
    :return:status,url,sid,error.
    """
    user = request.POST.get('user', None)
    password = request.POST.get('password', None)
    remember = request.POST.get('remember', None)
    href = request.POST.get('href', None)
    f = LoginForm({'user': user, 'password': password})
    response = {'status': 'no', 'error': '帐号密码错误'}
    if f.is_valid():
        if verify_login(request, user, password):
            response.update({
                'status': 'ok',
                'url': href
            })
            if remember is not None and remember == 'true':
                response.update({'sid': write_cookie(user)})
    return JsonResponse(response)


def logout(request):
    """
    用户登出,删除session,删除cookie
    :param request:
    :return: 跳转到不需要登录状态的首页
    """
    user = request.session.get('user', None)
    if user:
        request.session.pop('user')
        c = Cookie.objects.filter(user=user['user']).first()
        if c:
            c.delete()
    return HttpResponseRedirect(reverse('home'))


@ip_defense(refresh_hour=24, frequency=30)
def registered(request):
    """
    验证注册表单,不符合条件则收集错误信息,反馈给前台用户.
    每次注册,修改ip_defense各项数值.超过一定数值,则不再继续处理注册请求.
    :param request:
    :return: 注册成功,更新session,跳转页面. 注册失败,更新验证码,返回json数据.
    """

    # error存储所有错误信息,以{field:message}结构存储. respond 存储反馈信息:status,url,src,interval,error....
    error = {}
    respond = {}

    # 获取表单信息 弹出多余的cs_token 获取form对象,以便写入数据库. verification:获取验证码结果. defense:获取ip记录
    form = request.POST.dict()
    form.pop('csrfmiddlewaretoken')
    f = UserForm(form)
    verification = form.pop('verification', None) == request.session['code']
    defense = Defense.objects.filter(user_ip=request.META['REMOTE_ADDR'], func_name='registered').first()

    # 遍历所有字段,发现任何字段非唯一,将该字段错误信息写入error.最终返回验证结果unique
    unique = verification_field(User, ['user', 'nickname', 'email'], form, error)

    if f.is_valid() and verification and unique:
        # 修改defense,在防御有效期后,才可再次注册帐号.
        defense.status = False
        defense.save()
        # 响应前台,通知注册结果.
        respond['status'] = 'ok'
        respond['url'] = reverse('home')
        # ?未完成
        # 将数据存入数据库,并且修改登录状态session
        if not len(form['email']):
            form['email'] = None
        user = User(**form)
        user.registered()

    else:
        # frequency:注册次数 interval:间隔时间(单位:second)
        defense.frequency += 1
        defense.interval += 1
        defense.save()

        # 更新验证码
        get_verification(request)

        # 响应前台,通知注册结果,更新验证码src
        respond['status'] = 'no'
        respond['src'] = request.session['file_path']

        # forms.errors返回的数据结构复杂,处理后以{field:message}结构返回前台,并告知前台等待间隔时间.
        for i in f.errors.as_data().items():
            error.update({i[0]: i[1][0].messages[0]})
        respond['error'] = error
        respond['interval'] = defense.interval
        if not verification:
            respond['error'].update({'verification': '验证码错误'})
    return JsonResponse(respond)


def user_index(request, user_nickname):
    """
    用户个人主页
    :param request:
    :param user_nickname:
    :return:
    """
    # user:访问的是user的主页
    user = User.objects.filter(nickname=user_nickname).first()
    # collect:请求查看收藏夹
    # 以collect请求与is_self共同判断是否展示收藏夹.
    collect = eval(request.GET.get('collect', 'False'))
    self = is_self(request, user)
    if collect and self:
        topics = [i.topic_id for i in user.collections.all()]
    else:
        # 如果不为本人浏览主页
        topics = Topic.objects.filter(user_id=user.user, status=True, delete_status=False).all()
        collect = False
    page = int(request.GET.get('page', 1))

    topic, paginator, page_list = get_paginator(page, topics, per_page=20)
    # collect:前台判断topic是否属于收藏,与收藏按钮的状态变动.
    content = {
        'title': user_nickname,
        'user': user,
        'topics': topic,
        'page': page,
        'paginator': paginator,
        'page_list': page_list,
        'collect': collect,
        'home_page': True
    }
    return render(request, template_name='user/index.html', context=content)


def settings(request):
    """
    个人帐号设置界面
    :param request:
    :return:
    """
    user = get_user(request)
    content = {
        'title': '账号设置',
        'user': user
    }
    return render(request, template_name='user/settings.html', context=content)


def bind_email(request):
    """
    绑定邮箱
    message:前台提示绑定结果信息.
    :param request:
    :return:
    """
    user = get_user(request)
    # 当用户已绑定邮箱的情况下,返回邮箱已绑定信息.
    if user.email:
        return HttpResponseRedirect(reverse('user:settings') + '?message=bind-email-Already')
    else:
        email = request.POST.get('email')
        code = request.POST.get('Vcode')

        # 当Vcode创建时间大于5分钟前的时间则Vcode为有效,否则即为无效.
        v = judgment_code(user_user=user.user, code=code, period_of_validity=5)
        # 如果user与code匹配,并且Vcode为有效,则表明验证通过.进行邮箱绑定.
        if v:
            user.email = email
            user.save()
            message = '?message=bind-email-success'
            # 验证成功立即删除Vcode
            v.delete()
        else:
            message = '?message=code-error'
        return HttpResponseRedirect(reverse('user:settings') + message)


def modify_password(request):
    """
    修改密码,需要登入权限
    :param request:
    :return:
    """
    # 获取用户实例
    user = get_user(request)
    password = request.POST.get('password')
    password_repeat = request.POST.get('password_repeat')
    # 先判断两次密码是否一致,不一致直接返回错误消息 or 密码不符合LoginForm验证条件
    if password != password_repeat or not LoginForm({'user': user.user, 'password': password}).is_valid():
        return HttpResponseRedirect(reverse('user:settings') + '?message=password_repeatInconsistent')

    code = request.POST.get('Vcode')
    # code与有效期都符合条件judgment返回v实例,否则返回None
    v = judgment_code(user_user=user.user, code=code, period_of_validity=5)
    if v:
        # 修改密码,registered()方法将密码加密并且保存数据.最后删除v实例,使code失效.
        user.password = password
        user.registered()
        v.delete()
        # 密码修改成功,退出登录.
        return HttpResponseRedirect(reverse('user:logout'))
    else:
        # code错误或code已失效,在前台给出错误提示.
        return HttpResponseRedirect(reverse('user:settings') + '?message=code-error')


def modify_personal_information(request):
    """
    修改个人信息:头像与签名.
    :param request:
    :return:
    """
    user = get_user(request)
    file = request.FILES.get('avatar')
    # 如果存在file,and表达式才会继续判断.先判断尺寸是否大于2M再判断后缀是否合法.
    if file and file.size < 2 * 1024 ** 2:
        suffix = file.name.split('.')[1].lower()
        if suffix in ['jpg', 'png']:
            d = save_img(file, filename=f'{user.nickname}.{suffix}', folder='avatar/')
            # 头像路以static开头而不是/static,和FileField字段的upload_to函数行为保持一致.
            user.avatar = d['src'][1:]
    # 获取签名的值.
    try:
        signature = request.POST.get('signature', '')
        user.signature = signature
        user.save()
    except:
        raise Http404('签名过长,最大长度为48个字符.')
    return HttpResponseRedirect(reverse('user:settings'))


def application_reset_password(request):
    """
    申请重置密码界面与发送唯一验证码code.
    :param request:
    :return:
    """
    content = {
        'title': '密码找回'
    }
    if request.method == 'GET':
        return render(request, template_name='user/application_reset.html', context=content)
    else:
        userID = request.POST.get('user')
        u = User.objects.filter(user=userID).first()
        # 如果用户存在并且用户已绑定邮箱,生成200位长度的唯一验证码至用户邮箱.
        if u and u.email:
            # 生成验证码
            code = generate_code(user=u.user, length=200)
            # 生成信息
            message = f"你正在申请重置密码:\n点击链接进行密码重置,链接有效期为5分钟.\n" \
                      f"{DOMAIN_NAME + reverse('user:reset_password',args=[code,])}  " \
                      f"\n 如非你本人操作，请忽略此邮件。"
            # 发送邮件
            send_mail(to_addr=u.email, message=message)
            return HttpResponseRedirect(reverse('user:application_reset_password') + '?message=ResetLinksHasBeenSent')
        else:
            return HttpResponseRedirect(reverse('user:application_reset_password') + '?message=userDoesNotExist')


def reset_password(request, code):
    """
    重置密码界面与修改密码操作.
    :param request:
    :param code: 唯一验证码,有效期5分钟.
    :return:
    """
    content = {
        'title': '重置密码',
        'code': code
    }
    # GET请求跳转重置界面
    if request.method == 'GET':
        return render(request, template_name='user/reset_password.html', context=content)
    else:
        password = request.POST.get('password')
        password_repeat = request.POST.get('password_repeat')
        f = LoginForm({'user': 'repeat', 'password': password})

        # 验证密码是否符合规范与两次密码是否一致
        if f.is_valid() and password == password_repeat:
            v = judgment_code(user_user=None, code=code, period_of_validity=5)
            if v:
                # 通过v找到用户实例, 修改用户密码, 加密密码并且保存.
                user = User.objects.filter(user=v.user).first()
                user.password = password
                user.registered()
                # 删除code的实例v
                v.delete()
                return HttpResponseRedirect(reverse('home') + '?message=ResetPasswordSuccess')
            else:
                # 前台错误消息提示
                content.update({'error': '重置失败,请检查链接有效期.'})
        else:
            # 前台错误消息提示
            content.update({'error': '重置失败,请检查密码是否符合规范.'})
        return render(request, template_name='user/reset_password.html', context=content)


def leave_message(request):
    """
    接收留言请求视图, 此视图需要登入权限装饰器.
    :param request:
    :return:
    """
    to_user = request.POST.get('to_user')
    to_user = User.objects.filter(nickname=to_user).first()
    # 判断接受留言用户是否存在
    if to_user:
        # 获取留言内容, 获取留言用户实例.
        content = request.POST.get('content')
        user = get_user(request)
        # 写入留言 并保存
        m = Message(sender=user, addressee=to_user, content=content, types='message')
        m.save()
        # 如果存在type,那么请求为ajax.返回状态码与用户头像与昵称.
        if request.POST.get('type'):
            n = m.sender.nickname
            a = m.sender.avatar.__str__()
            return JsonResponse({'status': 'ok', 'data': {'avatar': a, 'name': n}})
        return HttpResponseRedirect(reverse('user:user_index', args=[to_user.nickname]))
    else:
        return Http404


def mailbox(request):
    """
    获取聊天记录与未读消息数量,不要具体内容.
    :param request:
    :return: 信箱页
    """
    self = get_user(request)
    contacts = Message.objects.values('addressee', 'sender', 'sender__avatar', 'sender__nickname').filter(
        addressee=self, addressee_status=False).annotate(count=Count('status'))
    content = {
        'title': '信箱',
        'contacts': contacts
    }

    return render(request, template_name='user/mailbox.html', context=content)


def get_message(request):
    """
    按需,获取对话记录.
    other_side: 对方.
    :param request:
    :return:返回状态码\对话集\下次请求数
    """
    # count:消息按需请求,当前请求次数.
    count = int(request.GET.get('count'))

    # self:当前用户id,other_side:对方用户
    self = get_user(request)
    other_side = User.objects.filter(nickname=request.GET.get('other_side')).first()

    other_side_message = Message.objects.filter(sender_id=other_side, addressee=self)

    # 将对方发送的消息状态更新为已阅读
    other_side_message.update(status=True)
    reply = Message.objects.filter(sender=self, addressee_id=other_side)

    # 将对方发送消息与自己发送的消息合并
    messages = other_side_message | reply

    # 按id顺序倒序,等于按发送时间倒序
    messages = messages.order_by('-id').values('sender__nickname', 'sender__avatar', 'content', 'create_time')
    # 取出按需请求次数的指定范围
    m = list(messages[count * 10 - 10:count * 10])
    # 将datetime类型转为str类型,并格式化.
    for i in m:
        i['create_time'] = i['create_time'].strftime('%Y-%m-%d %H:%M')
    # 前台显示需要反转
    m.reverse()
    # 如果后面还有消息,告诉前台还可以再次请求,否则设置count为小于0的数字,告诉前台后面没有消息了,不可再次请求.
    if len(messages[count * 10:count * 10 + 10]):
        count += 1
    else:
        count = -1
    return JsonResponse({'status': 'ok', 'messages': m, 'count': count})


def del_message(request):
    """
    修改删除状态为True,因为记录是双向的,所以以此方法做消息删除.
    :param request:
    :return:
    """
    self = get_user(request)
    nickname = request.GET.get('del_nickname')
    Message.objects.filter(sender__nickname=nickname, addressee=self, addressee_status=False).update(
        addressee_status=True)
    Message.objects.filter(sender=self, addressee__nickname=nickname, sender_status=False).update(sender_status=True)
    return JsonResponse({'status': 'ok'})
