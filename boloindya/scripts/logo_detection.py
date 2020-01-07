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
from forum.topic.models import Topic
from forum.user.models import UserProfile
from forum.topic.models import Notification
from forum.topic.models import VideoDeleted

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

	print("hello")
	try:
		client = vision.ImageAnnotatorClient()
		today = datetime.today()
		long_ago = today + timedelta(hours = -6)			# fetch the records of last 6 hrs
		topic_objects = Topic.objects.filter(date__gte = long_ago)

		for item in topic_objects:
			print("c1")
			uri = item.backup_url
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
			i = 1
			count = 1
			possible_plag = False
			plag_text = ""
			plag_source = ["TikTok", "Helo", "VigeoVideo", "MadeWithVivaVideo", "Tik", "Tok", "Vivo", "ShareChat", "Nojoto", "Trell", "ROPOSO", "Like"]
			for interval in intervals:
				ff = FFmpeg(inputs = {uri: None}, outputs = {"output{}.png".format(count): ['-y', '-ss', interval, '-vframes', '1']})
				ff.run()
				file_name = PROJECT_PATH + '/scripts/output{}.png'.format(count)
				with io.open(file_name, 'rb') as image_file:
					content = image_file.read()
				image = vision.types.Image(content = content)
				response = client.text_detection(image = image)
				texts = response.text_annotations
				for text in texts:
					if(text.description in plag_source):
						possible_plag = True
						plag_text = str(text.description)

			# if the video is plagarized, then send the notifcation to the user			
			if(possible_plag == True):
				print("here")
				if(item.is_removed == False):		#if the video has not been deleted
					item.is_removed = True
					item.save()
					print(item.user, item.title)
					deleted_obj = VideoDeleted.objects.create(user = item.user, video_name = item.title, time_deleted = datetime.now(), plag_text = plag_text)
					deleted_obj.save()

					Topic.delete(item)		# call the method to delete the video
					#curr_obj = Notification.objects.create(topic = item, for_user = item.user, notification_type = '7', user = item.user)		
					#curr_obj.save()
					

	except Exception as e:
		print('' + str(e))						


def main():
	identify_logo()

def run():
	main()	
