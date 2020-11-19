from django.db import connections

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def execute_query(query, params=None):
    cursor = connections['default'].cursor()
    if params:
        print "query", cursor.mogrify(query, params)
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    return dictfetchall(cursor)