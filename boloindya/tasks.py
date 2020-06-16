from __future__ import absolute_import, unicode_literals
from celery_boloindya import app
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.conf import settings
import os
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
logger = get_task_logger(__name__)

from oauth2client.service_account import ServiceAccountCredentials

def _get_access_token():
  """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      os.path.join(settings.BASE_DIR, 'boloindya-1ec98-firebase-adminsdk-ldrqh-27bdfce28b.json'), "https://www.googleapis.com/auth/firebase.messaging")
  access_token_info = credentials.get_access_token()
  return access_token_info.access_token


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
    import json
    import requests
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
            access =  _get_access_token()
            
            headers = {'Authorization': 'Bearer ' + access, 'Content-Type': 'application/json; UTF-8' }
            fcm_message={}
            if user_group == '8':
                devices=FCMDevice.objects.filter(user__pk=data.get('particular_user_id', None), is_uninstalled=False)
                for each in devices:
                    fcm_message = {"message": {"token": each.reg_id ,"data": {"title_upper": upper_title, "title": title, "id": instance_id, "type": notification_type,"notification_id": str(pushNotification.id), "image_url": image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
                    resp = requests.post("https://fcm.googleapis.com/v1/projects/boloindya-1ec98/messages:send", data=json.dumps(fcm_message), headers=headers)
                    logger.info((resp))
                    logger.info((resp.text))
                    logger.info((fcm_message))
            elif lang == '0' and user_group == '0':
                fcm_message = {"message": {"topic": "all" ,"data": {"title_upper": upper_title, "title": title, "id": instance_id, "type": notification_type,"notification_id": str(pushNotification.id), "image_url": image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            elif user_group == '2' or user_group == '1':
                fcm_message = {"message": {"topic": "boloindya_install" ,"data": {"title_upper": upper_title, "title": title, "id": instance_id, "type": notification_type,"notification_id": str(pushNotification.id), "image_url": image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            elif user_group == '7':
                devices=FCMDevice.objects.filter(user__pk__in=[19, 1492, 328, 41, 40], is_uninstalled=False)
                for each in devices:
                    fcm_message = {"message": {"token": each.reg_id ,"data": {"title_upper": upper_title, "title": title, "id": instance_id, "type": notification_type,"notification_id": str(pushNotification.id), "image_url": image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
                    resp = requests.post("https://fcm.googleapis.com/v1/projects/boloindya-1ec98/messages:send", data=json.dumps(fcm_message), headers=headers)
                    logger.info((resp))
                    logger.info((resp.text))
                    logger.info((fcm_message))
            elif user_group == '9':
                fcm_message = {"message": {"topic": "boloindya_users_creator" ,"data": {"title_upper": upper_title, "title": title, "id": instance_id, "type": notification_type,"notification_id": str(pushNotification.id), "image_url": image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            elif lang == '0' or user_group == '4' or user_group == '5' or user_group == '6' or user_group == '10' or user_group == '3':
                fcm_message = {"message": {"topic": "boloindya_signup" ,"data": {"title_upper": upper_title, "title": title, "id": instance_id, "type": notification_type,"notification_id": str(pushNotification.id), "image_url": image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            elif lang != '0':
                fcm_message = {"message": {"topic": "boloindya_language_"+lang ,"data": {"title_upper": upper_title, "title": title, "id": instance_id, "type": notification_type,"notification_id": str(pushNotification.id), "image_url": image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
            resp = requests.post("https://fcm.googleapis.com/v1/projects/boloindya-1ec98/messages:send", data=json.dumps(fcm_message), headers=headers)
            logger.info((resp))
            logger.info((resp.text))
            logger.info((fcm_message))
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
            topic.update_m3u8_content()
            # data_dump, m3u8_url, job_id = transcode_media_file(topic.question_video.split('s3.amazonaws.com/')[1])
            # if m3u8_url:
                # topic.backup_url = topic.question_video
                # topic.question_video = m3u8_url
                # topic.transcode_dump = data_dump
                # topic.transcode_job_id = job_id
                # # topic.is_transcoded = True
                # topic.save()
                #create_downloaded_url(topic_id)

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

@app.task
def sync_contacts_with_user(user_id):
    from forum.user.models import UserProfile,UserPhoneBook,Contact
    user_phonebook = UserPhoneBook.objects.get(user_id=user_id)
    all_contact_no = list(user_phonebook.contact.all().values_list('contact_number',flat=True))
    print all_contact_no
    all_userprofile = UserProfile.objects.filter(mobile_no__in=all_contact_no,user__is_active=True)
    print all_userprofile
    if all_userprofile:
        for each_userprofile in all_userprofile:
            Contact.objects.filter(contact_number=each_userprofile.mobile_no).update(is_user_registered=True,user=each_userprofile.user)

@app.task
def cache_follow_post(user_id):
    from forum.topic.utils import update_redis_paginated_data
    from forum.user.utils.follow_redis import get_redis_following
    from forum.user.models import UserProfile
    from forum.topic.models import Topic
    from django.db.models import Q
    key = 'follow_post:'+str(user_id)
    all_follower = get_redis_following(user_id)
    category_follow = UserProfile.objects.get(user_id = user_id).sub_category.all().values_list('pk', flat = True)
    query = Topic.objects.filter(Q(user_id__in = all_follower)|Q(m2mcategory__id__in = category_follow, language_id = UserProfile.objects.get(user_id = user_id).language), \
    is_vb = True, is_removed = False).order_by('-vb_score')
    update_redis_paginated_data(key, query)

@app.task
def cache_popular_post(user_id,language_id):
    from forum.topic.utils import update_redis_paginated_data, get_redis_vb_seen
    from forum.user.utils.follow_redis import get_redis_following
    from forum.topic.models import Topic
    key = 'lang:'+str(language_id)+':popular_post:'+str(user_id)
    all_seen_vb= []
    if user_id:
        all_seen_vb = get_redis_vb_seen(user_id)
    query = Topic.objects.filter(is_vb = True, is_removed = False, language_id = language_id, is_popular = True).exclude(pk__in = all_seen_vb).order_by('-vb_score')
    update_redis_paginated_data(key, query)

@app.task
def create_topic_notification(created,instance_id):
    from forum.topic.models import Topic,Notification
    from forum.user.models import Follower
    from forum.user.utils.follow_redis import get_redis_follower
    try:
        instance = Topic.objects.get(pk=instance_id)
        if created:
            # all_follower_list = Follower.objects.filter(user_following = instance.user).values_list('user_follower_id',flat=True)
            all_follower_list = get_redis_follower(instance.user.id)
            for each in all_follower_list:
                notify = Notification.objects.create(for_user_id = each,topic = instance,notification_type='1',user = instance.user)
        instance.calculate_vb_score()
    except Exception as e:
        print e
        pass

@app.task
def create_comment_notification(created,instance_id):
    from forum.topic.models import Notification
    from forum.comment.models import Comment
    from forum.user.models import Follower
    from forum.user.utils.follow_redis import get_redis_follower
    try:
        instance = Comment.objects.get(pk=instance_id)
        if created:
            # all_follower_list = Follower.objects.filter(user_following = instance.user).values_list('user_follower_id',flat=True)
            all_follower_list = get_redis_follower(instance.user.id)
            for each in all_follower_list:
                if not str(each) == str(instance.topic.user.id):
                    notify = Notification.objects.create(for_user_id = each,topic = instance,notification_type='2',user = instance.user)
            notify_owner = Notification.objects.create(for_user = instance.topic.user ,topic = instance,notification_type='3',user = instance.user)
    except Exception as e:
        print e
        pass

@app.task
def create_hash_view_count(create,instance_id):
    from forum.topic.models import Topic,TongueTwister,HashtagViewCounter
    from django.db.models import Sum
    from drf_spirit.utils import language_options
    try:
        for each_language in language_options:
            language_specific_vb = Topic.objects.filter(hash_tags__id=instance_id, is_removed=False, is_vb=True,language_id=each_language[0])
            language_specific_seen = language_specific_vb.aggregate(Sum('view_count'))
            language_specific_hashtag, is_created = HashtagViewCounter.objects.get_or_create(hashtag_id=instance_id,language=each_language[0])
            if language_specific_seen.has_key('view_count__sum') and language_specific_seen['view_count__sum']:
                print "language_specific",each_language[1]," --> ",language_specific_seen['view_count__sum'],instance_id
                language_specific_hashtag.view_count = language_specific_seen['view_count__sum']
            else:
                language_specific_hashtag.view_count = 0
            language_specific_hashtag.video_count = len(language_specific_vb)
            language_specific_hashtag.save()
    except Exception as e:
        print e

@app.task
def create_thumbnail_cloudfront(topic_id):
    try:
        from forum.topic.models import Topic
        from drf_spirit.utils import get_modified_url, check_url
        lambda_url = "http://boloindyapp-prod.s3-website-us-east-1.amazonaws.com/200x300"
        cloundfront_url = "http://d3g5w10b1w6clr.cloudfront.net/200x300"
        video_byte = Topic.objects.filter(pk=topic_id)
        if video_byte.count() > 0:
            thumbnail_url = video_byte[0].question_image
            lmabda_video_thumbnail_url = get_modified_url(thumbnail_url, lambda_url)
            response = check_url(lmabda_video_thumbnail_url)
            if response == '200':
                video_byte.update(is_thumbnail_resized = True)
                lmabda_cloudfront_url = get_modified_url(thumbnail_url, cloundfront_url)
                response = check_url(lmabda_cloudfront_url)
    except Exception as e:
        print e

@app.task
def send_report_mail(report_id):
    from jarvis.models import Report
    from django.contrib.auth.models import User
    report = Report.objects.get(pk=report_id)
    try:
        if isintance(report.target, User):
            user_instance = report.target
        else:
            user_instance = report.target.user
        content_email = """
            Hello, <br><br>
            We have received a report from %s. Please find the details below:<br><br>
            <b>Video Title(ID)/ Username (ID):</b> %s (%s) <br>
            <b>Report Type:</b> %s <br>
            <b>Reported By:</b> %s <br>
            <b>Contact Number of video owner:</b> %s (%s) <br>
            Thanks,<br>
            Team BoloIndya
            """ %(report.reported_by.username, report.topic,report.topic.id, report.report_type, \
                    report.reported_by, user_instance.st.mobile_no, user_instance.email)
        requests.post(
            "https://api.mailgun.net/v3/mail.careeranna.com/messages",
            auth=("api", "d6c66f5dd85b4451bbcbd94cb7406f92-bbbc8336-97426998"),
            data={"from": "BoloIndya Support <support@boloindya.com>",
                  "to": ["support@boloindya.com"],
                  "cc":[self.contact_email],
                  "bcc":["anshika@careeranna.com", "maaz@careeranna.com", \
                        "ankit@careeranna.com", "gitesh@careeranna.com", "tanmai@boloindya.com"],
                  "subject": "BoloIndya Report Received | " + str(report.target) + ' | ' + str(report.reported_by.username),
                  "html": content_email
            }
        )
    except:
        pass
    return True

@app.task
def deafult_boloindya_follow(user_id,language):
    try:
        from django.contrib.auth.models import User
        from forum.user.models import Follower, UserProfile
        from drf_spirit.utils import add_bolo_score
        from forum.user.utils.follow_redis import update_redis_follower, update_redis_following

        user = User.objects.get(pk=user_id)
        if language == '2':
            bolo_indya_user = User.objects.get(username = 'boloindya_hindi')
        elif language == '3':
            bolo_indya_user = User.objects.get(username = 'boloindya_tamil')
        elif language == '4':
            bolo_indya_user = User.objects.get(username = 'boloindya_telgu')
        else:
            bolo_indya_user = User.objects.get(username = 'boloindya')
        follow,is_created = Follower.objects.get_or_create(user_follower = user,user_following=bolo_indya_user)
        if is_created:
            add_bolo_score(user.id, 'follow', follow)
            userprofile = UserProfile.objects.filter(user = user).update(follow_count = F('follow_count') + 1)
            bolo_indya_profile = UserProfile.objects.filter(user = bolo_indya_user).update(follower_count = F('follower_count') + 1)
            update_redis_following(user.id,int(bolo_indya_user.id),True)
            update_redis_follower(int(bolo_indya_user.id),user.id,True)
        if not follow.is_active:
            follow.is_active = True
            follow.save()
            update_redis_following(user.id,int(bolo_indya_user.id),True)
            update_redis_follower(int(bolo_indya_user.id),user.id,True)
        return True
    except:
        return False

@app.task
def save_click_id_response(user_profile_id):
    import urllib2
    from forum.user.models import Follower, UserProfile
    userprofile = UserProfile.objects.filter(pk=user_profile_id)
    userprofile[0].click_id = click_id
    click_url = 'http://res.taskbucks.com/postback/res_careeranna/dAppCheck?Ad_network_transaction_id='+str(click_id)+'&eventname=register'
    response = urllib2.urlopen(click_url).read()
    userprofile.update(click_id_response = str(response))


@app.task
def send_upload_video_notification(data, pushNotification):
    #Import files for notification
    from jarvis.models import FCMDevice
    import json
    import requests
    try:
        title = data.get('title', "")
        upper_title = data.get('upper_title', "")
        notification_type = data.get('notification_type', "")
        instance_id = data.get('id', "")
        image_url = data.get('image_url', '')
        particular_user_id=data.get('particular_user_id', None)
        access =  _get_access_token()
        
        headers = {'Authorization': 'Bearer ' + access, 'Content-Type': 'application/json; UTF-8' }
        fcm_message={}
        devices=FCMDevice.objects.filter(user__pk=data.get('particular_user_id', None), is_uninstalled=False)
        for each in devices:
            fcm_message = {"message": {"token": each.reg_id ,"data": {"title_upper": upper_title, "title": title, "id": instance_id, "type": notification_type,"notification_id": "-1", "image_url": image_url}}}
            resp = requests.post("https://fcm.googleapis.com/v1/projects/boloindya-1ec98/messages:send", data=json.dumps(fcm_message), headers=headers)
        
    except Exception as e:
        logger.info(str(e))

if __name__ == '__main__':
    app.start()
