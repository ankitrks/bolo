from django import template

from django.conf import settings
import json
import re
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def shorcountertopic(counter):
    counter = int(counter)
    if counter >= 1000 and counter < 999999:
        return str(int(round(counter/1000.0, 1)) if round(counter/1000.0, 1).is_integer() else round(counter/1000.0, 1))+' K'
    elif counter >= 999999:
        return str(int(round(counter/1000000.0, 1)) if (round(counter/1000000.0, 1)).is_integer() else (round(counter/1000000.0, 1)))+' M'
    else:
        return str(counter)

@register.simple_tag()
def category_title_by_language(categoryObj,language):
    field_name=''
    if language == 'English':
        field_name = 'title'
    else:
        field_name = language.lower() + '_title'

    if language == 'Oriya':
        field_name = language.lower() + '_title'

    return getattr(categoryObj, field_name)
	#return categoryObj.titleName

@register.filter
@stringfilter
def get_video_cdn(question_video):
    if question_video:
        regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
        find_urls_in_string = re.compile(regex, re.IGNORECASE)
        question_video = question_video.replace("https://s3.aws.com/in-boloindya/", "https://in-boloindya.s3.aws.com/")
        url = find_urls_in_string.search(question_video)
        return str(question_video.replace(str(url.group()), settings.US_CDN_URL))
    else:
        return ''


