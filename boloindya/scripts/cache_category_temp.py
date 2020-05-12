import time
import pandas as pd
language_options = (
    ('0', "All"),
    ('1', "English"),
    ('2', "Hindi"),
    ('3', "Tamil"),
    ('4', "Telugu"),
    ('5', "Bengali"),
    ('6', "Kannada"),
    ('7', "Malayalam"),
    ('8', "Gujarati"),
    ('9', "Marathi"),
    ('10', "Punjabi"),
    ('11', "Odia"),

)

items_per_page = 15
min_count_per_page = 10
cache_max_pages = 200
extra_pages_beyong_max_pages = 30

start_total = time.time()
for each_language in language_options:
    start = time.time()
    for each_rec in Category.objects.all():
        page = 1
        final_data = {}
        exclude_ids = []
        topics_df = pd.DataFrame.from_records(Topic.objects.filter(is_removed = False, is_vb = True, m2mcategory = each_rec, \
                language_id = each_language[0]).order_by('-vb_score').values('id', 'user_id', 'vb_score'))
        if topics_df.empty:
            final_data[page] = []
        else:
            while(page != None):
                updated_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']').drop_duplicates('user_id')\
                        .nlargest(items_per_page, 'vb_score', keep='last')
                id_list = updated_df['id'].tolist()
                if len(id_list) > min_count_per_page and page <= cache_max_pages:
                    exclude_ids.extend( map(str, id_list) )
                    if id_list:
                        final_data[page] = { 'id_list' : id_list, 'scores' : updated_df['vb_score'].tolist() }
                        page += 1
                    else:
                        page = None
                else:
                    remaining_count = len(topics_df) - len(exclude_ids) - len(updated_df)
                    if remaining_count <= items_per_page * extra_pages_beyong_max_pages:
                        remaining_page_no = (remaining_count / items_per_page) + 1
                        if (remaining_count % items_per_page) > 0:
                            remaining_page_no += 1
                        while( remaining_page_no > 0):
                            updated_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']')[:items_per_page]
                            id_list = updated_df['id'].tolist()
                            exclude_ids.extend( map(str, id_list) )
                            remaining_page_no -= 1
                            if id_list:
                                final_data[page] = { 'id_list' : id_list, 'scores' : updated_df['vb_score'].tolist() }
                                page += 1
                            else:
                                page = None
                    else:
                        # if remaining items are too many (more than "extra_pages_beyong_max_pages" pages).
                        # these will be filtered realtime then.
                        final_data['remaining'] = {'remaining_count' : remaining_count, 'last_page' : page - 1}
                        page = None
                    page = None
    end = time.time()
    print 'Runtime: Language ' + str(each_language[1]) + ' is ' + str(end - start)
print 'Runtime Total is ' + str(time.time() - start_total)
