from datetime import datetime, timedelta
from drf_spirit.models import MusicAlbum
from django.conf import settings
from drf_spirit.utils import language_options
from redis_utils import *

def run(*args):
	try:
		hours = 6
		if args:
			hours = int(args[0])
		now = datetime.now()
		audio_qs = MusicAlbum.objects.filter(last_modified__gte = now-timedelta(hours=hours), is_extracted_audio=False).values_list('language_id', flat=True)
		print "audio_qs",audio_qs
                if audio_qs:
			unique_language_id = list(set(list(audio_qs)))
			for lang_id in unique_language_id:
				create_audio_paginated_data(lang_id)
			print("done")
	except Exception as e:
		print(e)

def create_audio_paginated_data(lang_id):
	try:
		items_per_page = settings.REST_FRAMEWORK['PAGE_SIZE']
		audio_list = list(MusicAlbum.objects.filter(language_id=lang_id, is_extracted_audio=False).values('id', 'title', 'author_name', 'language_id', 's3_file_path', 'image_path', 'order_no', 'last_modified', 'is_extracted_audio'))
		page_no = 1
		start_index = 0
		end_index = items_per_page
		while(1):
			if end_index > len(audio_list):
				end_index = len(audio_list)
				break;
			data = audio_list[start_index:end_index]
			key = "audio_list:lang_id:" + str(lang_id) + ":page:" +str(page_no)
			set_redis(key, data, False)

			page_no += 1
			start_index = end_index
			end_index = items_per_page * page_no
		data = audio_list[start_index:end_index]
		key = "audio_list:lang_id:" + str(lang_id) + ":page:" +str(page_no)
		set_redis(key, data, False)
	except Exception as e:
		print(e)
