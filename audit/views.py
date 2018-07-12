from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponseRedirect
from topic.models.model import Topic, Comment, Tag
from user.models.model import Message, User
from xuetang.plug_ins import save_img


# Create your views here.

def index(request):
    """审核管理首页,
    呈现各类待审核项目条数
    """
    content = {
        'title': '审核管理',
    }
    return render(request, template_name='audit/index.html', context=content)


"""用户审核"""


def user(request):
    """用户审核页"""

    content = {
        'title': '用户审核',
        'users': User.objects.filter(status=False).order_by('-create_time').all()
    }

    return render(request, template_name='audit/user.html', context=content)


def audit_user(request) -> JsonResponse:
    """用户审核通过处理"""
    user_id = request.POST.get('user_id')
    try:
        User.objects.filter(id=user_id, status=False).update(status=True)
    except BaseException as err:
        print(err)
    return JsonResponse({'status': 'ok'})


"""标签审核"""


def tag(request):
    """标签审核页"""

    content = {
        'title': '标签管理',
        'tagsF': Tag.objects.filter(status=False).order_by('-create_time').all(),  # 未审核
        'tagsT': Tag.objects.filter(status=True).all()  # 已审核
    }
    return render(request, template_name='audit/tag.html', context=content)


def tag_modify(request):
    """修改标签图标与描述,名称不允许修改.
    :return: 回到标签审核界面
    """

    tag_id = request.POST.get('tag_id')
    t = Tag.objects.filter(id=tag_id).first()
    url = request.POST.get('icon_url')
    description = request.POST.get('description')
    if description != '':
        # 描述有传值才更新数据
        t.description = description
    # url优先等级更高
    if url != '':
        if url == 'default':
            t.icon = '/static/img/tag/default.png'
        else:
            t.icon = url
    else:
        file = request.FILES.get('icon')
        if file:
            url = save_img(file, folder='tag')
            t.icon = url['src']
    t.save()
    return HttpResponseRedirect(reverse('audit:tag'))


"""话题与评论审核"""


def topic(request):
    """话题审核页"""

    content = {
        'title': '话题审核',
        'topics': Topic.objects.filter(status=False, delete_status=False).all()
    }
    return render(request, template_name='audit/topic.html', context=content)


def comment(request):
    """评论审核页"""

    content = {
        'title': '评论审核',
        'comments': Comment.objects.filter(status=False, delete_status=False).order_by('-time').all()
    }
    return render(request, template_name='audit/comment.html', context=content)


def process(request) -> JsonResponse:  # process:处理
    """处理话题与评论审核的请求视图"""

    request_get = request.GET.get
    #  main_id:表主键id model:模型对象 process_type:操作字段,(status,delete_status,audit_message). message:留言信息
    main_id = request_get('main_id')
    model = request_get('model')
    process_type = request_get('type')
    value = request_get('value')
    # 模型通过前台传回的model选择
    models = {
        'topic': Topic,
        'comment': Comment,
        'tag': Tag,
    }
    # 操作字段的值,通过前台传回的value选择.
    values = {
        'False': False,
        'True': True,
    }
    # 收集操作所需参数后,对数据库进行操作.
    obj = models[model].objects.filter(id=main_id).first()
    setattr(obj, process_type, values[value])
    obj.save()
    # 最终在前台提示 未完成.
    return JsonResponse({'status': 'ok'})


def audit_message(request) -> JsonResponse:
    """审核留言
    用户帐号不应该暴露在前台,所以to_user_id通过对象id查询到User.user再存入Message."""

    request_post = request.POST.get
    kw = {
        'types': request_post('types'),
        'types_id': request_post('type_id'),
        'to_user_id': User.objects.filter(id=request_post('to_user')).first().user,
        'user_id': request.session.get('user')['user'],
        'content': request_post('content')
    }
    m = Message(**kw)
    m.save()
    return JsonResponse({'status:': 'ok'})
