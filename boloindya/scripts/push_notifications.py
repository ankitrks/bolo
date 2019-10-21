from jarvis.models import PushNotification

from django.db.models import Q
from drf_spirit.models import UserLogStatistics
import datetime

from forum.topic.models import VBseen, Topic
from jarvis.models import FCMDevice

def run():

    time_now = datetime.datetime.now()
    pushNotifications = PushNotification.objects.filter(is_scheduled=True, is_removed=False, is_executed=False, scheduled_time__lte=time_now)
    for pushNotification in pushNotifications:

        title = pushNotification.title
        upper_title = pushNotification.description
        notification_type = pushNotification.notification_type
        id = pushNotification.instance_id
        user_group = pushNotification.user_group
        lang = pushNotification.language

        device = ''

        language_filter = {} 
        
        if lang != '0':
            language_filter = { 'user__st__language': lang }
        
        if user_group == '1':
            end_date = datetime.datetime.today()
            start_date = end_date - datetime.timedelta(hours=3)
            device = FCMDevice.objects.filter(user__isnull=True, created_at__range=(start_date, end_date))
        
        elif user_group == '2':
            device = FCMDevice.objects.filter(user__isnull=True)
        
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

            device = FCMDevice.objects.filter(~Q(user__pk__in=filter_list)).filter(**language_filter)
        
         
        pushNotification.is_scheduled = False 
        pushNotification.is_executed = True
        pushNotification.save()

        device.send_message(data={"title": title, "id": id, "title_upper": upper_title, "type": notification_type, "notification_id": pushNotification.pk})
        pushNotification.is_scheduled = False
