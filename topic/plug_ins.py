from .models.model import Tag, Topic, TopicAndTag, TopicLOC, CommentLOC, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def sort_out_tag(topic, tags):
    """写入标签  |  写入标签与话题关系
    :param topic: 话题对象
    :param tags: 标签列表[a, b, c]
    :return:
    """
    topic_id = topic.id
    annal_tags = set([i.tag_id.name for i in TopicAndTag.objects.filter(topic_id=topic).all()])
    tags = set(tags)
    # delete_tags:需要删除的标签 tags:需要添加的标签
    delete_tags = annal_tags - tags
    tags = tags - annal_tags
    for i in delete_tags:
        TopicAndTag.objects.filter(topic_id=topic_id, tag_id__name=i).delete()
    for i in tags:
        tag = Tag.objects.filter(name=i).first()
        # 创建标签库没有的标签
        if not tag:
            tag = Tag(name=i)
            tag.save()
        # 将标签与话题关联起来,直接保存.
        TopicAndTag(topic_id_id=topic_id, tag_id_id=tag.id).save()


def save_topic(request, topic=None):
    """整理数据,写入数据库.
    未注册用户所发布的话题将以管理员审核帐号写入数据库.显示状态为False
    :param request:
    :return:返回topic对象,写入标签时需要.
    """
    form = request.POST.dict()
    user = request.session.get('user', None)
    kw = {
        'title': form.get('title'),
        'area_id_id': int(form.get('area')),
        'content': form.get('content')
    }
    # topic.user默认为管理员审核帐号
    if not user or user['level'] == 0:
        kw['status'] = False
    if user:
        kw['user_id'] = user['user']
    if topic:
        kw.pop('user_id', None)
        Topic.objects.filter(id=topic.id).update(**kw)
    else:
        topic = Topic(**kw)
        topic.save()
    return topic


def get_topic(request, kw=None, Q_obj=Q(id__gt=0)):
    """获取参数,查询.
    没有参数,做基本查询
    :param request:
    :param Q_obj:默认Q对象,设置为id大于0的条件,不影响正常filter过滤.id一定大于0
    :param kw: filter参数
    :return: 查询结果对象集合
    """
    if kw is None:
        kw = {}
    # 获取查询排序,与分区信息
    sort = request.GET.dict().get('sort', None)
    # 设置基本查询所需的基本参数
    kwargs = {}
    kwargs.update(kw)
    by = 'create_time'

    # 让人很不舒服的条件排查.
    if sort:
        if sort == 'now':
            by = '-create_time'
        elif sort == 'hot':
            by = '-like'
        elif sort == 'over':
            kwargs['solve_status'] = True
    return Topic.status_true.filter(Q_obj, **kwargs).order_by(by).all()


def get_paginator(page, topics, per_page=10):
    """获取话题分页.
    :param page:请求的页面
    :param topics: 符合条件的话题集合
    :param per_page: 每页话题数
    :return: topic, paginator, page_list
    """
    # page:请求页数 paginator:分页对象 page_list:处理过后的分页数
    page = int(page)
    paginator = Paginator(topics, per_page)
    page_list = get_page(page, paginator.page_range)
    # topic 目标页的话题内容集合
    try:
        topic = paginator.page(page)
    except PageNotAnInteger:
        topic = paginator.page(1)
    except EmptyPage:
        topic = paginator.page(1)
    return topic, paginator, page_list


def modify_loc(request, model):
    """修改话题或评论关系状态,话题与评论关系视图内有较多相同的操作,所以把两个视图内交叉的部分拿出来在这个函数内处理
    :param request:
    :param model: 模式:'comment'或'topic'
    :return:
    """
    # key_field: 关系对象id字段 status请求状态True或False
    key_field = request.GET.get(model)
    status = {'True': True, 'False': False}[request.GET['status']]
    user = request.session.get('user')
    result = {}
    if user:
        # 字典表两条分支是视图之间的差异
        models = {
            'topic': {
                'model': TopicLOC,
                'kwargs': {
                    'topic_id_id': key_field,
                    'user_id': user.get('user')
                }
            },
            'comment': {
                'model': CommentLOC,
                'kwargs': {
                    'cid_id': key_field,
                    'user_id': user.get('user')
                }
            }
        }
        # 根据model参数 m指向特定关系模型 kwargs指向特定模型查询参数
        m = models.get(model).get('model')
        kwargs = models.get(model).get('kwargs')
        # loc既是最终查询结果
        loc = m.objects.filter(**kwargs).first()
        # 如果有记录,则做出符合规则的修改.
        if loc:
            # 特定规则逻辑处理,因为要在loc状态修改之前做出相应 +- 动作,所以只能在这里获取 +- 动作结果
            if model == 'topic':
                if loc.status:
                    if status:
                        result.update({'like': -1, 'contra': 0})
                    else:
                        result.update({'like': -1, 'contra': 1})
                elif loc.status is False:
                    if status is False:
                        result.update({'like': 0, 'contra': -1})
                    else:
                        result.update({'like': 1, 'contra': -1})
                else:
                    if status:
                        result.update({'like': 1, 'contra': 0})
                    else:
                        result.update({'like': 0, 'contra': 1})
            # 如果存在关系, 如果关系状态等于请求状态,则将关系状态抵消设置为null,如果不等于,则改写关系状态为请求状态
            # 这么做loc表就可能会有大量关系为null的无效状态,好处就是,避免短时间重复增加或删除关系记录. 解决办法需要定期清理loc表
            loc.status = None if loc.status == status else status
        # 没有loc关系,则直接创建对应请求状态的loc关系
        else:
            loc = m(status=status, **kwargs)
            # 特定规则逻辑处理
            if model == 'topic':
                if loc.status:
                    result.update({'like': 1, 'contra': 0})
                else:
                    result.update({'like': 0, 'contra': 1})
        loc.save()
        result.update({'status': loc.status})

        # 返回主键id, 表示得到关系 +- 动作
        result.update({'key_field': key_field})
    return result


def get_page(page, page_list):
    """以当前页为中心,生成:分页导航页数列表[p-2, p-1, p, p+1, p+2]
    :param page:
    :param page_list:
    :return:
    """
    length = len(page_list)
    if length > 5:
        left = 3
        right = 2
        m = page_list[-1]
        # 判断当前页page + 1 + 2的结果 是否超过列表范围
        for i in range(1, 3):
            if page + i > m:
                right -= 1
                left += 1
            elif page - i < 1:
                left -= 1
                right += 1
        return list(page_list[page - left:page + right])
    else:
        return list(range(1, length + 1))


def adoption_review(topic_id: str or int, user_user: str) -> bool:
    """采纳评论前的验证工作
    :param topic_id: 话题id
    :param user_user: 当前登录的用户
    :return: True of False
    """

    if Comment.objects.filter(topic_id=topic_id, adoption=True).first():
        return False  # 查询是否有已被采纳的评论(正常情况:在话题已有被采纳的评论情况下,采纳接口是隐藏的.)

    if not Topic.objects.filter(id=topic_id, user=user_user).first():  # 查询话题归属者是否是当前用户,非话题归属者无权限采纳
        return False

    return True  # 验证通过
