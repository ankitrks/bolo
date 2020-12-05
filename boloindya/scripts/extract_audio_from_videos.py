import os
import sys
import requests
import boto3
from datetime import datetime, timedelta

from multiprocessing import Process, Pool

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

import logging
logger = logging.getLogger('script')

from django.conf import settings
from forum.topic.models import Topic
from drf_spirit.models import MusicAlbum

BUCKET = 'in-boloindya'
s3_client = boto3.client('s3')

def run_command(video):
    try:
        if not video.get('question_video') or video.get('music_id'):
            return

        
        video_file = video.get('question_video').split("/")[-1]
        video_file_path = '/tmp/audio/%s'%(video_file)
        audio_file = video_file.split('.')[0] + '.aac'
        audio_file_path = '/tmp/audio/%s'%(audio_file)

        
        os.system('wget "%s" -O %s'%(video.get('question_video'), video_file_path))
        os.system('ffmpeg -i %s -vn -acodec copy %s -y'%(video_file_path, audio_file_path))

        response = s3_client.upload_file(audio_file_path, BUCKET, audio_file, ExtraArgs={'ACL': 'public-read'})
        s3_file_location = '/from_upload_panel/audio/' + audio_file
        print "s3 file location", s3_file_location
        s3_url = "https://%s.s3.amazonaws.com%s"%(BUCKET, s3_file_location)
        music = MusicAlbum.objects.create(**{
            'image_path': video.get('thumbnail'),
            'order_no': 15,
            'title': video.get('title'),
            'language_id': video.get('language_id'),
            'author_name': video.get('user__st__name', video.get('user__username')),
            's3_file_path': s3_url
        })
        Topic.objects.filter(id=video.get('id')).update(music_id=music.id, is_audio_extracted=True)
        print "respose", response
    except Exception as e:
        logger.info("Error while extracting audio from video: %s"%str(e))


def process_video_in_parallel(video_list):
    if not video_list:
        return 

    pool = Pool(processes=8)

    for video in video_list:
        pool.apply_async(run_command, args=(video, ))

    pool.close()
    pool.join()


def run(*args):
    os.system("mkdir /tmp/audio")
    process_video_in_parallel(Topic.objects.filter(is_audio_extracted=False).values('id', 'question_video', 'title', 'language_id', 'user__username',\
                                'user__st__name', 'thumbnail', 'music_id'))