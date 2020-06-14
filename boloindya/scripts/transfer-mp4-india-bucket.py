import json
import requests
from time import sleep
from datetime import datetime
from django.conf import settings
from forum.topic.models import *

f = open('/var/live_code/mp4_stats_' + str(datetime.now().date()) + '.txt', 'w')
def schedule_for_mp4_conversion(vid_url):
    new_url = ''
    try:
        f.write('============================' + '\n')
        f.write(vid_url + '\n')
        url = 'https://29gsiaxwd2.execute-api.ap-south-1.amazonaws.com/v1/transfer-video-byte'
        payload = {"input_key": vid_url.split(settings.BOLOINDYA_AWS_BUCKET_NAME+".s3.amazonaws.com/")[1]}
        response = requests.request("POST", url, headers = {}, data = json.dumps(payload), files = [])
        if response.status_code == 200:
            new_url = json.loads(response.text)['mp4_url']
            f.write(new_url + '\n')
    except Exception as e:
        f.write(str(e) + '\n')
    f.write('============================' + '\n')
    return new_url

counter = 0
topics = Topic.objects.filter(is_vb = True, is_removed = False, created_at__gte = '2020-05-01 00:00:00')\
    .exclude(question_video__icontains = 'in-boloindya').order_by('-is_popular', '-vb_score')[:50]
for each_topic in topics:
    counter += 1
    if counter >= 110:
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
f.close()