from django.conf import settings
def site_base_url(request):
    return {'site_base_url':settings.BASE_URL}

def site_base_url(request):
    return {'site_absolute_url':settings.ABSOLUTE_URL}