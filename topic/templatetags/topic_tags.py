from django import template
from django.utils.safestring import mark_safe
from topic.models import Area, Collection, CommentLOC, TopicLOC
import re
import datetime

register = template.Library()


# 需求简单,暂时用不到.
# @register.inclusion_tag('topic/area.html')
# def get_area():
#     return {'areas': Area.objects.all()}


@register.simple_tag
def get_area(checked=None):
    s = ''
    for i in Area.objects.all():
        if checked == i.id:
            s += f'<option value="{i.id}" selected=selected>{i.name}</option>'
        else:
            s += f'<option value="{i.id}">{i.name}</option>'
    return mark_safe(s)


@register.filter
def get_img(value, n):
    """
    筛选出一张img标签.根据参数n返回不同的值返回不同结果
    :param value:富文本编辑器存储的包含html标签的字符串
    :param n:当n不为None时,返回img.为None时,返回class相关属性.(增加一倍的正则筛选次数,性能方面未测试,待测试.前端功底差,没办法.)
    :return:当img标签未找到时,直接返回空字符串.
    """
    result = re.search(r'<img.*?>', value)
    if result:
        if n:
            return result.group()
        else:
            return 'height-100'
    else:
        return ''


@register.filter
def get_label(value, label):
    """
    获取指定标签内容,返回指定标签内容
    可以查找多个标签,找到内容直接返回,不再查找后续的标签.
    :param value: 查找内容对象
    :param label: 查找标签, 不同标签以空格区分 暂时不支持单标签比如<img>
    :return: 返回标签内容
    """
    for i in label.split():
        result = re.search(rf'<{i}.*?</{i}>', value)
        if result:
            return result.group()
    return ""


@register.filter
def out_img(value):
    """
    替换value内的所有img标签为空字符串.优化前台显示效果
    :param value: 富文本编辑器存储的包含html标签的字符串
    :return: 替换后的字符串
    """
    return re.sub(r'(<img).+?>', '', value)


@register.filter
def reply_count(c_obj, attribute):
    """
    获取评论有效回复数量,未审核的不包括在内.
    :param attribute: 属性名
    :param c_obj: comment模型实例
    :return: 数量或空字符串
    """
    a = getattr(c_obj, attribute)
    count = a.filter(status=True).count()
    return count if count else ''


@register.simple_tag
def collection_status(user, topic):
    """
    收藏状态
    :param user:
    :param topic:
    :return:
    """
    collection = Collection.objects.filter(user_id=user, topic_id_id=topic).first()
    if collection:
        return 'menu-btn-hover'
    else:
        return ''


@register.simple_tag
def comment_loc_count(cid):
    """
    点赞计数
    :param cid:
    :return:
    """
    count = CommentLOC.objects.filter(cid_id=cid, status=True).count()
    if count:
        return count
    else:
        return '赞'


@register.simple_tag
def comment_loc(cid, user, status):
    """
    判断当前用户评论赞或反
    :param cid:
    :param user:
    :return:
    """
    kwargs = {
        True: {
            True: 'is_like',
            False: ''
        },
        False: {
            True: '取消反对',
            False: '反对'
        }
    }
    c = CommentLOC.objects.filter(cid_id=cid, user_id=user, status=status).first()
    if c:
        return kwargs[status][True]
    else:
        return kwargs[status][False]


@register.simple_tag
def is_active(topic, user, status):
    loc = TopicLOC.objects.filter(user_id=user, topic_id_id=topic, status=status).first()
    if loc:
        return 'is_active'
    else:
        return ''


@register.simple_tag
def comment_count(topic, CID):
    return None
