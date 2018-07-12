from django import template
from topic.models import Tag, Topic, Comment, User

register = template.Library()


@register.simple_tag
def audit_count(model, pop_field=None):
    """待审核计数
    :param model: 模型名,小写.
    :param pop_field: 不需要参与条件搜索的字段名
    :return: 结果计数
    """

    kw = {
        'status': False,
        'delete_status': False
    }
    models = {
        'topic': Topic,
        'comment': Comment,
        'tag': Tag,
        'user': User
    }
    kw.pop(pop_field) if pop_field else ''  # 如果pop_field不为None,弹出不需要的字段.
    return models[model].objects.filter(**kw).count()
