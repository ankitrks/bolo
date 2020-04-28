from jarvis.models import PushNotification
from datetime import datetime, timedelta
from tasks import send_notifications_task

def run():
    current_time=datetime.now()
    extend_time=current_time+timedelta(minutes=15)
    p=PushNotification.objects.filter(scheduled_time__gte=current_time, scheduled_time__lt=extend_time, is_executed=False, is_removed=False, is_scheduled=True)
    for each in p:
        data = {}
        pushNotification = {}

        data['title'] = each.description
        data['upper_title'] = each.title
        data['notification_type'] = each.notification_type
        data['id'] = each.instance_id
        data['particular_user_id'] = each.particular_user_id
        data['user_group'] = each.user_group
        data['lang'] = each.language
        try:
            if each.m2mcategory.all().count() > 0:
                list_cat=each.m2mcategory.all().values_list('pk', flat=True)
                data['category']=','.join([str(x) for x in list_cat])
            else:
                data['category'] = ''
        except:
            data['category'] = ''
        data['image_url'] = each.image_url
        data['days_ago'] = each.days_ago
        data['schedule_status']='0'
        data['datepicker']=''
        data['timepicker']=''
        each.is_executed=True
        each.is_removed=True
        each.save()

        send_notifications_task.delay(data, pushNotification)
