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
    from drf_spirit.models import UserLogStatistics
    from jarvis.models import PushNotification, FCMDevice, PushNotificationUser
    from django.core.paginator import Paginator
    from forum.user.models import UserProfile
    try:
        title = data.get('title', "")
        upper_title = data.get('upper_title', "")
        notification_type = data.get('notification_type', "")
        id = data.get('id', "")
        user_group = data.get('user_group', "")
        lang = data.get('lang', "")
        schedule_status = data.get('schedule_status', "")
        datepicker = data.get('datepicker', '')
        timepicker = data.get('timepicker', '').replace(" : ", ":")
        image_url = data.get('image_url', '')
        
        if user_group == '8':
            lang='0'

        pushNotification = PushNotification()
        pushNotification.title = upper_title
        pushNotification.description = title
        pushNotification.language = lang
        pushNotification.image_url = image_url
        pushNotification.notification_type = notification_type
        pushNotification.user_group = user_group
        pushNotification.instance_id = id
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
            language_filter = {} 

            if lang != '0':
                language_filter = { 'user__st__language': lang, 'is_uninstalled': False }

            if data.get('category', 'Select Category') not in 'Select Category':
                filter_list=UserProfile.objects.filter(sub_category=data.get('category', None)).values_list('user__pk', flat=True)
                device = FCMDevice.objects.filter(user__pk__in=filter_list, user__st__language=lang, is_uninstalled=False)
            elif user_group == '8':
                device = FCMDevice.objects.filter(user__pk=data.get('particular_user_id', None))
            elif user_group == '1':
                end_date = datetime.today()
                start_date = end_date - timedelta(hours=3)
                device = FCMDevice.objects.filter(user__isnull=True, created_at__range=(start_date, end_date), is_uninstalled=False)

            elif user_group == '2':
                device = FCMDevice.objects.filter(user__isnull=True, is_uninstalled=False)

            elif user_group == '7':
                #This list contains user IDs for test users: Gitesh, Abhishek, Varun, Maaz
                # Anshika, Bhoomika and Akash
                filter_list = [39342, 1465, 2801, 19, 40, 328, 23, 3142, 1494, 41]
                device = FCMDevice.objects.filter(user__pk__in=filter_list, is_uninstalled=False)
            elif user_group == '0':
                device = FCMDevice.objects.filter(is_uninstalled=False, user__st__language=lang)
            else:
                filter_list = []


                if user_group == '3':
                    filter_list = VBseen.objects.distinct('user__pk').values_list('user__pk', flat=True)

                elif user_group == '4' or user_group == '5':
                    hours_ago = datetime.now()
                    if user_group == '4':
                        hours_ago -= timedelta(days=1)
                    else:
                        hours_ago -=  timedelta(days=2)

                    filter_list = UserLogStatistics.objects.filter(session_starttime__gte=hours_ago).values_list('user', flat=True)
                    filter_list = map(int , filter_list)

                elif user_group == '6':
                    filter_list = Topic.objects.filter(is_vb=True).values_list('user__pk', flat=True)

                device = FCMDevice.objects.exclude(user__pk__in=filter_list).filter(**language_filter)

            logger.info(device)
            device_pagination = Paginator(device, 1000)
            device_list=[]
            for index in range(1, (device_pagination.num_pages+1)):
                device_after_slice = device_pagination.page(index)
                logger.info(device_after_slice)
                for each in device_after_slice:
                    t = each.send_message(data={})
                    device_list.append(t)
                    try:
                        PushNotificationUser.objects.create(user=each.user, push_notification_id=pushNotification, status='2')
                    except:
                        pass
                #t = device_after_slice.object_list.send_message(data={"title": title, "id": id, "title_upper": upper_title, "type": notification_type, "notification_id": pushNotification.pk})
                #t = device_after_slice.object_list.send_message(data={'pupluar_data': 'true' })
                logger.info(device_list)
            pushNotification.is_executed=True
            pushNotification.save()
    except Exception as e:
        logger.info(str(e))

@app.task
def vb_create_task(topic_id):
    from forum.topic.models import Topic
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


if __name__ == '__main__':
    app.start()
