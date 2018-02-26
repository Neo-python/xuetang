from django import template
from topic.models import Tag, Topic, Comment

register = template.Library()


@register.simple_tag
def audit_count(model, pop_field):
    kw = {
        'status': False,
        'delete_status': False
    }
    models = {
        'topic': Topic,
        'comment': Comment,
        'tag': Tag
    }
    kw.pop(pop_field) if pop_field else ''
    return models[model].objects.filter(**kw).count()
