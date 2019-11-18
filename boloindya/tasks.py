from __future__ import absolute_import, unicode_literals
from celery1 import app
from celery.utils.log import get_task_logger
from django.core.mail import send_mail

logger = get_task_logger(__name__)

@app.task
def send_sample_mail_task(subject, message, email_from, getter):
    return send_mail(subject, message, email_from, getter)

@app.task
def send_notifications_task(data, pushNotification):

    #Import files for notification
    from datetime import datetime, timedelta
    from forum.topic.models import Topic, VBseen
    from drf_spirit.models import UserLogStatistics
    from jarvis.models import PushNotification, FCMDevice

    # from jarvis.views import send_notifications_thru_celery
    # return send_notifications_thru_celery(data, pushNotification)
    title = data.get('title', "")
    upper_title = data.get('upper_title', "")
    notification_type = data.get('notification_type', "")
    id = data.get('id', "")
    user_group = data.get('user_group', "")
    lang = data.get('lang', "")
    schedule_status = data.get('schedule_status', "")
    datepicker = data.get('datepicker', '')
    timepicker = data.get('timepicker', '').replace(" : ", ":")

    pushNotification = PushNotification()
    pushNotification.title = upper_title
    pushNotification.description = title
    pushNotification.language = lang
    pushNotification.notification_type = notification_type
    pushNotification.user_group = user_group
    pushNotification.instance_id = id
    pushNotification.save()

    if schedule_status == '1':
        if datepicker:
            pushNotification.scheduled_time = datetime.datetime.strptime(datepicker + " " + timepicker, "%m/%d/%Y %H:%M")
        pushNotification.is_scheduled = True            
        pushNotification.save()
    else:
        device = ''

        language_filter = {} 

        logger.info(user_group)

        if lang != '0':
            language_filter = { 'user__st__language': lang }
        
        if user_group == '1':
            end_date = datetime.datetime.today()
            start_date = end_date - datetime.timedelta(hours=3)
            device = FCMDevice.objects.filter(user__isnull=True, created_at__range=(start_date, end_date))
        
        elif user_group == '2':
            device = FCMDevice.objects.filter(user__isnull=True)
        
        elif user_group == '7':
            filter_list = [39342, 1465]
            device = FCMDevice.objects.filter(user__pk__in=filter_list)
            # device.send_message(data={"title": title, "id": id, "title_upper": upper_title, "type": notification_type, "notification_id": pushNotification.pk})
            # logger.info(len(device))
        else:
            filter_list = []

            if user_group == '3':
                filter_list = VBseen.objects.distinct('user__pk').values_list('user__pk', flat=True)
            
            elif user_group == '4' or user_group == '5':
                hours_ago = datetime.datetime.now()
                if user_group == '4':
                    hours_ago -= datetime.timedelta(days=1)
                else:
                    hours_ago -=  datetime.timedelta(days=2)

                filter_list = UserLogStatistics.objects.filter(session_starttime__gte=hours_ago).values_list('user', flat=True)
                filter_list = map(int , filter_list)
                
            elif user_group == '6':
                filter_list = Topic.objects.filter(is_vb=True).values_list('user__pk', flat=True)

            device = FCMDevice.objects.exclude(user__pk__in=filter_list).filter(**language_filter)

        logger.info(device)
        # print(device)
        device.send_message(data={"title": title, "id": id, "title_upper": upper_title, "type": notification_type, "notification_id": pushNotification.pk})


if __name__ == '__main__':
    app.start()