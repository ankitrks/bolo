from django import template

register = template.Library()

@register.filter
def sort_solr_result(cl):
    if hasattr(cl.model_admin, 'sqs_result_dict'):
        cl.result_list = sorted(cl.result_list, key=lambda x: cl.model_admin.sqs_result_dict.get(x.id), reverse=True)
    
    return cl
