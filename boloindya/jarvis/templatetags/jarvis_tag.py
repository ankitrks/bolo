# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django import template
import json
import re
from django.template.defaultfilters import stringfilter
register = template.Library()


@register.filter(name = "is_user_in_group")
def is_user_in_group(user, group_name):
    groups = user.groups.all().values_list('name', flat=True)
    return True if group_name in groups else False

@register.filter(name='split')
def split(value, key):
    return value.split(key)

@register.filter
@stringfilter
def convert_video_cdn(transcoded_file_url):
    if transcoded_file_url:
		video_url = transcoded_file_url
		# text_to_search='elastictranscode.videos/'
		# replacement_text=''
		# transcoded_file_url=transcoded_file_url.replace(text_to_search, replacement_text)
		regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
		find_urls_in_string = re.compile(regex, re.IGNORECASE)
		url = find_urls_in_string.search(transcoded_file_url)
		video_url = str(transcoded_file_url.replace(str(url.group()), "https://cdn.careeranna.com"))   
		return video_url
    else:
        return ''
