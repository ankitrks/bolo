# topics = Topic.objects.filter(is_vb = True, is_removed = False).exclude(transcode_dump__icontains = '.m3u8')\
#       .filter(question_video__icontains = '.mp4').order_by('-is_popular')
# counter = 0
# for each_topic in topics:
#     counter += 1
#     if counter >= 10:
#         sleep(180)
#         counter = 0
#     else:
#         try:
#             print each_topic.question_video
#             url = 'https://2497pr5563.execute-api.us-east-1.amazonaws.com/v1/invoke-transcode-onetime'
#             payload = {"input_key": 'public/' + each_topic.question_video.split('/public/')[1]}
#             response = requests.request("POST", url, headers = {}, data = json.dumps(payload), files = [])
#             if response.status_code == 200:
#                 m3u8_url = json.loads(response.text)['m3u8_url']
#             if m3u8_url:
#                 each_topic.transcode_dump = m3u8_url
#                 each_topic.save()
#                 print each_topic.id, each_topic.transcode_dump
#             else:
#                 print 'Error (not 200) in: ', each_topic.id
#         except Exception as e:
#             print 'Error in: ', each_topic.id, str(e)
#    print '==================='

import json
import m3u8
import requests
from time import sleep
from forum.topic.models import *
from datetime import datetime

f = open('/var/live_code/stats_' + str(datetime.now().date()) + '.txt', 'w')

def transcode_file(vid_url, each_topic):
    try:
        f.write('============================')
        f.write(vid_url)
        url = 'https://2497pr5563.execute-api.us-east-1.amazonaws.com/v1/invoke-transcode-onetime'
        payload = {"input_key": 'public/' + vid_url.split('/public/')[1]}
        response = requests.request("POST", url, headers = {}, data = json.dumps(payload), files = [])
        if response.status_code == 200:
            m3u8_url = json.loads(response.text)['m3u8_url']
            f.write(m3u8_url)
            if m3u8_url:
                each_topic.backup_url = each_topic.question_video
                each_topic.question_video = m3u8_url
                each_topic.is_transcoded = True
                each_topic.save() 
    except Exception as e:
        f.write(str(e))
    f.write('============================')
    return True

def get_sec(time_str): 
   m, s = time_str.split(':')
   return int(m) * 60 + int(s)

counter = 0
#.exclude(transcode_status_dump = 'passed').exclude(created_at__gte = '2020-06-07 21:00:00')
topics = Topic.objects.filter(is_vb = True, is_removed = False).filter(created_at__gte = '2020-05-28 14:45:00')\
    .filter(question_video__icontains = '.m3u8').order_by('-is_popular')
for each_topic in topics:
    f_res = False
    counter += 1
    if counter >= 110:
        sleep(90)
        counter = 0
    else:
        try:
            if '.m3u8' in each_topic.question_video:
                response = m3u8.load(each_topic.question_video) # Check for m3u8
                if not each_topic.m3u8_content:
                    each_topic.m3u8_content = response.dumps()
                
                if not '/elastic-transcoder/output/hls/' in each_topic.question_video:
                    if response.target_duration > 4:
                        f.write(str(each_topic.id) + ' Seg Duration: ' + str(response.target_duration) + '\n')
                        f_res = transcode_file(each_topic.safe_backup_url, each_topic)
                    else:
                        if not len(response.segments) or not response.target_duration:
                            f.write(str(each_topic.id) + ' M3U8 not loaded properly' + '\n')
                            f.write(str(each_topic.question_video) + '\n')
                        else:
                            m3u8_duration = int(len(response.segments) * response.target_duration)
                            vid_duration = int(get_sec(each_topic.media_duration))
                            if vid_duration - m3u8_duration > 2:
                                f.write(str(each_topic.id) + ' Video Incompleted - total: ' + str(vid_duration) \
                                    + ' | m3u8 duration: ' + str(m3u8_duration) + '\n')
                                f_res = transcode_file(each_topic.safe_backup_url, each_topic)
              
            elif '.mp4' in each_topic.question_video:
                f.write(str(each_topic.id) + ' Video not transcoded' + '\n')
                f_res = transcode_file(each_topic.safe_backup_url, each_topic)
           
        except Exception as e: # Breaks if m3u8 doesn't exists
            f.write(str(each_topic.id) + ' M3U8 doesnot exists: ' + str(e) + '\n')
            f_res = transcode_file(each_topic.safe_backup_url, each_topic)
    each_topic.transcode_status_dump = 'passed'
    each_topic.save()
    if not f_res:
        f.write('All OK: ' + str(each_topic.id) + '\n')
        counter -= 1
f.close()



## Check the code... doesn't do any action
"""
import json
import m3u8
import requests
from time import sleep
from forum.topic.models import *

from datetime import datetime
f = open('/var/live_code/stats_' + str(datetime.now().date()) + '.txt', 'w')

def get_sec(time_str): 
   m, s = time_str.split(':')
   return int(m) * 60 + int(s)

counter = 0
#.exclude(transcode_status_dump = 'passed').exclude(created_at__gte = '2020-06-07 21:00:00')
topics = Topic.objects.filter(is_vb = True, is_removed = False).filter(created_at__gte = '2020-06-09 00:00:00')
for each_topic in topics:
    f_res = False
    counter += 1
    if counter >= 110:
        sleep(90)
        counter = 0
    else:
        try:
            if '.m3u8' in each_topic.question_video:
                response = m3u8.load(each_topic.question_video) # Check for m3u8
                if not each_topic.m3u8_content:
                    each_topic.m3u8_content = response.dumps()
                
                if not '/elastic-transcoder/output/hls/' in each_topic.question_video:
                    if response.target_duration > 4:
                        f.write(str(each_topic.id) + ' Seg Duration: ' + str(response.target_duration) + '\n')
                        # f_res = transcode_file(each_topic.safe_backup_url, each_topic)

                    else:
                        if not len(response.segments) or not response.target_duration:
                            f.write(str(each_topic.id) + ' M3U8 not loaded properly' + '\n')
                            f.write(str(each_topic.question_video) + '\n')
                        else:
                            m3u8_duration = int(len(response.segments) * response.target_duration)
                            vid_duration = int(get_sec(each_topic.media_duration))
                            if vid_duration - m3u8_duration > 2:
                                f.write(str(each_topic.id) + ' Video Incompleted - total: ' + str(vid_duration) \
                                    + ' | m3u8 duration: ' + str(m3u8_duration) + '\n')
                                # f_res = transcode_file(each_topic.safe_backup_url, each_topic)
              
            elif '.mp4' in each_topic.question_video:
                f.write(str(each_topic.id) + ' Video not transcoded' + '\n')
                # f_res = transcode_file(each_topic.safe_backup_url, each_topic)
           
        except Exception as e: # Breaks if m3u8 doesn't exists
            f.write(str(each_topic.id) + ' M3U8 doesnot exists: ' + str(e) + '\n')
            # f_res = transcode_file(each_topic.safe_backup_url, each_topic)
    each_topic.transcode_status_dump = 'passed'
    each_topic.save()
    if not f_res:
        f.write('All OK: ' + str(each_topic.id) + '\n')
        counter -= 1
f.close()
"""