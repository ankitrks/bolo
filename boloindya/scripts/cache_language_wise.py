from drf_spirit.utils import language_options
from datetime import datetime
from redis_utils import *
from forum.topic.utils import update_redis_language_paginated_data

def run():
    start_total = datetime.now()
    for each_language in language_options:
        if not each_language[0] == '0':
            start = datetime.now()
            final_data = update_redis_language_paginated_data(each_language[0])
            print final_data
            end = datetime.now()
            print 'Runtime: Language ' + str(each_language[1]) + ' is ' + str(end - start)
            print "\n\n\n\n"
    print 'Runtime Total is ' + str(datetime.now() - start_total)
