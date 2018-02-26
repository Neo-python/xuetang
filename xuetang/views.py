from django.shortcuts import render
from django.http import JsonResponse
from .plug_ins import save_img, verification_code, get_user, send_mail, generate_code
from xuetang.settings import IMG_DIRS
import datetime
import os


def home(request):
    content = {
        'title': '首页',
        'area': '首页'
    }
    return render(request, template_name="index.html", context=content)


def upload(request):
    """
    按日期分文件夹,避免所有图片挤在一起产生冲突,未完成.
    :param request:
    :return:
    """
    to_day = datetime.datetime.now().strftime('%Y-%m-%d')
    path = (IMG_DIRS + 'upload/' + to_day).replace('\\', '/')
    print(path)
    is_path = os.path.exists(IMG_DIRS + 'upload/' + to_day)
    print(IMG_DIRS + 'upload/' + to_day)
    if is_path:
        print('ok')
    else:
        print('no')
    file = request.FILES.get('upload')
    src = save_img(file, 'xxx.jpg').get('src')
    return JsonResponse({'src': src})


def get_verification(request):
    """
    获取验证码,将验证码存于request.session中方便其他视图使用
    :param request:
    :return:验证码图片的src地址
    """
    dicts = verification_code(request)
    for k, v in dicts.items():
        request.session[k] = v
    return JsonResponse({"src": dicts['file_path']})


def send_code(request):
    """
    视图需要登入权限
    发送code到用户邮箱.
    :param request:
    :return:
    """
    user = get_user(request)
    # 如果用户已绑定邮箱,则接受信息邮箱为用户已绑定邮箱,行为名称由前台指定.
    if user.email:
        email = user.email
        behavior = request.POST.get('behavior')
    else:
        behavior = '绑定邮箱'
        email = request.POST.get('email')
    code = generate_code(user.user)
    # behavior:请求的行为名称.
    send_mail(to_addr=email, message=f'你正在请求{behavior}，请在 5 分钟内输入验证码 {code} 完成{behavior}。 如非你本人操作，请忽略此邮件。')
    return JsonResponse({'status': 'ok'})
