import boto3
from django.conf import settings
from forum.topic.models import Topic
import re




def check_file_name_validation(filename,username):
    if check_filename_valid(filename):
        return filename
    else:
        import time
        epoch_time = int(round(time.time() * 1000))
        file_name_words = filename.split('_')
        file_extension = file_name_words[-1].split('.')[-1]
        # print 'old_file_name:  ', filename
        # print 'new_file_name:   ',username+'_'+str(epoch_time)+'.'+file_extension.lower()
        return username+'_'+str(epoch_time)+'.'+file_extension


def check_filename_valid(filename):
    if re.match(r"^[A-Za-z0-9_.-]+(:?\.mp4|\.mov|\.3gp)+$", filename):
        return True
    else:
        return False

def rename_s3_file(old_key,new_key):
    session = boto3.Session(aws_access_key_id=settings.BOLOINDYA_AWS_ACCESS_KEY_ID,     aws_secret_access_key=settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    s3.Object(settings.BOLOINDYA_AWS_BUCKET_NAME, new_key, ACL='public-read').copy_from(CopySource=old_key)
    s3.Object(settings.BOLOINDYA_AWS_BUCKET_NAME, old_key).delete()

def run():
    for each_topic in Topic.objects.filter(is_vb=True).order_by('-id')[:1]:
        if each_topic.backup_url:
            try:
                filename = each_topic.backup_url.split('/')[-1]
                valid_filename = check_file_name_validation(filename,each_topic.user.username)
                if not filename== valid_filename:
                    old_url = each_topic.backup_url
                    new_url = '/'.join(each_topic.backup_url.split('/')[:len(each_topic.backup_url.split('/'))-1])+'/'+valid_filename
                    print 'old_url   :', each_topic.backup_url
                    print 'new_url   :', new_url
                    old_key=settings.BOLOINDYA_AWS_BUCKET_NAME+'/'+each_topic.backup_url.split('https://boloindyapp-prod.s3.amazonaws.com/')[1]
                    new_key=new_url.split('https://boloindyapp-prod.s3.amazonaws.com/')[1]
                    print 'old_key:  ',old_key
                    print 'new_key:  ',new_key
                    rename_s3_file(old_key,new_key)
                    Topic.objects.filter(pk=each_topic.id).update(backup_url=new_url,old_backup_url=old_url)
            except Exception as e:
                print e
                