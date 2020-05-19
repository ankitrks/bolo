import urllib2
import re
from forum.topic.models import Topic
from forum.user.models import UserProfile
from django.db.models import F,Q

def run():
    lambda_url = "http://in-boloindya.s3-website.ap-south-1.amazonaws.com/200x300"
    ## TODO: It has to be a dynamic distribution (among 5 cloudfront utls).
    ## Cloud front utls set will be different for "in-boloindya" and "in-boloindya" ## TODO: MOve to settings
    cloundfront_url = "http://d3g5w10b1w6clr.cloudfront.net/200x300"

def check_url(file_path):
    try:
        u = urllib2.urlopen(str(file_path))
        print u
        return "200"
    except Exception as e:
        print e,file_path
        return "403"

def get_modified_url(old_url,new_url_domain):
    if old_url:
        regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
        find_urls_in_string = re.compile(regex, re.IGNORECASE)
        url = find_urls_in_string.search(old_url)
        print str(old_url.replace(str(url.group()), new_url_domain))
        return str(old_url.replace(str(url.group()), new_url_domain))


    for each_video in Topic.objects.filter(is_vb=True,is_removed=False):
        lmabda_video_thumbnail_url = get_modified_url(each_video.question_image,lambda_url)
        check_url(lmabda_video_thumbnail_url)
        lmabda_cloudfront_url = get_modified_url(each_video.question_image,cloundfront_url)
        check_url(lmabda_cloudfront_url)

    for each_user in UserProfile.objects.exclude( cover_pic = '',profile_pic = ''):
        if each_user.cover_pic:
            lmabda_video_thumbnail_url = get_modified_url(each_user.cover_pic,lambda_url)
            check_url(lmabda_video_thumbnail_url)
            lmabda_cloudfront_url = get_modified_url(each_user.cover_pic,cloundfront_url)
            check_url(lmabda_cloudfront_url)
        if each_user.profile_pic:
            lmabda_video_thumbnail_url = get_modified_url(each_user.profile_pic,lambda_url)
            check_url(lmabda_video_thumbnail_url)
            lmabda_cloudfront_url = get_modified_url(each_user.profile_pic,cloundfront_url)
            check_url(lmabda_cloudfront_url)



