from forum.user.models import AndroidLogs
from forum.user.models import UserProfile
from time import sleep
from datetime import datetime
import urllib2
import json

def run():
    all_logs = AndroidLogs.objects.filter(log_type ='user_ip').distinct('user_id').order_by('-user_id')
    total_elements = all_logs.count()
    i=0
    for each_log in all_logs:
        print "##############    ",i,"/",total_elements,"      ############"
        userprofile = UserProfile.objects.filter(user_id = each_log.user.id)
        if not userprofile[0].state_name or not userprofile[0].city_name:
            url = 'http://ip-api.com/json/'+str(each_log.logs)
            response = urllib2.urlopen(url).read()
            json_response = json.loads(response)
            # print json_response['city'],json_response['regionName']
            userprofile.update(state_name = json_response['regionName'],city_name = json_response['city'])
            sleep(2)
        i+=1