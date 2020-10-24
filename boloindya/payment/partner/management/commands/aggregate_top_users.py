from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import connections


def month_year_iter(start_month, start_year, end_month, end_year):
    while start_month < end_month or start_year < end_year:
        start_month += 1

        if start_month > 12:
            start_year += 1
            start_month = 1

        yield "%s-%s-01"%(start_year, str(start_month).zfill(2))


class Command(BaseCommand):
    help = "Create payments entries"

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

    def handle(self, *args, **options):
        cr = connections['default'].cursor()

        for temp_table in self.temp_tables:
            cr.execute(temp_table.get('create_query'))

        for month in month_year_iter(1, 2020, 10, 2020):
            month_date = datetime.strptime(month, "%Y-%m-%d")

            month_start = str(datetime.strptime("%s-%s-01"%(month_date.year, month_date.month-1), "%Y-%m-%d").date())
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
            INSERT INTO temp_top_user_follower_count(user_id, follower_count)  
                SELECT user_following_id AS user_id, count(*)
                FROM forum_user_follower
                WHERE created_at BETWEEN %s AND %s AND is_active
                GROUP BY user_following_id
        """, [month_start, month_end])

        cr.execute("""
            INSERT INTO temp_top_user_follower_count(user_id, follower_count)  
                SELECT user_following_id AS user_id, count(*)
                FROM forum_user_follower
                WHERE created_at BETWEEN %s AND %s AND is_active
                GROUP BY user_following_id
        """, [month_start, month_end])

        print("Temp table filled")
        
        cr.execute("""
            INSERT INTO partner_topuser(agg_month, boloindya_id, name, username, video_count, follower_count, playtime, view_count)
            SELECT A.agg_month::date as agg_month, A.boloindya_id, COALESCE(p.name, p.slug, '') as name, 
                COALESCE(p.slug, '') as username, A.video_count, A.follower_count, 0 as playtime, 0 as view_count FROM (
                    SELECT %s as agg_month, COALESCE(vc.user_id, fc.user_id) as boloindya_id, COALESCE(video_count, 0) as video_count, 
                        COALESCE(follower_count, 0) as follower_count FROM temp_top_user_video_count vc
                    FULL OUTER JOIN temp_top_user_follower_count fc on fc.user_id = vc.user_id
                ) A
            LEFT JOIN forum_user_userprofile p on p.user_id = A.boloindya_id
        """, [month_start + ' 00:00:00'])

        print("main table updated")

        cr.execute("DELETE FROM temp_top_user_video_count")
        cr.execute("DELETE FROM temp_top_user_follower_count")
    

