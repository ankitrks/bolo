import subprocess
import os.path
from datetime import datetime
import os
import boto3
from django.conf import settings
from forum.topic.models import Topic
import re
import time

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

def check_file_name_validation(filename,username):
    if check_filename_valid(filename):
        return filename
    else:
        import time
        epoch_time = int(round(time.time() * 1000))
        file_name_words = filename.split('_')
        file_extension = file_name_words[-1].split('.')[-1]
        print 'old_file_name:  ', filename
        print 'new_file_name:   ',username+'_'+str(epoch_time)+'.'+file_extension.lower()
        return username+'_'+str(epoch_time)+'.'+file_extension


def check_filename_valid(filename):
    if re.match(r"^[A-Za-z0-9_.-]+(:?\.mp4|\.mov|\.3gp)+$", filename):
        return True
    else:
        return False

def run():
    start_date = datetime(2020,02,14)
    all_vb_list = Topic.objects.filter(is_vb=True,date__gt = start_date,has_downloaded_url = False,is_removed=False).order_by('-id')
    counter=0
    for each_vb in all_vb_list:
        try:
            counter+=1
            print "start time:  ",datetime.now()
            valid_file_name = check_file_name_validation(each_vb.backup_url.split('/')[-1],each_vb.user.username)
            filename_temp = str(counter)+"_"+valid_file_name
            filename = valid_file_name
            cmd = ['ffmpeg','-i', each_vb.backup_url, '-vf',"[in]scale=540:-1,drawtext=text='@"+each_vb.user.username+"':x=10:y=H-th-20:fontsize=18:fontcolor=white[out]",settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp]
            ps = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (output, stderr) = ps.communicate()
            cmd = 'ffmpeg -i '+settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp+' -ignore_loop 0 -i '+settings.PROJECT_PATH+"/boloindya/media/img/boloindya_white.gif"+' -filter_complex "[1:v]format=yuva444p,scale=140:140,setsar=1,rotate=0:c=white@0:ow=rotw(0):oh=roth(0) [rotate];[0:v][rotate] overlay=10:(main_h-overlay_h+10):shortest=1" -codec:a copy -y '+settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename
            subprocess.call(cmd,shell=True)
            downloaded_url = upload_media(open(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename),filename)
            if downloaded_url:
                Topic.objects.filter(pk=each_vb.id).update(downloaded_url = downloaded_url,has_downloaded_url = True)
            if os.path.exists(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename):
                os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp)
                os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename)
            print "bye"
            print "End time:  ",datetime.now()
        except Exception as e:
            try:
                os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename_temp)
            except:
                pass
            try:
                os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename)
            except:
                pass
            print e
    print counter