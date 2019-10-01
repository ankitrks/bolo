# this file is responsible for dumping the user logs into the database
# parsing data and putting objects into already created models

#from . import *
from drf_spirit.models import SignUpOTP
#from django.db import models
import os

def main():
	parse_logs()


# method responsible for parsing logs and extracting required info
def parse_logs_statistics():

	fname = os.getcwd() + '/user_log.json'

	user_data_list = []			#empty data list
	with open(fname) as json_file:
		user_data_dump = json.load(json_file)

	user_id = user_data_dump['user_id']
	user_phone_info = user_data_dump['user_phone_info']
	user_language = user_data_dump['user_languages']

	#user_data_list.append(user_id)
	#user_data_list.append(user_phone_info)
	#user_data_list.append(user_language)

	vb_viewed = []
	for (a,b) in user_data_dump['vb_viewed']:
		vb_viewed.append(a)
	vb_viewed_count = len(set(vb_viewed))
	#user_data_list.apppend(vb_viewed_count)

	vb_commented = []
	for (a,b) in user_data_dump['vb_commented']:
		vb_commented.append(a)
	vb_commented_count = len(set(vb_commented))
	#user_data_list.append(vb_commented_count)

	vb_unliked = []
	for (a,b) in user_data_dump['vb_unliked']:
		vb_unliked.append(a)
	vb_unliked_count = len(set(vb_unliked))
	#user_data_list.append(vb_unliked_count)

	vb_liked = []
	for (a,b) in user_data_dump['vb_liked']:
		vb_liked.append(a)
	vb_liked_count = len(set(vb_liked))
	#user_data_list.append(vb_liked_count)

	profile_follow = []
	for (a,b) in user_data_dump['profile_follow']:
		profile_follow.append(a)
	profile_follow_count = len(set(profile_follow))
	#user_data_list.append(profile_follow_count)
	
	profile_unfollow = []
	for (a,b) in user_data_dump['profile_unfollow']:
		profile_unfollow.append(a)
	profile_unfollow_count = len(set(profile_unfollow))
	#user_data_list.append(profile_unfollow_count)

	profile_report = []
	for (a,b) in user_data_dump['profile_report']:
		profile_report.append(a)
	profile_report_count = len(set(profile_report))
	#user_data_list.append(profile_report_count)

	vb_share = []
	for (a,b) in user_data_dump['vb_share']:
		vb_share.append(a)
	vb_share_count = len(set(vb_share))
	#user_data_list.append(vb_share_count)
	
	profile_viewed_following = []
	for (a,b) in user_data_dump['profile_viewed_following']:
		profile_viewed_following.append(a)
	profile_viewed_following_count = len(set(profile_viewed_following))
	#user_data_list.append(profile_viewed_following_count)

	profile_viewed_followers = []
	for (a,b) in user_data_dump['profile_viewed_followers']:
		profile_viewed_followers.append(a)
	profile_viewed_followers_count = len(set(profile_viewed_followers))
	#user_data_list.append(profile_viewed_followers_count)
	
	profile_visit_entry = []
	for (a,b) in user_data_dump['profile_visit_entry']:
		profile_visit_entry.append(a)
	profile_visit_entry_count = len(set(profile_visit_entry))
	#user_data_list.append(profile_visit_entry_count)

	session_start_time = user_data_dump['session_start_time']
	#user_data_list.append(user_data_dump['session_start_time'])

	user_stats_obj = user_log_statistics(user = user_id, user_phone_details = user_phone_info, user_lang = user_language, num_profile_follow = profile_follow_count, num_profile_unfollow = profile_unfollow_count,
		num_viewed_profile = profile_viewed_following_count, num_profile_reported = profile_report_count, num_viewed_following_list = profile_viewed_followers_count, num_entry_points = profile_visit_entry_count,
		num_vb_commented = vb_commented_count, num_vb_liked = vb_liked_count, num_vb_shared = vb_share_count, num_vb_unliked = vb_unliked_count, num_vb_viewed = vb_viewed_count, 
		session_starttime =  session_start_time
		)
	
	user_stats_obj.save()
	


if __name__ == '__main__':
	main()			







		