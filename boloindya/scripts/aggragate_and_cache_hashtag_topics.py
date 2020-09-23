import os
import sys
import json
import csv

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from django.db import connections
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from datetime import datetime, timedelta
import threading
import pandas as pd

import connection
from boloindya.tasks import strip_tags

redis_cli = connection.redis()
SLOT_SIZE = 2
LANGUAGES_MAP = dict([(each_rec[0], each_rec[1]) for each_rec in settings.LANGUAGE_OPTIONS])

class AggregateHashtagTopics:
    def __init__(self, *args, **kwargs):
        self.all_keys = []
        self.all_selected_ids = {}

    def get_hashtag_topics(self):
        start_date = (datetime.now() - timedelta(days=settings.CATEGORY_N_HASHTAG_CACHE_TIMESPAN)).strftime('%Y-%m-%d')

        self.popular_hashtags = self.get_popular_hashtags()
        popular_hashtags_values = ','.join(["(%s, '%s')"%(row[0], row[1]) for row in self.popular_hashtags])

        query = """
            SELECT * FROM (
                (SELECT * from (
                    SELECT topic.id, topic.is_popular, topic.created_at, topic.vb_score, topic.user_id, topic.language_id,
                        hashtag.tonguetwister_id, topic.created_at::date as create_date, (extract(hour FROM topic.created_at)::int / {slot_size}) as hour_slot,
                        rank() OVER (PARTITION BY topic.language_id ORDER by topic.created_at::date desc, (extract(hour FROM topic.created_at)::int / {slot_size}) desc, vb_score desc) 
                    FROM forum_topic_topic topic
                    INNER JOIN forum_topic_topic_hash_tags hashtag on hashtag.topic_id = topic.id
                    INNER JOIN (VALUES {popular_hashtags_values}) as language_hashtag(hashtag_id, language_id) on 
                            language_hashtag.hashtag_id = hashtag.tonguetwister_id AND
                            (language_hashtag.language_id != '0' AND language_hashtag.language_id = topic.language_id OR language_hashtag.language_id = '0')
                    WHERE 
                        topic.is_popular and
                        topic.created_at::date > '{start_date}'
                    ) A where A.rank < 300)
                UNION ALL
                (SELECT * FROM (
                    SELECT topic.id, topic.is_popular, topic.created_at, topic.vb_score, topic.user_id, topic.language_id, 
                        hashtag.tonguetwister_id, topic.created_at::date as create_date, 0 as hour_slot,
                        rank() OVER (PARTITION BY topic.language_id ORDER by topic.created_at desc) 
                    FROM forum_topic_topic topic
                    INNER JOIN forum_topic_topic_hash_tags hashtag on hashtag.topic_id = topic.id
                    INNER JOIN (VALUES {popular_hashtags_values}) as language_hashtag(hashtag_id, language_id) on 
                            language_hashtag.hashtag_id = hashtag.tonguetwister_id AND
                            language_hashtag.language_id = topic.language_id AND
                            (language_hashtag.language_id != '0' AND language_hashtag.language_id = topic.language_id OR language_hashtag.language_id = '0')
                    WHERE 
                        not topic.is_popular AND
                        topic.created_at::date > '{start_date}'
                    ) B WHERE B.rank < 300)
            ) C ORDER BY is_popular DESC, create_date DESC, hour_slot DESC, vb_score DESC
            """.format( start_date=start_date, slot_size=SLOT_SIZE,
                            popular_hashtags_values=popular_hashtags_values)

        

        with connections['default'].cursor() as cr:
            cr.execute(query, [self.popular_hashtags, self.popular_hashtags])

            columns = [col[0] for col in cr.description]
            return [
                dict(zip(columns, row))
                for row in cr.fetchall()
            ]


    def get_popular_hashtags(self):
        with connections['default'].cursor() as cr:
            cr.execute("""
                SELECT A.id, A.language FROM (
                    SELECT tt.id, hvc.language, rank() OVER (PARTITION BY hvc.language ORDER BY tt.is_popular DESC, tt.order, tt.hash_counter DESC )
                    FROM forum_topic_hashtagviewcounter hvc 
                    INNER JOIN forum_topic_tonguetwister tt ON tt.id = hvc.hashtag_id
                    INNER JOIN drf_spirit_campaign campaign on campaign.hashtag_id = tt.id
                    WHERE 
                        NOT tt.is_blocked AND
                        now() BETWEEN campaign.active_from AND campaign.active_till AND is_active
                ) A WHERE A.rank <= 10
            """)

            return cr.fetchall()


    def create_pages(self, topic_list):
        all_topics_df = pd.DataFrame.from_records(topic_list)

        items_per_page = 15

        for language_id in all_topics_df.drop_duplicates('language_id')['language_id'].tolist():
            for hashtag_id in all_topics_df.drop_duplicates('tonguetwister_id')['tonguetwister_id'].tolist():

                topics_df = all_topics_df[all_topics_df['tonguetwister_id'] == hashtag_id]
                topics_df = topics_df[topics_df['language_id'] == language_id]

                if topics_df.empty:
                    continue

                exclude_ids = []
                page = 1

                paging_dict = {}

                while True:
                    if settings.ALLOW_DUPLICATE_USER_POST:
                        selected_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']')[:items_per_page]
                    else:
                        selected_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']').drop_duplicates('user_id')[:items_per_page]
                                        

                    if selected_df.empty:
                        break

                    selected_ids = selected_df['id'].tolist()
                    exclude_ids += map(str, selected_ids)

                    paging_dict[page] = json.dumps({ 'id_list' : selected_ids, 'scores' : selected_df['vb_score'].tolist() })

                    page += 1

                key = 'hashtag:'+str(hashtag_id)+':lang:'+str(language_id)
                self.all_selected_ids[key] = exclude_ids
                self.all_keys.append(key)
                redis_cli.hmset(key, paging_dict)

        return exclude_ids


    def create_csv(self):
        csvfile = open('/tmp/hashtag_topics.csv', 'wb')
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Language', 'HashTag', 'Is Popular', 'Created at', 'Score', 'Topic ID',
                'User', 'Title'])

        cr = connections['default'].cursor()


        for key, topic_ids in self.all_selected_ids.iteritems():
            language = LANGUAGES_MAP.get(str(key.split(':lang:')[-1]))
            hashtag_id = key.split(':lang:')[0].replace('hashtag:', '')
            values = ["(%s, %s, '%s', %s)"%(i, _id, language, hashtag_id) for i, _id in enumerate(topic_ids)]


            cr.execute("""
                SELECT selected_topic.language, hashtag.hash_tag, topic.is_popular, topic.created_at, 
                        topic.vb_score, topic.id, COALESCE(userprofile.name, userprofile.slug), topic.title::text
                FROM forum_topic_topic topic
                INNER JOIN forum_user_userprofile userprofile ON topic.user_id = userprofile.user_id
                INNER JOIN (VALUES {values}) as selected_topic (sequence, id, language, hashtag_id) ON topic.id = selected_topic.id
                LEFT JOIN forum_topic_tonguetwister hashtag ON hashtag.id = selected_topic.hashtag_id
                ORDER BY selected_topic.sequence
            """.format(values=','.join(values)))
            
            for row in cr.fetchall():
                updated_row = []
                for item in row:
                    if type(item) == unicode:
                        updated_row.append(strip_tags(item).encode('utf-8').strip())
                    else:
                        updated_row.append(item)

                writer.writerow(updated_row)

        csvfile.close()


    def send_topic_list_to_mail(self):
        # send_mail('Test', 'Testing', 'reports@boloindya.com', ['shadab.m@boloindya.com'])
        mail = EmailMessage('Test', 'Testing', 'reports@boloindya.com', ['shadab.m@boloindya.com'])
        csvfile = open('/tmp/hashtag_topics.csv', 'rb')
        mail.attach(csvfile.name, csvfile.read(), 'text/csv')
        mail.send()
        

def run():
    instance = AggregateHashtagTopics()
    topic_ids = instance.create_pages(instance.get_hashtag_topics())
    instance.create_csv()
    instance.send_topic_list_to_mail()
    
