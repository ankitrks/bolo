from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.conf import settings

import os
import sys
import json

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )



def month_year_iter(start_month, start_year, end_month, end_year):
    while start_month < end_month or start_year < end_year:
        start_month += 1

        if start_month > 12:
            start_year += 1
            start_month = 1

        yield "%s-%s-01"%(start_year, str(start_month).zfill(2))


class AggregateTopUsers:
    temp_tables = [{
        'name': 'temp_top_user_video_count',
        'create_query': """
                CREATE TABLE IF NOT EXISTS temp_top_user_video_count(
                   user_id integer,
                   video_count integer,
                   PRIMARY KEY(user_id)
                )
            """
    },{
        'name': 'temp_top_user_follower_count',
        'create_query': """
                CREATE TABLE IF NOT EXISTS temp_top_user_follower_count(
                   user_id integer,
                   follower_count integer,
                   PRIMARY KEY(user_id)
                )
            """
    },{
        'name': 'temp_top_user_playtime',
        'create_query': """
                CREATE TABLE IF NOT EXISTS temp_top_user_playtime(
                   user_id integer,
                   playtime real,
                   PRIMARY KEY(user_id)
                )
            """
    },{
        'name': 'temp_top_user_view_count',
        'create_query': """
                CREATE TABLE IF NOT EXISTS temp_top_user_view_count(
                   user_id integer,
                   view_count integer,
                   PRIMARY KEY(user_id)
                )
            """
    }]

    def start(self):
        cr = connections['default'].cursor()

        for temp_table in self.temp_tables:
            cr.execute(temp_table.get('create_query'))

        today = datetime.now()
        last_month = today.month - 1
        last_year = today.year

        print "last month", last_month, last_year

        if last_month == 0:
            last_month = 12
            last_year = today.year - 1

        print "last month", last_month, last_year

        for month in month_year_iter(last_month, last_year, today.month, today.year):
            print "month", month
            month_date = datetime.strptime(month, "%Y-%m-%d")

            previous_month = month_date.month - 1
            previous_year = month_date.year

            print "previous month", previous_month, previous_year

            if previous_month == 0:
                previous_month = 12
                previous_year = month_date.year - 1

            month_start = str(datetime.strptime("%s-%s-01"%(previous_year, previous_month), "%Y-%m-%d").date())
            month_end = str((datetime.strptime("%s-%s-01"%(month_date.year, month_date.month), "%Y-%m-%d") - timedelta(days=1)).date())

            self.aggregate(cr, month_start, month_end)


    def aggregate(self, cr, month_start, month_end):
        print("From:: ", month_start, " - ", month_end)

        cr.execute("DELETE FROM temp_top_user_video_count")
        cr.execute("DELETE FROM temp_top_user_follower_count")
        cr.execute("DELETE FROM temp_top_user_playtime")
        cr.execute("DELETE FROM temp_top_user_view_count")

        print("Temp DB cleared")

        cr.execute("""
            INSERT INTO temp_top_user_video_count(user_id, video_count)  
                SELECT user_id, count(1)
                FROM forum_topic_topic
                WHERE created_at BETWEEN %s AND %s
                GROUP BY  user_id
        """, [month_start, month_end])

        cr.execute("""
            INSERT INTO temp_top_user_follower_count(user_id, follower_count)  
                SELECT user_following_id AS user_id, count(*)
                FROM forum_user_follower
                WHERE created_at BETWEEN %s AND %s AND is_active
                GROUP BY user_following_id
        """, [month_start, month_end])

        cr.execute("""
            INSERT INTO temp_top_user_playtime(user_id, playtime)  
                SELECT t.user_id AS user_id, sum(p.playtime)/3600 as playtime
                FROM forum_user_videoplaytime p
                INNER JOIN forum_topic_topic t on p.video_id = t.id
                WHERE p."timestamp" BETWEEN %s AND %s AND NOT t.is_removed
                GROUP BY t.user_id
        """, [month_start, month_end])

        cr.execute("""
            INSERT INTO temp_top_user_view_count(user_id, view_count)  
                SELECT t.user_id AS user_id, count(*)
                FROM forum_topic_vbseen s
                INNER JOIN forum_topic_topic t on s.topic_id = t.id
                WHERE s.created_at BETWEEN %s AND %s AND NOT t.is_removed
                GROUP BY t.user_id
        """, [month_start, month_end])

        print("Temp table filled")
        
        cr.execute("""
            INSERT INTO partner_topuser(agg_month, boloindya_id, name, username, video_count, follower_count, playtime, view_count)
            SELECT A.agg_month::date as agg_month, A.boloindya_id, COALESCE(p.name, p.slug, '') as name, 
                COALESCE(p.slug, '') as username, A.video_count, A.follower_count, A.playtime, A.view_count FROM (
                    SELECT %s as agg_month, COALESCE(vc.user_id, fc.user_id, pt.user_id, vic.user_id) as boloindya_id, COALESCE(video_count, 0) as video_count, 
                        COALESCE(follower_count, 0) as follower_count, COALESCE(playtime, 0) as playtime, COALESCE(view_count, 0) as view_count
                    FROM temp_top_user_video_count vc
                    FULL OUTER JOIN temp_top_user_follower_count fc on fc.user_id = vc.user_id
                    FULL OUTER JOIN temp_top_user_playtime pt on pt.user_id = vc.user_id and pt.user_id = fc.user_id 
                    FULL OUTER JOIN temp_top_user_view_count vic on vic.user_id = vc.user_id and vic.user_id = pt.user_id and vic.user_id = fc.user_id 
                ) A
            LEFT JOIN forum_user_userprofile p on p.user_id = A.boloindya_id
        """, [month_start + ' 00:00:00'])

        print("main table updated")

        cr.execute("DELETE FROM temp_top_user_video_count")
        cr.execute("DELETE FROM temp_top_user_follower_count")
        cr.execute("DELETE FROM temp_top_user_playtime")
        cr.execute("DELETE FROM temp_top_user_view_count")
    

def run():
    AggregateTopUsers().start()
