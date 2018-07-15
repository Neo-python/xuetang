from django.shortcuts import render, HttpResponseRedirect, reverse, Http404
from django.http import JsonResponse
from django.template import loader
from .plug_ins import sort_out_tag, save_topic, get_topic, modify_loc, get_paginator
from .models import Area, Topic, Comment, Collection, Tag
from django.db.models import Q
from xuetang.plug_ins import get_user
import operator
from functools import reduce


# Create your views here.


def release(request):
    """
    发布话题
    :param request:
    :return:返回发布话题所在页面,未完成.返回发布结果信息.未完成
    """
    tags = request.POST.get('tags').split()

    # 保存话题
    topic = save_topic(request)

    if tags:
        # 如果有标签,创建标签,简历标签与话题关系
        sort_out_tag(topic, tags)
    return HttpResponseRedirect(reverse('topic:topic_index', args=[topic.area_id.path_name]))


def modify(request):
    """
    话题编辑页面与处理编辑内容
    :param request:
    :return: GET返回编辑页面,POST返回话题讨论页.
    """
    if request.method == 'GET':
        topic_id = request.GET.get('topic_id')
        topic = Topic.objects.filter(id=topic_id).first()
        content = {
            'title': '编辑话题',
            'topic': topic
        }
        return render(request, template_name='topic/modify.html', context=content)
    else:
        tags = request.POST.get('tags').split()
        topic_id = request.POST.get('topic_id')
        topic = Topic.objects.filter(id=topic_id).first()
        topic = save_topic(request, topic)
        sort_out_tag(topic, tags)
        return HttpResponseRedirect(reverse('topic:topic_index', args=[topic.area_id.path_name]))


def topic_index(request, area):
    """
    话题分区视图.
    :param request:
    :param area: 分区代号,作为筛选话题的主要条件之一.与前台sort分类标识
    :return: 话题列表
    """
    # 获取分区话题
    topics = get_topic(request, {'area_id__path_name': area})
    # 获取分区名,返回给前台title
    area_name = Area.objects.filter(path_name=area).first().name
    # page:请求页数 paginator:分页对象 page_list:处理过后的分页数
    page = int(request.GET.get('page', 1))
    topic, paginator, page_list = get_paginator(page, topics)
    content = {
        'title': area_name,
        'args': 'sort=' + request.GET.get('sort', ''),
        'area': area,
        'page': page,
        'topics': topic,
        'paginator': paginator,
        'page_list': page_list,
        'topic': True
    }
    return render(request, template_name='topic/index.html', context=content)


def search_topic(request):
    """
    搜索视图
    不支持tag与question双参数同时搜索.
    收集tag\question\page url参数,
    args为当前搜索内容记录,在分页导航中传入args内容.
    :param request:
    :return:
    """
    # page:请求页码,tag:标签名,question:问题内容
    page = int(request.GET.get('page', 1))
    tag = request.GET.get('tag')
    tag = Tag.objects.filter(name=tag).first()
    question = request.GET.get('question')
    # 不支持双参数同时搜索,优先搜索tag标签
    if tag:
        # topics: 获取话题中,外键id等于tag,并且状态为true的所有话题集合
        topics = get_topic(request, {'tags__tag_id': tag.id, 'status': True})

        # 将topics交给get_paginator处理获得指定页数,指定每页内容的topic 返回前台呈现
        topic, paginator, page_list = get_paginator(page=page, topics=topics, per_page=20)

        # args:url参数,维持分页功能.
        args = 'tag=' + tag.name
        title = tag.name

    elif question:
        # 查找关键词中包含的第一个标签,供前台呈现.
        for i in question.split():
            tag = Tag.objects.filter(name=i).first()
            # 查找第一个,找到即不再继续.
            if tag:
                break

        # Q_obj:多参数模糊查询.底层机制完全不知道.待解决.
        Q_obj = reduce(operator.or_,
                       ([Q(**{'title__icontains': i}) | Q(**{'content__icontains': i}) for i in question.split()]))

        # 获取话题集合
        topics = get_topic(request, Q_obj=Q_obj)

        # 获取分页相关数据
        topic, paginator, page_list = get_paginator(page=page, topics=topics, per_page=20)

        # args:url参数,维持搜索分页功能.
        args = 'question=' + question
        title = question
    else:
        return Http404
    content = {
        'title': title,
        'page': page,
        'topics': topic,
        'paginator': paginator,
        'page_list': page_list,
        'args': args,
        'tag': tag
    }
    return render(request, template_name='topic/index.html', context=content)


def discuss(request, topic_id):
    """
    话题讨论页面
    :param request:
    :param topic_id: 话题id
    :return: 返回话题内容页面
    """
    page = int(request.GET.get('page', 1))
    topic = Topic.status_true.filter(id=topic_id).first()
    comments = topic.comments.filter(status=True, reply_obj_id=None).all()
    comments, paginator, page_list = get_paginator(page, comments, per_page=20)
    contents = {
        'title': topic.title,
        'area': topic.area_id.path_name,
        'topic': topic,
        'comments': comments,
        'paginator': paginator,
        'page_list': page_list,
        'page': page
    }
    return render(request, template_name='topic/discuss.html', context=contents)


def comment(request, topic_id):
    """
    处理评论请求
    :param request:
    :param topic_id: 话题id,定位评论与话题关系
    :return: 当请求属于reply回复评论时,返回状态信息等...当请求属于评论时,跳转至话题页面,并携带message信息.
    """
    # 获取user判断评论有效性 obj判断是否为回复
    user = get_user(request)
    content = request.POST.get('comment', None)
    obj = request.POST.get('reply', None)
    kwargs = {'reply_obj_id': obj} if obj else {}
    # 以url参数message=xxx的方式传递给给前台的消息反馈,具体消息在前台js文件内.
    message = '?'
    if user:
        # 当用户帐号未激活时,将评论状态改为待审核,并做出相应提示.
        if user.level == 0:
            kwargs.update({'status': False})
            message += 'message=comment-level'
        comment = Comment(user_id=user.user, topic_id_id=topic_id, content=content, **kwargs)
        comment.save()
    else:
        # 获取游客ip message提示评论需要审核
        ip = request.META['REMOTE_ADDR']
        message += "message=comment-audit"
        comment = Comment(user_id='AdminAudit', status=False, topic_id_id=topic_id, content=content, ip=ip, **kwargs)
        comment.save()
    # 如果有reply对象,请求则为ajax请求,返回前台所需的反馈信息.
    if obj:
        # reply回复功能,不允许未登入用户回复,
        return JsonResponse({'status': 'ok', 'user': comment.user.nickname, 'content': comment.content})
    else:
        return HttpResponseRedirect(reverse('topic:discuss', args=[topic_id]) + message)


def get_reply(request):
    """
    获取指定评论对象,得到回复数据,以json格式返回给前台,由前台渲染呈现.
    :param request:
    :return: 返回状态码,replys:回复集合. replys是由n个{user:xx, content:xx}组成的列表
    """
    reply = int(request.GET.get('reply'))

    # 得到全部指向评论id的状态为true的回复
    comments = Comment.objects.filter(status=True, reply_obj=reply).all()

    replys = []
    # 如果comments不为None, 循环comments 生成{user:xx, content:xx}格式的字典表,追加进replys,供前台呈现.
    if comments:
        for i in comments:
            replys.append({
                'user': i.user.nickname,
                'content': i.content
            })
    return JsonResponse({'status': 'ok', 'replys': replys})


def collection(request):
    """
    收藏话题请求\处理,视图.
    如果用户当前未登录,直接返回failure状态码,如果已登录,再继续做判断.
    :param request:
    :return: 状态码与相应提示信息通知
    """
    user = get_user(request)
    if user:
        topic = request.GET.get('topic')
        c = Collection.objects.filter(topic_id_id=topic, user=user).first()
        if c:
            # 用户已收藏此话题,当前请求判断为取消收藏.选择删除收藏关系
            c.delete()
            return JsonResponse({'status': 'success', 'message': 'cancel-collection'})
        else:
            # 用户未收藏此话题,建立收藏关系
            c = Collection(topic_id_id=topic, user=user)
            c.save()
            return JsonResponse({'status': 'success', 'message': 'collection-success'})
    else:
        return JsonResponse({'status': 'failure', 'message': 'collection-failure'})


def comment_loc(request):
    """
    comment like or contra 关系处理视图
    :param request:
    :return:
    """
    result = modify_loc(request, 'comment')
    key_id = result.pop('key_field', None)
    # 如果有key_id 表示关系处理正常,返回相关信息到前台.
    if key_id:
        return JsonResponse(result)
    else:
        return Http404


def topic_loc(request):
    """
    话题like or contra 关系处理视图
    从modify_loc获取关系 +- 动作结果,修改话题相关字段值
    :param request: 成功返回关系结果,否则返回404状态,前端不执行后续js操作
    :return:
    """
    result = modify_loc(request, 'topic')
    key_id = result.pop('key_field', None)

    # 如果有key_id 表示关系处理正常,修改话题相关字段值.
    if key_id:
        topic = Topic.objects.filter(pk=key_id).first()
        topic.like += result.pop('like')
        topic.contra += result.pop('contra')
        topic.save()
        return JsonResponse(result)
    else:
        raise Http404
