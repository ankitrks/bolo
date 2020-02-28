from django import template
from boto.s3.connection import S3Connection
from django.conf import settings
from jarvis.models import language_options, user_group_options, status_options, FCMDevice
from drf_spirit.utils  import language_options
from forum.user.models import UserProfile

from django.utils.safestring import mark_safe
from datetime import datetime, timedelta

register = template.Library()

@register.simple_tag()
def get_user_opened_notification(pushNotification):
    return len(pushNotification.push_notification_id.filter(status='1'))


@register.simple_tag()
def get_user_delivered_notification(pushNotification):
    return len(pushNotification.push_notification_id.filter(status__in=['0', '1']))

@register.simple_tag()
def get_language_name(id):
    return language_options[int(id)][1]

@register.simple_tag()
def get_user_group_name(id):
    id = int(id)
    if id == 1:
        return mark_safe('<i class="fa fa-user-plus"></i> 3Hrs')
    elif id == 2:
        return mark_safe('<i class="fa fa-user-plus"></i>')
    elif id == 3:
        return mark_safe('<i class="fa fa-play"></i>')
    elif id == 4:
        return mark_safe('<i class="fa fa-android"></i> 24 hrs')
    elif id == 5:
        return mark_safe('<i class="fa fa-android"></i> 72 hrs')
    elif id == 6:
        return mark_safe('<i class="fa fa-video-camera" aria-hidden="true"></i>')
    return user_group_options[int(id)][1]

@register.simple_tag()
def get_notification_status(id):
    return status_options[int(id)][1]

@register.simple_tag()
def get_percentage(total, num):
    if total == 0:
        return 100
    return str(get_user_opened_notification(num)*100/total)+" %"

@register.simple_tag()
def get_category_count(id):
    return FCMDevice.objects.filter(user__st__sub_category=id, is_uninstalled=False).count()

@register.simple_tag()
def get_language_count(id):
    if id == '0':
        return FCMDevice.objects.filter(is_uninstalled=False).count()
    else:     
        return FCMDevice.objects.filter(user__st__language=id, is_uninstalled=False).count()

@register.simple_tag()
def get_uninstall_users(pushNotification):
    diff=pushNotification.scheduled_time-timedelta(hours=7)
    return len(pushNotification.push_notification_id.filter(status__in=['0', '1'], device__is_uninstalled=True, device__uninstalled_date__gte=pushNotification.scheduled_time, device__uninstalled_date__lt=diff))

