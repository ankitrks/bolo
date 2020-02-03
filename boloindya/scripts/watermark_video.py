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
    start_date = datetime(2020,01,13)
    all_vb_list = Topic.objects.filter(is_popular=True,downloaded_url__isnull=True,date__gte=start_date).order_by('-id')
    for each_vb in all_vb_list:
        try:
            print "start time:  ",datetime.now()
            filename = each_vb.backup_url.split('/')[-1]
            cmds2 = ['ffmpeg','-i',each_vb.backup_url , '-vf',"[in]drawtext=text='Bolo Indya':x=10:y=H-th-35:fontsize=16:fontcolor=white,drawtext=text='@"+each_vb.user.username+"':x=10:y=H-th-20:fontsize=12:fontcolor=white[out]",settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename]
            ps2 = subprocess.Popen(cmds2, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (output, stderr) = ps2.communicate()
            downloaded_url = upload_media(open(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename),filename)
            if downloaded_url:
                each_vb.downloaded_url = downloaded_url
                each_vb.save()
            if os.path.exists(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename):
                os.remove(settings.PROJECT_PATH+"/boloindya/scripts/watermark/"+filename)
            # print "bye"
            print "End time:  ",datetime.now()
        except Exception as e:
            print e