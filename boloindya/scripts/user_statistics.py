from drf_spirit.models import UserJarvisDump, user_log_statistics, user_follow_unfollow_details, user_videotype_details, video_details, user_entry_point

user_statistics()

def user_statistics():
    #user_log_fname = os.getcwd() + '/drf_spirit/user_log.json'
    # user_data_dump = json.loads(request.body)         # loading data from body of request
    #dump_data = models.TextField()
    user_data_list = []                 # the list which will be returned for putting values in model

    #with open(user_log_fname) as json_file:
    #    user_data_dump = json.load(json_file)       # storing the data in a dict

    all_traction_data = UserJarvisDump.objects.filter(is_executed=False)
    # print all_traction_data
    
    for user_jarvis in all_traction_data:

        try:
            user_data_string = user_jarvis.dump
            user_data_dump = ast.literal_eval(user_data_string)

            user_data_list = []                 # the list which will be returned for putting values in model

            #with open(user_log_fname) as json_file:
            #    user_data_dump = json.load(json_file)       # storing the data in a dict

            user_id = user_data_dump['user_id']
            user_phone_info = user_data_dump['user_phone_info']
            user_language = len(set(user_data_dump['user_languages']))
            user_data_list.append(user_id)
            user_data_list.append(user_phone_info)
            user_data_list.append(user_language)

            #vb_viewed_count = len(set(user_data_dump['vb_viewed']))
            #vb_commented_count = len(set(user_data_dump['vb_commented']))
            #vb_unliked_count = len(set(user_data_dump['vb_unliked']))
            #vb_share_count= len(set(user_data_dump['vb_share']))
            #profile_follow_count = len(set(user_data_dump['profile_follow']))
            #profile_unfollow_count = len(set(user_data_dump['profile_unfollow']))
            #profile_report_count = len(set(user_data_dump['profile_report']))

            vb_viewed = []
            for (a,b) in user_data_dump['vb_viewed']:
                vb_viewed.append(a)
            vb_viewed_count = len(set(vb_viewed))
            user_data_list.append(vb_viewed_count)

            vb_commented = []
            for (a,b) in user_data_dump['vb_commented']:
                vb_commented.append(a)
            vb_commented_count = len(set(vb_commented))
            user_data_list.append(vb_commented_count)

            vb_unliked = []
            for (a,b) in user_data_dump['vb_unliked']:
                vb_unliked.append(a)
            vb_unliked_count = len(set(vb_unliked))
            user_data_list.append(vb_unliked_count)

            vb_liked = []
            for (a,b) in user_data_dump['vb_liked']:
                vb_liked.append(a)
            vb_liked_count = len(set(vb_liked))
            user_data_list.append(vb_liked_count)

            profile_follow = []
            for (a,b) in user_data_dump['profile_follow']:
                profile_follow.append(a)
            profile_follow_count = len(set(profile_follow))
            user_data_list.append(profile_follow_count)

            profile_unfollow = []
            for (a,b) in user_data_dump['profile_unfollow']:
                profile_unfollow.append(a)
            profile_unfollow_count = len(set(profile_unfollow))
            user_data_list.append(profile_unfollow_count)

            profile_report = []
            for (a,b) in user_data_dump['profile_report']:
                profile_report.append(a)
            profile_report_count = len(set(profile_report))
            user_data_list.append(profile_report_count)

            vb_share = []
            for (a,b) in user_data_dump['vb_share']:
                vb_share.append(a)
            vb_share_count = len(set(vb_share))
            user_data_list.append(vb_share_count)

            profile_viewed_following = []    
            for(a,b) in user_data_dump['profile_viewed_following']:
                profile_viewed_following.append(a)
            profile_viewed_following_count = len(set(profile_viewed_following))
            user_data_list.append(profile_viewed_following_count)

            profile_viewed_followers = []
            for (a,b) in user_data_dump['profile_viewed_followers']:
                profile_viewed_followers.append(a)
            profile_viewed_followers_count = len(set(profile_viewed_followers))
            user_data_list.append(profile_viewed_followers_count)

            profile_visit_entry = []
            for (a,b,c) in user_data_dump['profile_visit_entry']:
                profile_visit_entry.append(a)
            profile_visit_entry_count = len(set(profile_visit_entry))
            user_data_list.append(profile_visit_entry_count)

            #return user_data_list           #return the list of entries in the form of list

            #p1 = user_log_statistics()
            #user_data_list = p1.user_statistics()               # take data from the method in the form of list
            user_data_obj = user_log_statistics(user = user_data_list[0], user_phone_details = user_data_list[1], user_lang = user_data_list[2], num_vb_viewed = user_data_list[3],
                num_vb_commented = user_data_list[4], num_vb_unliked = user_data_list[5], num_vb_liked = user_data_list[6], num_profile_follow = user_data_list[7], num_profile_unfollow = user_data_list[8],
                num_profile_reported = user_data_list[9], num_vb_shared = user_data_list[10], num_viewed_following_list = user_data_list[11], num_entry_points = user_data_list[13]
            )
            user_data_obj.save()
            print(user_data_obj)

        except Exception as e:
            print(str(e))

    return JsonResponse({'message':'success'}, status=status.HTTP_201_CREATED)