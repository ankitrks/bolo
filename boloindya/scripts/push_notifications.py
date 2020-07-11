from jarvis.models import PushNotification

from django.db.models import Q
from drf_spirit.models import UserLogStatistics
import datetime

from forum.topic.models import VBseen, Topic
from jarvis.models import FCMDevice
from django.conf import settings
from jarvis.utils import get_token_for_user_id

def run():

    time_now = datetime.datetime.now()
    scheduled_pushNotifications = PushNotification.objects.filter(is_scheduled=True, is_removed=False, is_executed=False, scheduled_time__lte=time_now) 
    send_push_notification(scheduled_pushNotifications)
    unscheduled_pushNotifications = PushNotification.objects.filter(is_scheduled=False, is_removed=False, is_executed=False, created_at__lte = time_now - datetime.timedelta(minutes=15) )
    send_push_notification(unscheduled_pushNotifications)





def send_push_notification(pushNotifications):
    from jarvis.utils import _get_access_token
    access =  _get_access_token()  
    headers = {'Authorization': 'Bearer ' + access, 'Content-Type': 'application/json; UTF-8' }

    for pushNotification in pushNotifications:
        try:

            if pushNotification.user_group == '8':
                token_list = get_token_for_user_id(pushNotifications.particular_user_id)
                for each_token in token_list:
                    fcm_message = {"message": {"token": each_token ,"data": {"title_upper": pushNotification.title, "title": pushNotification.description, "id": pushNotification.instance_id, "type": pushNotification.notification_type,"notification_id": str(pushNotification.id), "image_url": pushNotification.image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
                    resp = requests.post("https://fcm.googleapis.com/v1/projects/boloindya-1ec98/messages:send", data=json.dumps(fcm_message), headers=headers)
            elif pushNotification.language == '0' and pushNotification.user_group == '0':
                fcm_message = {"message": {"topic": "all" ,"data": {"title_upper": pushNotification.title, "title": pushNotification.description, "id": pushNotification.instance_id, "type": pushNotification.notification_type,"notification_id": str(pushNotification.id), "image_url": pushNotification.image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            elif pushNotification.user_group == '2' or pushNotification.user_group == '1':
                fcm_message = {"message": {"topic": "boloindya_install" ,"data": {"title_upper": pushNotification.title, "title": pushNotification.description, "id": pushNotification.instance_id, "type": pushNotification.notification_type,"notification_id": str(pushNotification.id), "image_url": pushNotification.image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            elif pushNotification.user_group == '9':
                fcm_message = {"message": {"topic": "boloindya_users_creator" ,"data": {"title_upper": pushNotification.title, "title": pushNotification.description, "id": pushNotification.instance_id, "type": pushNotification.notification_type,"notification_id": str(pushNotification.id), "image_url": pushNotification.image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            elif pushNotification.language == '0' or pushNotification.user_group == '4' or pushNotification.user_group == '5' or pushNotification.user_group == '6' or pushNotification.user_group == '10' or pushNotification.user_group == '3':
                fcm_message = {"message": {"topic": "boloindya_signup" ,"data": {"title_upper": pushNotification.title, "title": pushNotification.description, "id": pushNotification.instance_id, "type": pushNotification.notification_type,"notification_id": str(pushNotification.id), "image_url": pushNotification.image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            elif pushNotification.language != '0':
                fcm_message = {"message": {"topic": "boloindya_language_"+pushNotification.language ,"data": {"title_upper": pushNotification.title, "title": pushNotification.description, "id": pushNotification.instance_id, "type": pushNotification.notification_type,"notification_id": str(pushNotification.id), "image_url": pushNotification.image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            resp = requests.post("https://fcm.googleapis.com/v1/projects/boloindya-1ec98/messages:send", data=json.dumps(fcm_message), headers=headers)
            pushNotification.is_executed=True
            pushNotification.save()
        except Exception as e:
            print e








