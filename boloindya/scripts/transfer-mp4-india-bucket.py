import json
import m3u8
import requests
from time import sleep
from datetime import datetime
from django.conf import settings
from forum.topic.models import *

# Topic.objects.filter(is_vb = True, is_removed = False, created_at__gte = '2020-05-01 00:00:00', is_popular = True)\
# .exclude(question_video__icontains = 'in-boloindya').count()

f = open('/var/live_code/mp4_stats_' + str(datetime.now().date()) + '.txt', 'w')
def schedule_for_mp4_conversion(vid_url):
    new_url = ''
    try:
        f.write('============================' + '\n')
        f.write(vid_url + '\n')
        url = 'https://29gsiaxwd2.execute-api.ap-south-1.amazonaws.com/v1/transfer-video-byte'
        payload = {"input_key": vid_url.split("s3.amazonaws.com/")[1].replace('boloindyapp-prod/', '')}
        response = requests.request("POST", url, headers = {}, data = json.dumps(payload), files = [])
        if response.status_code == 200:
            new_url = json.loads(response.text)['mp4_url']
            f.write(new_url + '\n')
    except Exception as e:
        f.write(str(e) + '\n')
    f.write('============================' + '\n')
    return new_url

import boto3
def get_status_for_file_on_s3(media_file):
    bucket_name = "in-boloindya"
    BOLOINDYA_AWS_ACCESS_KEY_ID = 'AKIAZNK4CM5CW4W4VWP7'
    BOLOINDYA_AWS_SECRET_ACCESS_KEY = 'Odl4xfZTJZM0mq89XtNXf95g2zY8NwRuhp5+zp87'
    input_key = media_file.split(".amazonaws.com/")[1].replace('boloindyapp-prod/', '')
    try:
        s3 = boto3.client('s3',aws_access_key_id = BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = BOLOINDYA_AWS_SECRET_ACCESS_KEY)
        response = s3.head_object(Bucket=bucket_name, Key=input_key)
        return response['ResponseMetadata']['HTTPStatusCode']
    except Exception as e:
        return 404

counter = 0
topics = Topic.objects.filter(is_vb = True, is_removed = False, created_at__gte = '2020-05-01 00:00:00')\
    .exclude(question_video__icontains = 'in-boloindya').order_by('-is_popular', '-vb_score')
for each_topic in topics:
    no_old_video = False
    delete_video = False

    if '.mp4' in each_topic.safe_backup_url:
        check_mp4_status = get_status_for_file_on_s3(each_topic.safe_backup_url)
        if check_mp4_status == 404:
            no_old_video = True
            try:
                if '.m3u8' in each_topic.question_video:
                    m3u8.load( each_topic.question_video )
                else:
                    if '.mp4' in each_topic.question_video and each_topic.question_video != each_topic.safe_backup_url:
                        check_mp4_status2 = get_status_for_file_on_s3(each_topic.question_video)
                        if check_mp4_status2 == 404:
                            delete_video = True
                    else:
                        delete_video = True
            except:
                no_old_video = True
                delete_video = True

        if delete_video:
            f.write('Delete VIDEO please: ' + str(each_topic.id) + '\n')
            each_topic.delete()
        else:
            counter += 1
            if counter >= 240:
                sleep(60)
                counter = 0
            else:
                if not each_topic.safe_backup_url:
                    if '.mp4' in each_topic.question_video:
                        each_topic.safe_backup_url = each_topic.question_video
                    
                    elif '.mp4' in each_topic.backup_url:
                        each_topic.safe_backup_url = each_topic.backup_url
                
                if '.mp4' in each_topic.safe_backup_url:
                    new_url = schedule_for_mp4_conversion(each_topic.safe_backup_url)
                    if new_url:
                        if '.m3u8' in each_topic.question_video:
                            each_topic.backup_url = each_topic.question_video
                        each_topic.question_video = new_url
                    else:
                        f.write('No New URL: ' + str(each_topic.id) + ' > ' + new_url + '\n')
                else:
                    f.write('Not Converted: ' + str(each_topic.id) + '\n')
            each_topic.save()
    f.flush() # Write real time to file
f.close()