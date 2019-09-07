from django import template
import boto3
from django.conf import settings
import json

register = template.Library()

@register.filter(name = "get_safe_url")
def get_safe_url(path,user):
    filepath = path.split('https://'+settings.AWS_BUCKET_NAME+'.s3.amazonaws.com/')[0]
    print filepath,"##################"
    if user.is_authenticated() and  user.is_staff:
        client = boto3.client('s3',aws_access_key_id = settings.AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY)
        # s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
        #                     settings.AWS_SECRET_ACCESS_KEY,
        #                     is_secure=True)
        # Create a URL valid for 60 seconds.
        return client.generate_url(60, 'GET',
                            bucket=settings.AWS_BUCKET_NAME,
                            key=filepath,
                            force_http=True)


@register.filter(name = "convert_string_to_json")
def convert_string_to_json(value):
    value= value.replace("u'",'"')
    value= value.replace("'",'"')
    return json.loads(value)
