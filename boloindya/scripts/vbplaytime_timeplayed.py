from forum.user.models import AndroidLogs, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend
from drf_spirit.models import UserJarvisDump, UserLogStatistics, ActivityTimeSpend, VideoDetails,UserTimeRecord
from forum.topic.models import Topic
import time
import ast 
from django.http import JsonResponse
import re
import datetime
from datetime import datetime
import os 
import pytz 
import dateutil.parser 
local_tz = pytz.timezone("Asia/Kolkata")
import sys
import django
from datetime import timedelta
from collections import OrderedDict 
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

max_playtime_list = []

def parse_duration(time):
    string_dist = time.split(":")
    mins = int(string_dist[0])
    seconds = int(string_dist[1])
    time = mins*60 + seconds
    return int(time)

def parse_colon(time):
    dist_time = time.split(":")
    if(len(dist_time)>1):
        return dist_time[0] + "" + dist_time[1]
    else:
        return dist_time[0] 

# check if this video has a legitimate playtime and return correct time
def checkvbplay(curr_videoid, time_video_played):
    media_details = Topic.objects.filter(id = curr_videoid)
    tot_playtime = media_details[0].media_duration
    tot_playtime_sec = parse_duration(tot_playtime)
    if(time_video_played > tot_playtime_sec):
        return tot_playtime_sec
    else:
        return time_video_played


def estimate_playdiff(time_sec, datetime_unix):

    datetime_dt = datetime.utcfromtimestamp((float(datetime_unix))/ 1000).replace()
    ref_timestamp = datetime_dt + timedelta(seconds = -time_sec)
    return ref_timestamp


def dump_vbrecords(userid, curr_videoid, ref_timestamp, actual_playtime):
    print userid, curr_videoid, ref_timestamp, actual_playtime
    user_data_obj, created = VideoPlaytime.objects.get_or_create(user = userid, videoid = curr_videoid, timestamp = ref_timestamp, video_id=curr_videoid)
    if(created):
        print(userid, curr_videoid, ref_timestamp, actual_playtime)
        user_data_obj.playtime = actual_playtime
        user_data_obj.save()
    else:
        print(userid, curr_videoid, ref_timestamp, actual_playtime)
        user_data_obj.playtime = actual_playtime
        user_data_obj.save()



def record_duration_play(log_text_dump, userid, created_at):

    unique_video_play = []      # dict recording the freq of the videos played

    try:            
        clickonplay_ref_map = OrderedDict()         #vid --> clickonplay time mapping
        for i in range(0, len(log_text_dump)):
            record_i = log_text_dump[i]
            curr_state = record_i.get('state')
            
            

            if 'TimePlayed' in curr_state:
                playtime = record_i['miliseconds']
                time_video_played  = (float(playtime) / 1000)
                if 'starting_time' in record_i:
                    unix_timestamp = int(record_i['starting_time'])/1000
                    dt_timestamp = datetime.utcfromtimestamp(unix_timestamp).replace(tzinfo = local_tz)
                else:
                    dt_timestamp = created_at
                curr_videoid = int(record_i.get('video_byte_id'))
                media_details = Topic.objects.filter(id = curr_videoid)
                tot_playtime = media_details[0].media_duration
                tot_playtime_sec = parse_duration(tot_playtime)

                if(time_video_played<0):
                    time_video_played = 0

                if(time_video_played>tot_playtime_sec):
                    time_video_played = tot_playtime_sec
                if time_video_played > 0.0:
                    dump_vbrecords(userid,curr_videoid,dt_timestamp,time_video_played)

    except Exception as e:
        print('Exception 2: ' + str(e)) 

def main():


    android_logs = AndroidLogs.objects.filter(log_type = 'click2play', is_executed = False)
    for each_log in android_logs:
        try:
            each_dump_log = ast.literal_eval(each_log.logs)
            each_dump_userid = each_log.user_id
            record_duration_play(each_dump_log, each_dump_userid,each_log.created_at)
            unique_id = each_log.pk
            AndroidLogs.objects.filter(pk = unique_id).update(is_executed = True)

        except Exception as e:
            print('Exception1: ' + str(e))



def run():
    main()


