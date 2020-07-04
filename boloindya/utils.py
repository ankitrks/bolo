from django.contrib import admin
def admin_all(model):
    for obj in model.__dict__.values():
        try:
            admin.site.register(obj)
        except Exception, e:
            pass

from django.conf import settings
class DBRouter(object): 
    def db_for_read(self, model, **hints):
        return 'read'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the primary/replica pool.
        """
        db_list = ('default', 'read')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

# import io
# import os
# import wget
# import subprocess
# from datetime import datetime
# from google.cloud import speech
# from google.cloud.speech import enums
# from google.cloud.speech import types
# def convert_speech_to_text(blob_url):
# 	google_cred = "export GOOGLE_APPLICATION_CREDENTIALS='/live_code/careerAnna/cred.json'"
# 	subprocess.call(google_cred, shell=True)
# 	fname = datetime.now().strftime('%s')
# 	wget_command = "python -m wget -o /tmp/" + fname + " " + blob_url
# 	subprocess.call(wget_command, shell=True)

# 	command = "ffmpeg -i /tmp/" + fname + " -ab 160k -ac 1 -ar 44100 -vn /tmp/" + fname + ".wav"
# 	subprocess.call(command, shell=True)
# 	client = speech.SpeechClient()

# 	with io.open('/tmp/' + fname + '.wav', 'rb') as audio_file:
# 	  content = audio_file.read()
# 	  audio = types.RecognitionAudio(content=content)

# 	config = types.RecognitionConfig( encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16, \
# 					sample_rate_hertz=44100, language_code='en-US')
# 	response = client.recognize(config, audio)

# 	for result in response.results:
# 	   print('Transcript: {}'.format(result.alternatives[0].transcript))
