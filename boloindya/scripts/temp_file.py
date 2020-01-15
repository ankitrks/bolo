from google.cloud import vision
import io
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

	video_url = "https://boloindyapp-prod.s3.amazonaws.com/public/video_bytes/Abhinav_bro_lucky_😎😎_1578899727365.mp4"
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
		file_name = PROJECT_PATH + '/drf_spirit/output{}.png'.format(count)
		with io.open(file_name, 'rb') as image_file:
			content = image_file.read()
		image = vision.types.Image(content = content)
		response = client.text_detection(image = image)
		texts = response.text_annotations
		print(len(texts))
		count+=1
		for text in texts:
			#print('\n"{}"'.format(text.description))
			if(text.description == "TikTok"):
				print("yes")


if __name__ == '__main__':

	identify_logo_text()
	