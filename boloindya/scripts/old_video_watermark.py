import subprocess
import os.path
from datetime import datetime
import os
import boto3
from django.conf import settings
from forum.topic.models import Topic

def ffmpeg(*cmd):
    try:
        subprocess.check_output(['ffmpeg'] + list(cmd))
    except subprocess.CalledProcessError:
        return False
    return True

def upload_media(media_file,filename):
    try:
        client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
        filenameNext= str(filename).split('.')
        final_filename = str(filenameNext[0])+"."+str(filenameNext[1])
        client.put_object(Bucket=settings.BOLOINDYA_AWS_BUCKET_NAME, Key='watermark/' + final_filename, Body=media_file,ACL='public-read')
        filepath = "https://s3.amazonaws.com/"+settings.BOLOINDYA_AWS_BUCKET_NAME+"/watermark/"+final_filename
        return filepath
    except:
        return None


def run():
    start_date = datetime(2020,02,14)
    all_vb_list = Topic.objects.filter(is_vb=True,date__lt = start_date,has_downloaded_url = False).order_by('-id')
    counter=0
    for each_vb in all_vb_list:
        try:
            counter+=1
            print "start time:  ",datetime.now()
            filename_temp = str(counter)+"_"+each_vb.backup_url.split('/')[-1]
            filename = each_vb.backup_url.split('/')[-1]
            cmd = ['ffmpeg','-i', each_vb.backup_url, '-vf',"[in]scale=540:-1,drawtext=text='@"+each_vb.user.username+"':x=10:y=H-th-20:fontsize=16:fontcolor=white[out]",settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp]
            ps = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (output, stderr) = ps.communicate()
            cmd = 'ffmpeg -i '+settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp+' -ignore_loop 0 -i '+settings.PROJECT_PATH+"/boloindya/media/img/boloindya_white.gif"+' -filter_complex "[1:v]format=yuva444p,scale=120:120,setsar=1,rotate=0:c=white@0:ow=rotw(0):oh=roth(0) [rotate];[0:v][rotate] overlay=10:(main_h-overlay_h+5):shortest=1" -codec:a copy -y '+settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename
            subprocess.call(cmd,shell=True)
            downloaded_url = upload_media(open(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename),filename)
            if downloaded_url:
                Topic.object.filter(pk=each_vb.id).update(downloaded_url = downloaded_url,has_downloaded_url = True)
            if os.path.exists(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename):
                os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp)
                os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename)
            print "bye"
            print "End time:  ",datetime.now()
        except Exception as e:
            print e