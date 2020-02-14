INCLUDE_SPELLING  =True 
HAYSTACK_INCLUDE_SPELLING = True
#to autocomplete the text user
sqs = SearchQuerySet().models(UserProfile).autocomplete(**{'text':'bolo'}).filter(is_removed=False)

#to autocomplete the text topic
sqs = SearchQuerySet().models(Topic).autocomplete(**{'text':'bolo'}).filter(is_removed=False)

#to autocomplete the hashtag
sqs = SearchQuerySet().models(TongueTwister).autocomplete(**{'text':'bolo'})

#to search TOPIC
sqs =  SearchQuerySet().models(Topic).raw_search('maaz')

#to search user
sqs = SearchQuerySet().models(UserProfile).raw_search('maaz')

#to search hashtag
sqs = SearchQuerySet().models(TongueTwister).raw_search('maaz')

#to get suggestion

sqs = SearchQuerySet().auto_query('maa').spelling_suggestion()
 # u'maaz

# ...or...
sqs = SearchQuerySet().spelling_suggestion('maa')
# u'maaz'