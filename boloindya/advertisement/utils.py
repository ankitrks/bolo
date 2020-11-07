from django.db import connections

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def query_fetch_data(query, params=None):
    cursor = connections['default'].cursor()
    
    if not params:
        params = []

    print "query", cursor.mogrify(query, params)
    cursor.execute(query, params)
    return dictfetchall(cursor)


def convert_to_dict_format(item):
    _dict = {}
    for key, val in item.iteritems():
        key_parts = key.split('__', 1)

        if len(key_parts) == 2:
            if _dict.get(key_parts[0]):
                _dict[key_parts[0]].update({key_parts[1]: val})
            else:
                _dict[key_parts[0]] = {key_parts[1]: val}
        elif len(key_parts) == 1:
            _dict[key_parts[0]] = val


    for key, val in _dict.iteritems():
        if type(val) == dict:
            _dict[key] = convert_to_dict_format(val)

    return _dict