import subprocess
import os.path
import os
from django.conf import settings

def run():
    REDIS_PORT = 6379
    deleting_key_pattern=['bi:hashtag:*:lang:*','bi:cat:*:lang:*','bi:lang:*','bi:follow_post:*','bi:lang:*:popular_post:*']
    for each_pattern in deleting_key_pattern:
        myCmd = 'redis-cli -h '+settings.REDIS_HOST+' -p '+REDIS_PORT+' KEYS "'+each_pattern+'" | xargs redis-cli DEL'
        print os.system(myCmd)