from django import template
from boto.s3.connection import S3Connection
from django.conf import settings
from jarvis.models import language_options, user_group_options, status_options

register = template.Library()

@register.simple_tag()
def get_user_opened_notification(pushNotification):
    return len(pushNotification.push_notification_id.filter(status='1'))

@register.simple_tag()
def get_language_name(id):
    return language_options[int(id)][1]

@register.simple_tag()
def get_user_group_name(id):
    return user_group_options[int(id)][1]

@register.simple_tag()
def get_notification_status(id):
    return status_options[int(id)][1]
