from forum.category.models import Category
from drf_spirit.utils import language_options
from datetime import datetime
from redis_utils import *
from forum.topic.utils import update_redis_category_paginated_data

def run():
    start_total = datetime.now()
    for each_language in language_options:
        if not each_language[0] == '0':
            start = datetime.now()
            for each_category in Category.objects.filter(parent__isnull=False):
                final_data = update_redis_category_paginated_data(each_language[0],each_category.id)
                print final_data
            end = datetime.now()
            print 'Runtime: Language ' + str(each_language[1]) + ' is ' + str(end - start)
            print "\n\n\n\n"
    print 'Runtime Total is ' + str(datetime.now() - start_total)
