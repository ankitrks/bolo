import os
import sys
import json
import csv

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from django.db import connections
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, timedelta
import threading
import pandas as pd

import connection

redis_cli = connection.redis()
SLOT_SIZE = 2

class AggregateHashtagTopics:
    def get_hashtag_topics(self, language_id):
        start_date = (datetime.now() - timedelta(days=settings.CATEGORY_N_HASHTAG_CACHE_TIMESPAN)).strftime('%Y-%m-%d')

        self.popular_hashtags = get_popular_hashtags(language_id)

        query = """
                (SELECT id, is_popular, created_at, created_at::date as create_date, (extract(hour FROM created_at)::int / {slot_size}) as hour_slot,
                      vb_score, user_id, hashtag.tonguetwister_id as hashtag_id
                FROM forum_topic_topic topic
                INNER JOIN forum_topic_topic_hash_tags hashtag on hashtag.topic_id = topic.id
                WHERE 
                    language_id = '{language_id}' and
                    is_popular and
                    created_at::date > '{start_date}' and
                    hashtag.tonguetwister_id in {popular_hashtag_ids}
                ORDER by hashtag.tonguetwister_id, created_at::date desc, (extract(hour FROM created_at)::int / {slot_size}) desc, vb_score desc)
                UNION ALL
                (SELECT id, is_popular, created_at, created_at::date as create_date, (extract(hour FROM created_at)::int / {slot_size}) as hour_slot,
                  vb_score, user_id, hashtag.tonguetwister_id as hashtag_id
                FROM forum_topic_topic topic
                INNER JOIN forum_topic_topic_hash_tags hashtag on hashtag.topic_id = topic.id
                WHERE 
                    language_id = '{language_id}' and
                    not is_popular and
                    created_at::date > '{start_date}' and
                    hashtag.tonguetwister_id in {popular_hashtag_ids} 

                ORDER BY hashtag.tonguetwister_id, created_at LIMIT 200)
            """.format(language_id=language_id, start_date=start_date, slot_size=SLOT_SIZE,
                            popular_hashtag_ids='%s')

        with connections['default'].cursor() as cr:
            cr.execute(query, [self.popular_hashtags, self.popular_hashtags])

            columns = [col[0] for col in cr.description]
            return [
                dict(zip(columns, row))
                for row in cr.fetchall()
            ]


    def get_popular_hashtag(self, language_id):
        with connections['default'].cursor() as cr:
            cr.execute("""
                SELECT tt.id
                FROM forum_topic_hashtagviewcounter hvc 
                INNER JOIN forum_topic_tonguetwister tt ON tt.id = hvc.hashtag_id
                WHERE 
                    hvc.language = %s AND
                    NOT tt.is_blocked
                ORDER BY tt.is_popular DESC, tt.order, tt.hash_counter DESC
                LIMIT 10
            """, [language_id])

            return [row[0] for row in cr.fetchall()]


    def create_pages(self, topic_list):
        all_topics_df = pd.DataFrame.from_records(topic_list)

        items_per_page = 15
        exclude_ids = []
        page = 1

        paging_dict = {}

        for language_id in self.total_language_ids:
            for hashtag_id in self.popular_hashtags:
                print("TT id ", hashtag_id)
                topics_df = all_topics_df[all_topics_df.hashtag_id = hashtag_id]
                print(" TT dataframe ", topics_df)
                while True:
                    if settings.ALLOW_DUPLICATE_USER_POST:
                        selected_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']')\
                                        .nlargest(items_per_page, 'vb_score', keep = 'first')
                    else:
                        selected_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']').drop_duplicates('user_id')\
                                        .nlargest(items_per_page, 'vb_score', keep = 'first')

                    if selected_df.empty:
                        break

                    selected_ids = selected_df['id'].tolist()
                    # print("======== Page - ", page)
                    # print(selected_df)
                    exclude_ids += map(str, selected_ids)

                    paging_dict[page] = json.dumps({ 'id_list' : selected_ids, 'scores' : selected_df['vb_score'].tolist() })

                    page += 1

                # key = 'hashtag:'+str(each_rec)+':lang:'+str(language_id)
                key = 'hashtag:'+str(1)+':lang:'+str(1)
                print("key == ", key)
                redis_cli.hmset(key, paging_dict)

        return exclude_ids


    def create_csv(self, topic_ids):
        values = ['(%s, %s)'%(i, _id) for i, _id in enumerate(topic_ids)]

        with connections['default'].cursor() as cr:
            cr.execute("""
                SELECT topic.id, COALESCE(userprofile.name, userprofile.slug), topic.title::text, topic.vb_score
                FROM forum_topic_topic topic
                INNER JOIN forum_user_userprofile userprofile ON topic.user_id = userprofile.user_id
                INNER JOIN (VALUES {values}) as selected_topic (sequence, id) ON topic.id = selected_topic.id
                ORDER BY selected_topic.sequence
            """.format(values=','.join(values)))

            with open('/tmp/hashtag_topics.csv', 'wb') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                for row in cr.fetchall():
                    updated_row = []
                    for item in row:
                        if type(item) == unicode:
                            updated_row.append(item.encode('utf-8').strip())
                        else:
                            updated_row.append(item)

                    writer.writerow(updated_row)


    def send_topic_list_to_mail():
        send_mail('Test', 'Testing', 'reports@boloindya.com', ['shadab.m@boloindya.com'])
            

def run():
    topic_ids = create_pages(get_hashtag_topics('1'))
    create_csv(topic_ids)
    # print("=============== ")
    # key = 'hashtag:'+str(1)+':lang:'+str(1)
    # print(redis_cli.hgetall(key))
    # send_topic_list_to_mail()

