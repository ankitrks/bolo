from datetime import datetime, timedelta
from drf_spirit.models import MusicAlbum
from django.conf import settings
from drf_spirit.utils import language_options
from redis_utils import *

def run():
	try:
		now = datetime.now()
		audio_qs = MusicAlbum.objects.filter(last_modified__gte = now-timedelta(hours=6)).values_list('language_id', flat=True)
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
		audio_list = list(MusicAlbum.objects.filter(language_id=lang_id).values('id', 'title', 'author_name', 'language_id', 's3_file_path', 'image_path'))
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