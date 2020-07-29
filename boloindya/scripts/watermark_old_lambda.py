import json
import boto3
import requests
from time import sleep
from datetime import datetime
from django.conf import settings
from forum.topic.models import *

def schedule_for_branding(vid_url, username):
    new_url = ''
    try:
        #print('============================') # + '\n'
        #print(username + ' > ' + vid_url) # + '\n'
        url = 'https://jrco8bdf39.execute-api.ap-south-1.amazonaws.com/v1/invokewatermarkforexisitngvideos'
        payload = {"input_key": vid_url.split(".amazonaws.com/")[1].replace('in-boloindya/', ''), 'username' : username}
        response = requests.request("POST", url, headers = {}, data = json.dumps(payload), files = [])
        if response.status_code == 200:
            json_response = json.loads(response.text)
            if json_response.has_key('message') and json_response['message'] == 'success' and json_response.has_key('url') and json_response['url']:
                new_url = json_response['url']
            print(new_url) # + '\n'
    except Exception as e:
        print(str(e)) # + '\n'
    print('============================') # + '\n'
    return new_url

def run():
    # last_urls = []
    counter = 0
    topics = Topic.objects.filter(is_vb=True, is_removed=False, has_downloaded_url = False, created_at__gte = '2020-05-01 00:00:00')\
        .order_by('-is_popular', '-id')
    for each_topic in topics:
        brand_url = False
        counter += 1
        if counter >= 330:
            sleep(120)
            counter = 0
            # last_urls = []
        else:
            try:  
                if '.mp4' in each_topic.question_video:
                    #print(str(each_topic.id) + ' Creating branded copy') # + '\n'
                    brand_url = schedule_for_branding(each_topic.safe_backup_url, each_topic.user.username)
                    if brand_url:
                        # last_urls.append(brand_url)
                        each_topic.downloaded_url = brand_url
                        each_topic.has_downloaded_url = True
                        each_topic.is_globally_pinned = True #To check them later
                        each_topic.save()
                        # print(str(each_topic.id) + ' Created...') # + '\n'
                    #else:
                    #    print(str(each_topic.id) + ' Blank brand url: ') # + '\n'
            except Exception as e: # Breaks if m3u8 doesn't exists
                print(str(each_topic.id) + ' Could not created the copy: ' + str(e)) # + '\n'
