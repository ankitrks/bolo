from django import template

from django.conf import settings
import json
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def shorcountertopic(counter):
    counter = int(counter)
    if counter>1000 and counter<= 9999:
        return str(counter/1000.0)[:3]+'K'
    elif counter >9999 and counter<=999999:
        return str(counter/1000.0)[:5]+'K'
    elif counter >999999:
        return str(counter/1000000.0)[:5]+'M'
    else:
        return str(counter)
