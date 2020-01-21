# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django import template
register = template.Library()


@register.filter(name = "is_user_in_group")
def is_user_in_group(user, group_name):
    groups = user.groups.all().values_list('name', flat=True)
    return True if group_name in groups else False

@register.filter(name='split')
def split(value, key):
    return value.split(key)