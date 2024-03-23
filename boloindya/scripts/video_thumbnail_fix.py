# -*- coding: utf-8 -*-
from drf_spirit.views import get_video_thumbnail
import boto3
from botocore.errorfactory import ClientError
from django.conf import settings
from datetime import datetime, timedelta
from forum.topic.models import Topic

def run():
    s3 = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
    for each_topic in Topic.objects.filter(created_at__gte = datetime.now() - timedelta(minutes=10)).order_by('-id'):
        topic_question_image = each_topic.question_image
        bucket_name = 'in-boloindya'
        if 'in-boloindya' in topic_question_image:
            bucket_name = 'in-boloindya'
        elif 'boloindyapp-prod' in topic_question_image:
            bucket_name = 'boloindyapp-prod'
        img_key = each_topic.question_image.split('amazonaws.com/')[1]
        if img_key.startswith('boloindyapp-prod/'):
            img_key = img_key.split('boloindyapp-prod/')[1]
        elif img_key.startswith('in-boloindya/'):
            img_key = img_key.split('in-boloindya/')[1]
        try:
            s3.head_object(Bucket=bucket_name, Key=img_key)
            print 'Got it...'
        except ClientError:
            print 'Not Found: ', img_key
            try:
                img_url = get_video_thumbnail(each_topic.question_video)
            except Exception as e:
                img_url = False
                print "Error: Unable to create the thumnbail ", e
            if img_url:
                Topic.objects.filter(id = each_topic.id).update(question_image = img_url)
            else:
                print "Error: Unable to create the thumnbail"