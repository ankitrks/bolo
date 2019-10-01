from drf_spirit.models import UserJarvisDump, UserLogStatistics, UserFollowUnfollowDetails, UserVideoTypeDetails, VideoDetails, UserEntryPoint, UserViewedFollowersFollowing, VideoSharedDetails,UserSearch
import time
import ast
import re
import datetime
from django.http import JsonResponse
from rest_framework import status
import pytz
import os
from datetime import datetime
local_tz = pytz.timezone("Asia/Kolkata")

#! /usr/bin/python
import sys
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

# func for dumping user statistics in the model (userid, userphoneinfo, vb_viwed, vb_commented, )
def user_statistics(user_data_dump):

    try:
        user_data_list = []                 # the list which will be returned for putting values in model
        user_id = user_data_dump['user_id']
        user_phone_info = user_data_dump['user_phone_info']
        user_language = len(set(user_data_dump['user_languages']))              # number of distinct languages prefered by the user
        user_data_list.append(user_id)
        user_data_list.append(user_phone_info)
        user_data_list.append(user_language)
        #user_session_time = time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(float(user_data_dump['session_start_time'])/1000.))
        #user_session_time = datetime.datetime.fromtimestamp(float(user_data_dump['session_start_time']))
        utc_dt = datetime.utcfromtimestamp(float(user_data_dump['session_start_time'])/ 1000).replace(tzinfo=pytz.utc)
        #print(utc_dt)

        vb_viewed = []
        if('vb_viewed' in user_data_dump):
            for (a,b) in user_data_dump['vb_viewed']:
                vb_viewed.append(a)
        vb_viewed_count = len(set(vb_viewed))
        user_data_list.append(vb_viewed_count)

        vb_commented = []
        if('vb_commented' in user_data_dump):
            for (a,b) in user_data_dump['vb_commented']:
                vb_commented.append(a)
        vb_commented_count = len(set(vb_commented))
        user_data_list.append(vb_commented_count)

        vb_unliked = []
        if('vb_unliked' in user_data_dump):
            for (a,b) in user_data_dump['vb_unliked']:
                vb_unliked.append(a)
        vb_unliked_count = len(set(vb_unliked))
        user_data_list.append(vb_unliked_count)

        vb_liked = []
        if('vb_liked' in user_data_dump):
            for (a,b) in user_data_dump['vb_liked']:
                vb_liked.append(a)
        vb_liked_count = len(set(vb_liked))
        user_data_list.append(vb_liked_count)

        profile_follow = []
        if('profile_follow' in user_data_dump):
            for (a,b) in user_data_dump['profile_follow']:
                profile_follow.append(a)
        profile_follow_count = len(set(profile_follow))
        user_data_list.append(profile_follow_count)

        profile_unfollow = []
        if('profile_unfollow' in user_data_dump):
            for (a,b) in user_data_dump['profile_unfollow']:
                profile_unfollow.append(a)
        profile_unfollow_count = len(set(profile_unfollow))
        user_data_list.append(profile_unfollow_count)

        profile_report = []
        if('profile_report' in user_data_dump):
            for (a,b) in user_data_dump['profile_report']:
                profile_report.append(a)
        profile_report_count = len(set(profile_report))
        user_data_list.append(profile_report_count)

        vb_share = []
        if('vb_share' in user_data_dump):
            for (a,b,c) in user_data_dump['vb_share']:
                vb_share.append(a)
        vb_share_count = len(set(vb_share))
        user_data_list.append(vb_share_count)

        profile_viewed_following = []
        if('profile_viewed_following' in user_data_dump):    
            for(a,b) in user_data_dump['profile_viewed_following']:
                profile_viewed_following.append(a)
        profile_viewed_following_count = len(set(profile_viewed_following))
        user_data_list.append(profile_viewed_following_count)

        profile_viewed_followers = []
        if('profile_viewed_followers' in user_data_dump):
            for (a,b) in user_data_dump['profile_viewed_followers']:
                profile_viewed_followers.append(a)
        profile_viewed_followers_count = len(set(profile_viewed_followers))
        user_data_list.append(profile_viewed_followers_count)

        profile_visit_entry = []
        if('profile_visit_entry' in user_data_dump):
            for (a,b,c) in user_data_dump['profile_visit_entry']:
                profile_visit_entry.append(a)
        profile_visit_entry_count = len(set(profile_visit_entry))
        user_data_list.append(profile_visit_entry_count)

        #return user_data_list           #return the list of entries in the form of list
        #p1 = user_log_statistics()
        #user_data_list = p1.user_statistics()               # take data from the method in the form of list

        #print(user_data_list)
        user_data_obj = UserLogStatistics(user = user_data_list[0], user_phone_details = user_data_list[1], user_lang = user_data_list[2], num_vb_viewed = user_data_list[3],
            num_vb_commented = user_data_list[4], num_vb_unliked = user_data_list[5], num_vb_liked = user_data_list[6], num_profile_follow = user_data_list[7], num_profile_unfollow = user_data_list[8],
            num_profile_reported = user_data_list[9], num_vb_shared = user_data_list[10], num_viewed_following_list = user_data_list[11], num_entry_points = user_data_list[13], session_starttime = utc_dt
        )
        user_data_obj.save()
        #print(user_data_obj)

    except Exception as e:
            print('Exception 1: ' + str(e))

    return JsonResponse({'message':'success'}, status=status.HTTP_201_CREATED)

# func for dumping follow unfollow details in model(userid, profileid, timestamp, relationshiptype -{follow, unfollow, report, share})
def follow_unfollow_details(user_data_dump):
    
    try:
        user_id = user_data_dump['user_id']
        follow_list = []
        if('profile_follow' in user_data_dump):
            if(len(user_data_dump['profile_follow']) > 0 ):
                for(item1, item2) in user_data_dump['profile_follow']:
                    utc_dt = datetime.utcfromtimestamp(float(item2)/ 1000).replace(tzinfo=pytz.utc)
                    follow_list.append((item1, utc_dt))

        unfollow_list = []
        if('profile_unfollow' in user_data_dump):
            if(len(user_data_dump['profile_unfollow']) > 0):
                for (item1, item2) in user_data_dump['profile_unfollow']:

                    utc_dt = datetime.utcfromtimestamp(float(item2)/ 1000).replace(tzinfo=pytz.utc)
                    unfollow_list.append((item1, utc_dt))

        report_list = []
        if('profile_report' in user_data_dump):
            if(len(user_data_dump['profile_report']) > 0):
                for (item1, item2) in user_data_dump['profile_report']:
                    
                    utc_dt = datetime.utcfromtimestamp(float(item2)/ 1000).replace(tzinfo=pytz.utc)
                    report_list.append((item1, utc_dt))

        share_list = []
        if('profile_share' in user_data_dump):
            if(len(user_data_dump['profile_share']) > 0):
                for (item1, item2) in user_data_dump['profile_share']:
                    
                    utc_dt = datetime.utcfromtimestamp(float(item2)/ 1000).replace(tzinfo=pytz.utc)
                    share_list.append((item1, utc_dt))


        if(len(follow_list) > 0):
            for (a,b) in follow_list:
                user_data_obj = UserFollowUnfollowDetails(user = user_id, profileid = a, timestamp = b, relationship_type = 'follow')
                user_data_obj.save()

        if(len(unfollow_list) > 0):        
            for (a,b) in unfollow_list:
                user_data_obj = UserFollowUnfollowDetails(user = user_id, profileid= a, timestamp = b, relationship_type = 'unfollow')
                user_data_obj.save()                        

        if(len(report_list) > 0):        
            for(a,b) in report_list:
                user_data_obj = UserFollowUnfollowDetails(user = user_id, profileid= a, timestamp = b, relationship_type = 'report')
                user_data_obj.save()

        if(len(share_list) > 0 ):        
            for(a,b) in share_list:
                user_data_obj = UserFollowUnfollowDetails(user = user_id, profileid= a, timestamp = b, relationship_type = 'share')
                user_data_obj.save()

    except Exception as e:
        print('Exception2: ' + str(e))


    return JsonResponse({'message':'success'}, status = status.HTTP_201_CREATED)               

# func for dumping user video details in the model (video viewed, shared, commented, liked, unliked)
def video_type_details(user_data_dump):
    
    try:
        user_id = user_data_dump['user_id']
        if('vb_viewed' in user_data_dump):
            if(len(user_data_dump['vb_viewed']) > 0):
                for(a,b) in user_data_dump['vb_viewed']:
                    
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserVideoTypeDetails(user = user_id, videoid = a, timestamp = utc_dt, video_type = 'viewed')
                    user_data_obj.save()

        if('vb_share' in user_data_dump):
            if(len(user_data_dump['vb_share']) > 0):        
                for (a,b,c) in user_data_dump['vb_share']:
                    
                    utc_dt = datetime.utcfromtimestamp(float(c)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserVideoTypeDetails(user = user_id, videoid = a, timestamp = utc_dt, video_type = 'shared')
                    user_data_obj.save()

        if('vb_commented' in user_data_dump):
            if(len(user_data_dump['vb_commented']) > 0):
                for(a,b) in user_data_dump['vb_commented']:
                    #datetime_format = time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(b/1000.))
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserVideoTypeDetails(user = user_id, videoid = a, timestamp = utc_dt, video_type = 'commented')
                    user_data_obj.save()

        if('vb_liked' in user_data_dump):
            if(len(user_data_dump['vb_liked']) > 0):
                for (a,b) in user_data_dump['vb_liked']:
                    #datetime_format = time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(b/1000.))
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserVideoTypeDetails(user = user_id, videoid = a, timestamp = utc_dt, video_type = 'liked')
                    user_data_obj.save()

        if('vb_unliked' in user_data_dump):  
            if(len(user_data_dump['vb_unliked']) > 0):      
                for (a,b) in user_data_dump['vb_unliked']:
                    #datetime_format = time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(b/1000.))
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserVideoTypeDetails(user = user_id, videoid = a, timestamp = utc_dt, video_type = 'unliked')
                    user_data_obj.save()

    except Exception as e:
        print('Exception 3:' + str(e))

    return JsonResponse({'message':'success'}, status = status.HTTP_201_CREATED)        


#func for dumping video creation details into the model(videoid, timestamp)
def video_info(user_data_dump):
    
    try:
        if('vb_impressions' in user_data_dump):
            if(len(user_data_dump['vb_impressions']) > 0):
                for(a,b) in user_data_dump['vb_impressions']:
                    #datetime_format = time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(b/1000.))
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = VideoDetails(videoid = a, timestamp = utc_dt)
                    user_data_obj.save()

    except Exception as e:
        print('Exception 4: ' + str(e))

    return JsonResponse({'message':'success'}, status = status.HTTP_201_CREATED)          


#func for dumping user entry points into the model(profileid, entrytype, timestamp)      
def record_user_entry_points(user_data_dump):

    try:
        if('profile_visit_entry' in user_data_dump):
            if(len(user_data_dump['profile_visit_entry']) > 0):
                for (a,b,c) in user_data_dump['profile_visit_entry']:
                    #datetime_format = time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(c/1000.))
                    utc_dt = datetime.utcfromtimestamp(float(c)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserEntryPoint(user = a, entrypoint = b, timestamp = utc_dt)
                    user_data_obj.save()

    except Exception as e:
        print('Exception 5: ' + str(e))

    return JsonResponse({'message':'success'}, status = status.HTTP_201_CREATED)        


#func for dumping the profileids of profiles viewed and followed
def userviewed_follower_following(user_data_dump):

    try:
        userid = user_data_dump['user_id']
        if('profile_viewed_following' in user_data_dump):
            if(len(user_data_dump['profile_viewed_following']) > 0):
                for(a,b) in user_data_dump['profile_viewed_following']:
                    
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserViewedFollowersFollowing(user = userid, profileid = a, timestamp = utc_dt, relationship_type = 'following')
                    user_data_obj.save()

        if('profile_viewed_followers' in user_data_dump):
            if(len(user_data_dump['profile_viewed_followers']) > 0):        
                for(a,b) in user_data_dump['profile_viewed_followers']:
                    
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserViewedFollowersFollowing(user = userid, profileid = a, timestamp = utc_dt, relationship_type = 'followers')
                    user_data_obj.save()

    except Exception as e:
        print('Exception 6: ' + str(e))

    return JsonResponse({'message':'success'}, status = status.HTTP_201_CREATED)        

#func for storing user interests 
def user_category_intereset(user_data_dump):

    
    try:
        userid = user_data_dump['user_id']
        if('interest_added' in user_data_dump):
            if(len(user_data_dump['interest_added']) > 0):
                for (a,b) in user_data_dump['interest_added']:
                    
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserInterest(user = userid, categoryid = a, timestamp = utc_dt, category_status = 'added')
                    user_data_obj.save()

        if('interest_removed' in user_data_dump):
            if(len(user_data_dump['interest_removed']) > 0):        
                for (a,b) in user_data_dump['interest_removed']:
                    
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserInterest(user = userid, categoryid = a, timestamp = utc_dt, category_status = 'removed')
                    user_data_obj.save()

    except Exception as e:
        print(str(e))

    return JsonResponse({'message':'success'}, status = status.HTTP_201_CREATED)            

#func for storing video platform shared details of the user
def video_share(user_data_dump):
    try:
        userid = user_data_dump['user_id']
        if('vb_share' in user_data_dump):
            if(len(user_data_dump['vb_share']) > 0):
                for (a,b,c) in user_data_dump['vb_share']:

                    utc_dt = datetime.utcfromtimestamp(float(c)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = VideoSharedDetails(user = userid, videoid = a, share_platform = b, timestamp = utc_dt)
                    user_data_obj.save()

    except Exception as e:
        print('Exception 7: ' + str(e))

    return JsonResponse({'message':'success'}, status = status.HTTP_201_CREATED)


# func for storing the search query of the user
def search_query(user_data_dump):

    try:
        userid = user_data_dump['user_id']
        if('searches' in user_data_dump):
            if(len(user_data_dump['searches']) > 0):   
                for(a,b) in user_data_dump['searches']:
                    utc_dt = datetime.utcfromtimestamp(float(b)/ 1000).replace(tzinfo=pytz.utc)
                    user_data_obj = UserSearch(user = userid, searchquery = a, timestamp = utc_dt)
                    user_data_obj.save()
                    

    except Exception as e:
        print('Exception 8:' + str(e))    

    return JsonResponse({'message':'success'}, status = status.HTTP_201_CREATED)  

# func for recording the activity time spend of the user
def record_activity_time_spend(user_data_dump):
    str_start = 'STARTED'
    str_paused = 'PAUSED'

    try:
        userid = user_data_dump['user_id']
        if('activity_time_spend' in user_data_dump):
            if(len(user_data_dump['activity_time_spend']) > 0):
                for key, val in user_data_dump['activity_time_spend'].items():
                    previous_start = -1
                    previous_pause = -1
                    for item in val:
                        if(re.search(str_start, item) and previous_start == -1):
                            #previous_start = int(re.sub('STARTED\_', '',item))
                            start_str = (re.sub('STARTED_', '', item))
                            if(not re.search('[a-zA-Z]', start_str)):
                                previous_start = int(start_str)
                                #print(previous_start)

                        if((re.search(str_paused, item)) and previous_start > 0):           # pair found
                            #pause_time = int(re.sub('PAUSED\_', '',item))
                            pause_str = (re.sub('PAUSED_', '', item))
                            if(not re.search('[a-zA-Z]', )):
                                previous_pause = int(previous_pause)
                                print(previous_pause)

                            time_diff = int((pause_time - previous_start)/ 1000)
                            #print((previous_start, pause_time, time_diff))     
                            #user_data_obj = activity_time_spend(user = userid, fragmentid = key, starttime = previous_start, pausetime = pause_time)
                            #user_data_obj.save()

                        if(re.search(str_start, item) and previous_start > 1):          # update the previous time record
                            #previous_start = int(re.sub(('STARTED\_', '',item)))
                            previous_start = (re.sub('STARTED_', '', item))
                            if(not re.search('[a-zA-Z]', previous_start)):
                                previous_start = int(previous_start)



    except Exception as e:
        print('Exception 9:' + str(e))   


def main():
    # pick only those dumps which have not been executed 
    all_traction_data = UserJarvisDump.objects.filter(is_executed = False, dump_type = 1)
    for user_jarvis in all_traction_data:
        try:
            user_data_string = user_jarvis.dump
            user_data_dump = ast.literal_eval(user_data_string)
            #print(user_data_dump)
            #pass the collected user dump through a set of methods
            user_statistics(user_data_dump)
            follow_unfollow_details(user_data_dump)
            video_type_details(user_data_dump)
            video_info(user_data_dump)
            record_user_entry_points(user_data_dump)
            userviewed_follower_following(user_data_dump)
            user_category_intereset(user_data_dump)
            video_share(user_data_dump)
            search_query(user_data_dump)
            #record_activity_time_spend(user_data_dump)

            
            unique_id = user_jarvis.pk # get primary key of the dump
            UserJarvisDump.objects.filter(pk = unique_id).update(is_executed = True, dump_type = 1)  #mark the is_executed field as true
        except Exception as e:
            print('Exception 8: ' + str(e))

def run():
    main()

#if __name__ == '__main__':
#    main()



