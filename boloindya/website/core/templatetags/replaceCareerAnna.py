from django import template
register = template.Library()
from django.template import defaultfilters

@register.filter
@defaultfilters.stringfilter
def replace(value, args=","):
    try:
        old, new = args.split(',')
        return value.replace(old, new)
    except ValueError:
        return value