# 插件函数库
import os
import datetime
import smtplib
import time
import random
from functools import wraps
from xuetang.settings import IMG_DIRS, SYMBOL_NUMBER
from django.http import Http404
from random import randint
from PIL import Image, ImageDraw, ImageFont
from xuetang.settings import VERIRICATION_CODE_DIRS
from user.models.model import Defense, User, VerificationCode
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.header import Header
import xuetang.config as config


def fn_timer(func):
    @wraps(func)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        t1 = time.time()
        print("Total time running %s: %s seconds" %
              (func.__name__, str(t1 - t0))
              )
        return result

    return function_timer


def verification_code(request):
    """
    生成4位随机数字图片
    :param request: 通过request获取请求ip,生成唯一的文件夹,存放验证码.
    :return: 返回数字信息,图片路径,生成时间.
    """
    code = [str(randint(0, 9)) for _ in range(4)]
    image = Image.new("RGB", (110, 34), (255, 255, 255))
    font = ImageFont.truetype(font="./static/fonts/consola.ttf", size=42)
    draw = ImageDraw.Draw(image)
    for i in range(4):
        # linux写入高度为-10.windows写入高度为0.
        draw.text((27.5 * i, -10), code[i], font=font, fill=(0, 0, 0))
    file_path = VERIRICATION_CODE_DIRS + request.META['REMOTE_ADDR']
    # 统一路径.
    file_path = file_path.replace('\\', '/')
    if os.path.exists(file_path):
        for i in os.listdir(path=file_path):
            os.remove(os.path.join(file_path, i))
    else:
        os.makedirs(file_path)
    filename = "".join([str(randint(0, 100)) for _ in range(6)])
    file_path += "/" + filename + '.jpg'
    image.save(file_path, format='JPEG')
    return {
        'code': ''.join(code),
        'file_path': "\\static\\img\\verification_code\\" + request.META[
            'REMOTE_ADDR'] + '\\' + filename + '.jpg',
        'create_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def ip_defense(refresh_hour=24, frequency=0):
    """
    以ip为身份信息,对每一个视图函数做出保护.限制请求次数,频率.
    :param refresh_hour: ip记录刷新时间,默认24小时刷新.
    :param frequency: 最大请求次数.
    :return: 符合条件返回被装饰函数,不符合返回404页面.
    """

    def inner(func):
        def in_inner(request, *args, **kwargs):
            # 获取now,以当前时间减去最后请求时间,得到间隔时间.
            # 获取属于当前函数的ip请求记录
            now = datetime.datetime.now()
            user = Defense.objects.filter(user_ip=request.META['REMOTE_ADDR'], func_name=func.__name__).first()

            # 如果存在记录
            if user:
                # 如果记录存在时长超过限定值,则更新记录.数值初始化.
                if (now - user.create_time).total_seconds() >= refresh_hour * 3600:
                    user.delete()
                    user = Defense(user_ip=request.META['REMOTE_ADDR'], func_name=func.__name__)
                    user.save()
            else:
                # 不存在则新建一条记录
                user = Defense(user_ip=request.META['REMOTE_ADDR'], func_name=func.__name__)
                user.save()

            # 为了使间隔时间可以迭代递增,interval默认值为1. 计算间隔的seconds也+1
            seconds = (now - user.last_time).seconds + 1

            # 判断请求次数, 间隔时间, 与ip记录状态.
            if frequency > user.frequency and seconds >= user.interval and user.status:

                return func(request, *args, **kwargs)
            else:
                raise Http404()

        return in_inner

    return inner


def user(request):
    """
    模板常量USER来源
    :param request:
    :return: 返回user对象 或者None
    """
    if request.session.get('user', None):
        obj = User.objects.filter(user=request.session['user']['user']).first()
        return {"USER": obj}
    else:
        return {'USER': None}


def get_user(request):
    """
    :param request:
    :return:
    """
    if not request.session.get('user', None):
        return None
    u = request.session['user']['user']
    u = User.objects.filter(user=u).first()
    return u


def judgment_code(user_user, code, period_of_validity=5):
    """
    返回验证码匹配结果
    :param user_user: 用户帐号.为None,则不验证user.
    :param code: 验证码
    :param period_of_validity:验证码有效时间
    :return: V实例或None
    """
    if user_user:
        kw = {'user': user_user}
    else:
        kw = {}
    now = datetime.datetime.now() - datetime.timedelta(minutes=period_of_validity)
    return VerificationCode.objects.filter(create_time__gt=now, code=code, **kw).first()


def limits(user_level, management_level, model):
    """
    设置视图可以访问的用户权限\管理权限\与判断请求内容是否属于当前用户的model
    请求内容属于当前用户,ml=1.比如隐藏文章需要权限1,删除文章ml权限需要2.
    先去完成文章内容.
    :param user_level:
    :param management_level:
    :param model:
    :return:
    """

    def inner(func):
        def in_inner(request, *args, **kwargs):
            user = request.session.get('user', None)
            # ml:management_level ~验证model关联对象,是否是当前用户
            if model.objects.filter(user=user.user).first():
                ml = 1
            else:
                ml = 0


def save_img(file, filename=None, folder=None):
    """
    存储图片函数
    :param file:文件对象
    :param filename: 指定保存的文件名,带文件类型后缀.
    :param folder:指定img目录下文件夹,头部不带'/'.
    :return:{'path': path, 'src': src}返回绝对路径和src路径
    """
    if not filename:
        filename = file.__str__()

    if folder:
        path = IMG_DIRS + folder + "/"
        src = '/static/img/' + folder + "/"
    else:
        path = IMG_DIRS + 'upload/'
        src = '/static/img/' + 'upload/'

    path = path.replace('\\', '/')  # 纠正路径 \\ -> /

    if check_path(path=path, create=True):  # 检测或直接创建路径
        path += filename
        src += filename

        with open(path, 'wb') as f:  # 创建文件写入内容进文件
            for i in file:
                f.write(i)
            f.close()

        return {'path': path, 'src': src}
    else:
        raise Exception('path does not exits and cannot be create!')


def send_mail(smtp_server='smtp.163.com', from_addr='g602049338@163.com', from_name='python学堂',
              password=config.EMAIL_PASSWORD,
              to_addr='602049338@qq.com', message=None, header='python学堂发来的邮件'):
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = _format_addr(f'{from_name} <{from_addr}>')
    msg['To'] = _format_addr(f'Do Not Reply <{to_addr}>')
    msg['Subject'] = Header(header, 'utf-8').encode()
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(0)
    # 使用ssl端口465密码为授权码.非登录密码.
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


def generate_code(user, length=6):
    """
    首先删除过期记录,
    生成一个唯一code
    返回code
    这个函数还是有存在bug的风险,暂时先忽略,等实际测试.
    :param user:登入帐号名 User.user
    :param length: code位数.
    :return:
    """
    # expiration:过期时间为5分钟前
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
    # 删除过期记录
    VerificationCode.objects.filter(create_time__lt=expiration).all().delete()

    # codes:所有已存在的code与空code的集合体.避免生成已存在的code
    codes = {i.code for i in VerificationCode.objects.all()}
    codes.add('')
    code = ''
    # 如果生成的code存在codes内,则重新生成随机code直到生成唯一code.退出循环.
    while code in codes:
        code = ''
        if length == 6:
            for i in range(length):
                code += str(random.randrange(0, 9))
        else:
            for _ in range(length):
                i = random.randrange(49, 122)
                if i in SYMBOL_NUMBER:
                    code += str(random.randrange(0, 10))
                else:
                    code += chr(i)
    v = VerificationCode.objects.filter(user=user).first()
    # 如果该用户有Vcode记录则修改记录,否则生成一个新的Vcode
    if v:
        v.code = code
        v.save()
    else:
        VerificationCode(user=user, code=code).save()
    return code


def check_path(path: str, create: bool = False) -> bool:
    """检查路径是否存在
    :param path: 被检查的路径
    :param create: 当路径不存在时,是否创建路径
    :return: 检测结果
    """
    if os.path.exists(path=path):  # 检测到路径存在,直接返回True.
        return True
    else:  # 如果创建成功,返回True, 否则都返回False.
        if create:
            try:
                os.makedirs(path)  # 尝试创建路径
            except OSError as err:
                print(err)
                return False
            else:
                return True  # 创建成功 == 路径存在, 返回True.
        else:
            return False
