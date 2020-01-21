import boto3
import time
import random
import os
import os, io
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime,timedelta,date
from ffmpy import FFmpeg
from datetime import timedelta
from google.cloud import vision
import operator
from ffmpy import FFmpeg
client = vision.ImageAnnotatorClient()
from forum.topic.models import Topic
from forum.user.models import UserProfile
from forum.topic.models import Notification
import urllib

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# method for converting string to time
def timetostring(t):
	minute = 0
	seconds = 0
	if(t<10):
		minute = 0
		seconds = t 
		return '00'+':'+'0'+ str(seconds)
	elif(t>=60):
		minute = '01'
		seconds = t%60
		if(seconds < 10):
			seconds = '0' + str(seconds)
		else:
			seconds = str(seconds)
		return minute + ':' + seconds	
	else:
		return '00:' + str(t)			


# method to identify plagarised logos in videos uploaded
def identify_logo():
	
	plag_source = []
	plag_text_options = Topic.plag_text_options
	for (a,b) in plag_text_options:
		plag_source.append(str(b))


	f_name = 'plag_vid_details.txt'
	f = io.open(f_name, "w", encoding="UTF-8")
	today = datetime.today()
	try:
		long_ago = today + timedelta(days = -9)
		topic_objects = Topic.objects.exclude(is_removed = True).filter(is_vb = True, date__gte = long_ago)
		print(len(topic_objects))
		global_counter = 1
		for item in topic_objects:
			print("counter....", global_counter, item.id)
			url = item.backup_url
			video_title = item.title
			url_str = url.encode('utf-8')
			test = urllib.FancyURLopener()
			test.retrieve(url_str, '/tmp/local_video.mp4')
			duration = item.media_duration 
			time = duration.split(":")
			minute = int(time[0]) * 60
			second = int(time[1])
			total_second = minute + second
			t1 = int(total_second / 5)
			t2 = t1 + t1
			t3 = t1 + t2
			t4 = t1 + t3
			t5 = t1 + t4
			t1 = '00:' + timetostring(t1)
			t2 = '00:' + timetostring(t2)
			t3 = '00:' + timetostring(t3)
			t4 = '00:' + timetostring(t4)
			intervals = []
			intervals.append(t1)
			intervals.append(t2)
			intervals.append(t3)
			intervals.append(t4)
			count = 1
			global_counter+=1

			for interval in intervals:
				ff = FFmpeg(inputs = {'local_video.mp4': None}, outputs = {"output{}.png".format(count): ['-y', '-ss', interval, '-vframes', '1']})
				ff.run()
				file_name = PROJECT_PATH + '/tmp/output{}.png'.format(count)
				with io.open(file_name, 'rb') as image_file:
					content = image_file.read()
					image = vision.types.Image(content = content)
					response = client.text_detection(image = image)
					texts = response.text_annotations
					for text in texts:
						modified_text = text.description
						if(modified_text in plag_source):
							print(modified_text)
							print("yes")
							print("...............")
							f.write(video_title + " " + url_str + " " + (modified_text) + "\n")
							Topic.objects.filter(id = iter_id).update(plag_text = str(plag_source.index(modified_text)))
							Topic.objects.filter(id = iter_id).update(time_deleted = datetime.now())
							data[0].delete()

	except Exception as e:
		print('' + str(e))  				

	f.close()
					


def main():
	identify_logo()

def run():
	main()	
