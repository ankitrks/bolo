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
min_rec_to_cache = 90 # will cache atleast 6 pages(min_rec_to_cache / items_per_page). 
extra_pages_beyong_max_pages = 30
tt = None

start_total = time.time()
for each_language in language_options:
    start = time.time()

    list_page = 0
    paginated_data = []
    hash_df = pd.DataFrame.from_records(HashtagViewCounter.objects.filter(language=each_language[0])\
            .order_by('-hashtag__is_popular', '-hashtag__popular_date', '-view_count').values('hashtag__id', 'video_count'))
    while(list_page != None):
        page_data = hash_df[(list_page*items_per_page):((list_page+1)*items_per_page)]
        item_list = page_data['hashtag__id'].tolist()
        count_list = page_data['video_count'].tolist()
        
        if page_data.empty or list_page >= cache_max_pages:
            list_page = None
        else:
            paginated_data.append({ (list_page+1) : item_list })
            list_page += 1

            loop_counter = 0
            for each_rec in item_list:
                loop_counter +=1
                if count_list[loop_counter-1] <= min_rec_to_cache:
                    # print 'Skipping... not gte ' + str(min_rec_to_cache)
                    continue
                page = 1
                final_data = {}
                exclude_ids = []
                topics_df = pd.DataFrame.from_records(Topic.objects.filter(is_removed = False, is_vb = True, hash_tags__id = each_rec, \
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
                                tt = final_data
                                page = None
                            page = None
                    print str(each_language[1]) + ' >> hashtag ID: ' + str(each_rec) + '. total pages - ' + str(len(final_data))
                    print '================'
    end = time.time()
    print 'Runtime: Language ' + str(each_language[1]) + ' is ' + str(end - start)
print 'Runtime Total is ' + str(time.time() - start_total)


"""
 - Store data in redis....
 - If page no key is not present, check if key "remaining" is present...
 If no.... return blank.
 If Yes, get last_page_no = redis_data_language_wise['remaining']['last_page']
 last_page_data = redis_data_language_wise[last_page_no]
 topics = Topics.objects.exclude(id__in = last_page_data['id_list']).filter(vb_score__gte = last_page_data[scores][-1])
 this query will run everytime for the remaining objects. Paginate it.

 if page in Get parameter is 191 and redis has total 190 pages data then:
 new_page = page_no_from_get_param - last_page_no (191-190)
 pass topics in Paginated class with new_page
 
 Code:
 last_page_data = redis_data_language_wise[last_page_no]
 topics = Topics.objects.exclude(id__in = last_page_data['id_list']).filter(vb_score__gte = last_page_data[scores][-1])
 new_page = page_no_from_get_param - last_page_no #(191-190)

 paginator = Paginator(topics, items_per_page)
 topics_page = paginator.page(new_page)
 return VideoByteSerializer(topics_page)
"""
