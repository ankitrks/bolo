# -*- coding: utf-8 -*-

from forum.topic.models import Topic
from google.cloud import vision
import io
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
client = vision.ImageAnnotatorClient()
from ffmpy import FFmpeg
import sys
import os
#from settings import PROJECT_PATH

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def detect_logos():

	filename = 'tik_tok.png'
	print(filename)

	with io.open(filename, 'rb') as image_file:
		content = image_file.read()
		#print(content)

	image = vision.types.Image(content = content)	
	#print(image)
	response = client.text_detection(image = image)
	texts = response.text_annotations
	for text in texts:
		print('\n"{}"'.format(text.description))


def identify_logo_text():

	f_name = 'plag_videos_names.txt'
	tid = [17256, 17409, 17274, 17406, 17276, 17617, 17744, 17251, 17849, 17757, 17426, 17702, 18087, 18016, 17254, 18173, 18480, 18127, 19297, 19068, 19025, 18969, 19187, 19300, 19318, 19325, 18971, 18920, 18974, 19194, 19302, 19030, 19360, 19315, 19304, 19335, 19116, 18919, 19197, 18046, 19289, 19192, 18640, 19294, 19368, 19037, 19186, 19096, 19207, 19202, 18329, 18930, 19246, 19332, 19369, 18915, 18917, 18968, 19311, 19260, 19199, 19183, 19250, 19339, 19047, 19375, 19378, 19129, 18931, 19188, 19117, 19209, 19103, 18914, 18483, 18967, 19298, 19210, 19359, 19054, 19200, 19203, 19189, 19357, 19353, 19213, 18918, 19336, 19316, 19044, 19198, 19370, 19211, 18926, 19400, 19257, 18910, 18916, 18942, 19229, 19387, 19231, 19382, 19356, 19191, 19236, 19251, 19206, 19309, 19374, 19372, 19224, 18913, 19381, 18941, 18946, 19223, 19259, 18947, 19226, 19384, 19413, 19239, 19404, 19355, 19227, 18912, 19397, 19373, 19380, 19212, 19205, 18895, 19258, 19208, 19249, 18956, 19253, 19365, 18070, 18945, 18911, 19358, 17979, 18959, 19364, 19230, 19195, 18951, 18970, 19193, 18818, 19262, 19182, 19376, 19268, 19256, 19244, 18921, 18909, 19204, 19232, 19354, 19391, 18966, 19383, 18943, 18939, 18927, 19394, 19235, 19233, 19388, 19247, 19218, 19215, 19371, 19221, 19185, 19228, 19385, 18940, 19222, 19225, 19362, 18935, 19241, 18933, 18954, 19201, 19234, 19252, 19396, 19184, 19238, 18957, 19237, 19240, 19217, 19196, 19245, 19395, 19278, 19242, 18958, 19414, 19279, 18953, 19248, 19389, 19274, 19219, 18923, 19243, 19216, 19269, 19410, 19363, 19254, 19271, 18972, 18961, 18955, 19214, 19263, 19261, 19406, 19415, 19270, 18886, 18194, 19361, 19405, 19282, 19403, 19275, 19283, 18965, 19284, 19386, 19255, 19265, 18944, 19267, 19273, 18436, 19276, 19399, 19266, 18948, 18949, 18950, 19411, 19417, 19401, 19220, 19408, 19367, 19402, 19366, 19416, 19398, 19392, 19281, 19280, 19409, 19407, 18962, 19352, 19272, 19190, 19390, 18131, 19277, 19393, 18963, 18952, 19264, 18960, 19412, 19377, 19379, 18964]

	plag_source = ["TikTok", "Helo", "Vigo", "Tik", "Tok", "Vivo", "ShareChat", "Nojoto", "Trell", "ROPOSO", "Likee"]
	f = open(f_name, 'w')

	for iter_id in tid:
		data = Topic.objects.filter(id = iter_id)
		video_url = str(data[0].backup_url)
		video_title = str(data[0].title).encode('utf-8')
		user_name = str(data[0].user)

		#video_url = "https://boloindyapp-prod.s3.amazonaws.com/public/video_bytes/Abhinav_bro_lucky_%F0%9F%98%8E%F0%9F%98%8E_1578057562228.mp4"
		#video_url = video_url.encode('utf-8')
		t1 = '00:03'
		t2 = '00:05'
		t3 = '00:07'
		intervals = []
		intervals.append(t1)
		intervals.append(t2)
		intervals.append(t3)

		count = 1
		for interval in intervals:
			ff = FFmpeg(inputs = {video_url: None}, outputs = {"output{}.png".format(count): ['-y', '-ss', interval, '-vframes', '1']})
			#print(ff.cmd)
			ff.run()
			file_name = PROJECT_PATH + '/scripts/output{}.png'.format(count)
			with io.open(file_name, 'rb') as image_file:
				content = image_file.read()
			image = vision.types.Image(content = content)
			response = client.text_detection(image = image)
			texts = response.text_annotations
			print(len(texts))
			count+=1
			for text in texts:
				if(text.description in plag_source):
					print('\n"{}"'.format(text.description))
					print("yes")
					print("............")
					f.write(str(iter_id) + str(video_title) + str(user_name))

	f.close()					


def main():
	identify_logo_text()


def run():
	main()