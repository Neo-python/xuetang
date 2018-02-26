from django import template
from user.models.model import Message

register = template.Library()


@register.simple_tag
def unread_messages(user):
    count = Message.objects.filter(addressee=user, status=False).count()
    if count:
        return count
    else:
        return ''


@register.simple_tag
def unread_count(user, self):
    count = Message.objects.filter(sender_id=user, addressee=self, types='message', status=False).count()
    if count:
        return count
    else:
        return ''
