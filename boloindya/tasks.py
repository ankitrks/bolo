from __future__ import absolute_import, unicode_literals
from celery_boloindya import app
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
logger = get_task_logger(__name__)

@app.task
def send_notifications_task(data, pushNotification):
    #Import files for notification
    from datetime import datetime, timedelta
    from forum.topic.models import Topic, VBseen
    from forum.category.models import Category
    from drf_spirit.models import UserLogStatistics
    from jarvis.models import PushNotification, FCMDevice, PushNotificationUser
    from django.core.paginator import Paginator
    from forum.user.models import UserProfile, AndroidLogs
    try:
        title = data.get('title', "")
        upper_title = data.get('upper_title', "")
        notification_type = data.get('notification_type', "")
        instance_id = data.get('id', "")
        user_group = data.get('user_group', "")
        lang = data.get('lang', "0")
        schedule_status = data.get('schedule_status', "")
        datepicker = data.get('datepicker', '')
        timepicker = data.get('timepicker', '').replace(" : ", ":")
        image_url = data.get('image_url', '')
        particular_user_id=data.get('particular_user_id', None)
        category=data.get('category', '')

        if notification_type == '3':
            instance_id=instance_id.replace('#', '')

        pushNotification = PushNotification()
        pushNotification.title = upper_title
        pushNotification.description = title
        pushNotification.language = lang
        pushNotification.image_url = image_url
        pushNotification.notification_type = notification_type
        pushNotification.user_group = user_group
        pushNotification.instance_id = instance_id
        if data.get('days_ago', '1'):
            pushNotification.days_ago=data.get('days_ago', '1')
        if particular_user_id:
            pushNotification.particular_user_id=particular_user_id
        pushNotification.save()
    except Exception as e:
        logger.info(str(e))

    try:
        if schedule_status == '1':
            if datepicker:
                pushNotification.scheduled_time = datetime.strptime(datepicker + " " + timepicker, "%m/%d/%Y %H:%M")
            pushNotification.is_scheduled = True
            pushNotification.save()
        else:
            device = ''
            language_filter = {'is_uninstalled': False}
            exclude_filter = {}
            if lang != '0':
                language_filter = { 'user__st__language': lang, 'is_uninstalled': False}
            if category:
                try:
                    pushNotification.category=Category.objects.get(pk=category)
                    pushNotification.save()
                except Exception as e:
                    logger.info(str(e))
                language_filter['user__st__sub_category']=data.get('category', None)
            if user_group == '8':
                language_filter = {'is_uninstalled': False}
                language_filter['user__pk']=data.get('particular_user_id', None)
            elif user_group == '1':
                end_date = datetime.today()
                start_date = end_date - timedelta(hours=3)
                language_filter = {'is_uninstalled': False}
                language_filter['user__isnull']=True
                language_filter['created_at__range']=(start_date, end_date)
            elif user_group == '2':
                language_filter = {'is_uninstalled': False}
                language_filter['user__isnull']=True
            elif user_group == '7':
                #This list contains user IDs for test users: Gitesh, Abhishek, Varun, Maaz
                # Anshika, Bhoomika and Akash
                language_filter = {'is_uninstalled': False}
                filter_list = [39342, 1465, 2801, 19, 40, 328, 23, 3142, 1494, 41, 1491]
                language_filter['user__pk__in']=filter_list
            elif user_group == '9':
                hours_ago = datetime.now()-timedelta(days=int(data.get('days_ago', "1")))
                filter_list=Topic.objects.filter(is_vb=True, date__gt=hours_ago).order_by('-user__pk').distinct('user').values_list('user__pk', flat=True)
                print(filter_list)
                language_filter['user__pk__in']=filter_list
            elif user_group == '10':
                hours_ago = datetime.now()-timedelta(days=int(data.get('days_ago', "1")))
                filter_list=AndroidLogs.objects.filter(created_at__gt=hours_ago).order_by('-user__pk').distinct('user').values_list('user__pk', flat=True)
                print(filter_list)
                language_filter['user__pk__in']=filter_list
            elif user_group == '3':
                filter_list = VBseen.objects.distinct('user__pk').values_list('user__pk', flat=True)
                exclude_filter={'user__pk__in': filter_list}
            elif user_group == '4' or user_group == '5':
                hours_ago = datetime.now()
                if user_group == '4':
                    hours_ago -= timedelta(days=1)
                else:
                    hours_ago -=  timedelta(days=2)
                filter_list=AndroidLogs.objects.filter(created_at__gt=hours_ago).order_by('-user__pk').distinct('user').values_list('user__pk', flat=True)
                exclude_filter={'user__pk__in': filter_list}
            elif user_group == '6':
                filter_list = Topic.objects.filter(is_vb=True).values_list('user__pk', flat=True)
                exclude_filter={'user__pk__in': filter_list}
            print(exclude_filter)
            print(language_filter)
            device = FCMDevice.objects.exclude(**exclude_filter).filter(**language_filter)
            logger.info(device)
            print(device)
            device_pagination = Paginator(device, 1000)
            device_list=[]
            for index in range(1, (device_pagination.num_pages+1)):
                device_after_slice = device_pagination.page(index)
                logger.info(device_after_slice)
                for each in device_after_slice:
                    try:
                        t = each.send_message(data={"title": title, "id": instance_id, "title_upper": upper_title, "type": notification_type, "notification_id": pushNotification.pk, "image_url": image_url}, time_to_live=604800)
                        response=t[1]['results'][0]['message_id']
                        try:
                            PushNotificationUser.objects.create(user=each.user, push_notification_id=pushNotification, status='2', device=each, response_dump=t)
                        except:
                            pass
                    except:
                        pass
                    #t = each.send_message(data={})
                    #print(t)
                    #t = each.send_message(data={"title": title, "id": id, "title_upper": upper_title, "type": notification_type, "notification_id": pushNotification.pk, "image_url": image_url})
                logger.info(device_list)
            pushNotification.is_executed=True
            pushNotification.save()
    except Exception as e:
        logger.info(str(e))

@app.task
def vb_create_task(topic_id):
    from forum.topic.models import Topic
    from forum.topic.transcoder import transcode_media_file
    topic = Topic.objects.get(pk=topic_id)
    if not topic.is_transcoded:
        if topic.is_vb and topic.question_video:
            data_dump, m3u8_url, job_id = transcode_media_file(topic.question_video.split('s3.amazonaws.com/')[1])
            if m3u8_url:
                topic.backup_url = topic.question_video
                topic.question_video = m3u8_url
                topic.transcode_dump = data_dump
                topic.transcode_job_id = job_id
                # topic.is_transcoded = True
                topic.save()
                topic.update_m3u8_content()
                create_downloaded_url(topic_id)

@app.task
def user_ip_to_state_task(user_id,ip):
    from forum.user.models import UserProfile
    import urllib2
    import json
    userprofile = UserProfile.objects.filter(pk=user_id)
    url = 'http://ip-api.com/json/'+ip
    response = urllib2.urlopen(url).read()
    json_response = json.loads(response)
    userprofile.update(state_name = json_response['regionName'],city_name = json_response['city'])


def ffmpeg(*cmd):
    try:
        subprocess.check_output(['ffmpeg'] + list(cmd))
    except subprocess.CalledProcessError:
        return False
    return True

def upload_media(media_file,filename):
    try:
        client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
        filenameNext= str(filename).split('.')
        final_filename = str(filenameNext[0])+"."+str(filenameNext[1])
        client.put_object(Bucket=settings.BOLOINDYA_AWS_BUCKET_NAME, Key='watermark/' + final_filename, Body=media_file,ACL='public-read')
        filepath = "https://s3.amazonaws.com/"+settings.BOLOINDYA_AWS_BUCKET_NAME+"/watermark/"+final_filename
        return filepath
    except:
        return None

def create_downloaded_url(topic_id):
    import subprocess
    import os.path
    from datetime import datetime
    import os
    import boto3
    from django.conf import settings
    from forum.topic.models import Topic
    video_byte = Topic.objects.get(pk=topic_id)
    try:
        print "start time:  ",datetime.now()
        filename_temp = "temp_"+video_byte.backup_url.split('/')[-1]
        filename = video_byte.backup_url.split('/')[-1]
        cmd = ['ffmpeg','-i', video_byte.backup_url, '-vf',"[in]scale=540:-1,drawtext=text='@"+video_byte.user.username+"':x=10:y=H-th-20:fontsize=18:fontcolor=white[out]",settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp]
        ps = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (output, stderr) = ps.communicate()
        cmd = 'ffmpeg -i '+settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp+' -ignore_loop 0 -i '+settings.PROJECT_PATH+"/boloindya/media/img/boloindya_white.gif"+' -filter_complex "[1:v]format=yuva444p,scale=140:140,setsar=1,rotate=0:c=white@0:ow=rotw(0):oh=roth(0) [rotate];[0:v][rotate] overlay=10:(main_h-overlay_h+10):shortest=1" -codec:a copy -y '+settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename
        subprocess.call(cmd,shell=True)
        downloaded_url = upload_media(open(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename),filename)
        if downloaded_url:
            Topic.objects.filter(pk=video_byte.id).update(downloaded_url = downloaded_url,has_downloaded_url = True)
        if os.path.exists(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename):
            os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp)
            os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename)
        print "bye"
        print "End time:  ",datetime.now()
    except Exception as e:
        try:
            os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp)
        except:
            pass
        try:
            os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename)
        except:
            pass
        print e

if __name__ == '__main__':
    app.start()
