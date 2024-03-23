import subprocess
import os.path
from datetime import datetime
import os
import boto3
from django.conf import settings
from forum.topic.models import Topic
from django.db.models import Q


def run():
    all_vb_list = Topic.objects.filter(Q(vb_width__isnull=True)|Q(vb_height__isnull=True)|Q(vb_width=0)|Q(vb_height=0),is_vb=True,backup_url__isnull=False).exclude(backup_url='').order_by('-id')
    for each_vb in all_vb_list:
        try:
            print "start time:  ",datetime.now()
            output_dict={}
            cmd = ['ffprobe','-v','error' , '-show_entries','stream=width,height','-of','csv=p=0:s=x',str(each_vb.backup_url)]
            ps = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (output, stderr) = ps.communicate()
            widthandheight = output.replace('\n','').split('x')
            print widthandheight
            output_dict['pk'] = each_vb.id
            output_dict['url'] = each_vb.backup_url
            output_dict['width'] = widthandheight[0]
            output_dict['height'] = widthandheight[1]
            print output_dict
            Topic.objects.filter(pk=each_vb.id).update(vb_width = widthandheight[0],vb_height=widthandheight[1])
            print "End time:  ",datetime.now()
        except Exception as e:
            print e