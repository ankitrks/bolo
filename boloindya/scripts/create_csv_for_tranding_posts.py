
import os
import sys
import json
import csv

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from django.db import connections
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import threading
import pandas as pd

import connection
from tasks import strip_tags

from forum.topic.models import Topic, VBseen

LANGUAGES_MAP = dict([(each_rec[0], each_rec[1]) for each_rec in settings.LANGUAGE_OPTIONS])

redis_cli = connection.redis()

class CreateCSVForTrending:
    def __init__(self, *args, **kwargs):
        self.all_keys = []
        self.all_selected_ids = {}


    def get_tranding_topics(self):
        user = User.objects.get(username='noobmaster69')

        exclude_list = list(VBseen.objects.filter(user_id = user.id).distinct('topic_id').values_list('topic_id', flat = True))

        start_date = datetime.now()
        end_date = (start_date - timedelta(hours=settings.TRENDING_CACHE_TIMESPAN*24))

        selected_ids = []

        for language_id in ['1', '2']:

            topics = Topic.objects.filter(is_vb = True, is_removed = False, 
                language_id__in = language_id, is_popular = True, date__gte=end_date.date(), date__lte=start_date.date())\
                .exclude(pk__in = exclude_list).order_by('-id', '-vb_score').values('id', 'user_id', 'vb_score','date')[:1000]

            if len(topics) < 20:
                topics = Topic.objects.filter(is_vb = True, is_removed = False, 
                    language_id__in = language_id, is_popular = True, date__lte=end_date.date())\
                    .exclude(pk__in = exclude_list).order_by('-id', '-vb_score').values('id', 'user_id', 'vb_score','date')[:1000]


            topics_df = pd.DataFrame.from_records(topics)

            exclude_ids = []
            items_per_page = 15
            max_page_creation_limit = 2
            page_created = 0

            while page_created < max_page_creation_limit:
                if settings.ALLOW_DUPLICATE_USER_POST:
                    selected_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']')\
                            .nlargest(items_per_page, 'vb_score', keep = 'first')
                else:
                    selected_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']').drop_duplicates('user_id')\
                            .nlargest(items_per_page, 'vb_score', keep = 'first')

                if selected_df.empty:
                    break

                id_list = selected_df['id'].tolist()
                exclude_ids += map(str, id_list)

                selected_ids += id_list

                page_created += 1

        return selected_ids



    def create_csv(self, topic_ids):
        print "topic_ids", topic_ids

        csvfile = open('/tmp/trending_topics.csv', 'wb')
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Language', 'Is Popular', 'Created at', 'Score', 'Topic ID',
                'User', 'Title'])

        cr = connections['default'].cursor()

        values = ["(%s, %s)"%(i, _id) for i, _id in enumerate(topic_ids)]
        language_values = ["('%s', '%s')"%(_id, name) for _id, name in LANGUAGES_MAP.iteritems()]



        cr.execute("""
            SELECT language.name, topic.is_popular, topic.created_at, 
                    topic.vb_score, topic.id, COALESCE(userprofile.name, userprofile.slug), topic.title::text
            FROM forum_topic_topic topic
            INNER JOIN forum_user_userprofile userprofile ON topic.user_id = userprofile.user_id
            INNER JOIN (VALUES {values}) as selected_topic (sequence, id) ON topic.id = selected_topic.id
            INNER JOIN (VALUES {language_values}) as language (id, name) ON language.id = topic.language_id
            ORDER BY selected_topic.sequence
        """.format(values=','.join(values), language_values=','.join(language_values)))
        
        for row in cr.fetchall():
            updated_row = []
            for item in row:
                if type(item) == unicode:
                    updated_row.append(strip_tags(item).encode('utf-8').strip())
                else:
                    updated_row.append(item)

            writer.writerow(updated_row)

        csvfile.close()


def run():
    instance = CreateCSVForTrending()
    topic_ids = instance.create_csv(instance.get_tranding_topics())
    # instance.create_csv()
    # instance.send_topic_list_to_mail()
