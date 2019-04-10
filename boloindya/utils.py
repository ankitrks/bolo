from django.contrib import admin
def admin_all(model):
    for obj in model.__dict__.values():
        try:
            admin.site.register(obj)
        except Exception, e:
            pass

import io
import os
import wget
import subprocess
from datetime import datetime
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
def convert_speech_to_text(blob_url):
	fname = datetime.now().strftime('%s')
	wget_command = "python -m wget -o /tmp/" + fname + " " + blob_url
	subprocess.call(wget_command, shell=True)

	command = "ffmpeg -i /tmp/" + fname + " -ab 160k -ac 1 -ar 44100 -vn /tmp/" + fname + ".wav"
	subprocess.call(command, shell=True)
	client = speech.SpeechClient()

	with io.open('/tmp/' + fname + '.wav', 'rb') as audio_file:
	  content = audio_file.read()
	  audio = types.RecognitionAudio(content=content)

	config = types.RecognitionConfig( encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16, \
					sample_rate_hertz=44100, language_code='en-US')
	response = client.recognize(config, audio)

	for result in response.results:
	   print('Transcript: {}'.format(result.alternatives[0].transcript))