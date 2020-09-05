from forum.topic.models import Topic,TongueTwister
from forum.comment.models import Comment
from datetime import datetime
from django.db.models import Q,F
from django.db.models import Sum
import re
from HTMLParser import HTMLParser 

def run():

    class MLStripper(HTMLParser):
        def __init__(self):
            self.reset()
            self.fed = []
        def handle_data(self, d):
            self.fed.append(d)
        def get_data(self):
            return ''.join(self.fed)

    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    def find(string, char):
        return [i for i, ltr in enumerate(string) if ltr == char]

    def check_space_before_hash(string):
        if "#" in string:
            indexes =find(string,"#")
            final_indexes=[]
            for each_index in indexes:
                if not string[each_index-1].isspace() and each_index:
                    final_indexes.append(each_index)

            if final_indexes:
                string = string[:final_indexes[0]]+" "+string[final_indexes[0]:]
                string=check_space_before_hash(string)
            string = check_space_before_mention(string)
        return string.strip()

    def check_space_before_mention(string):
        if "@" in string:
            indexes =find(string,"@")
            final_indexes=[]
            for each_index in indexes:
                if not string[each_index-1].isspace() and each_index:
                    final_indexes.append(each_index)

            if final_indexes:
                string = string[:final_indexes[0]]+" "+string[final_indexes[0]:]
                string=check_space_before_mention(string)
        return string.strip()

    topic_hash_tag_counter = 0
    all_topics = Topic.objects.filter(title__icontains="#", first_hash_tag__isnull = True).values_list('pk', flat = True).order_by('-date')
    for each_topic_id in all_topics:
        print "#######################topic_hash_tag_counter   ",topic_hash_tag_counter,"/",len(all_topics),"      ##########################"
        topic_hash_tag_counter+=1
        try:
            each_topic = Topic.objects.get(pk = each_topic_id)
            title = check_space_before_hash(strip_tags(each_topic.title))
            hash_tag = title.split()
            # print hash_tag
            if hash_tag:
                for index, value in enumerate(hash_tag):
                    if value.startswith("#"):
                        tag = TongueTwister.objects.get(hash_tag__iexact=value.strip('#'))
                        print tag, list(each_topic.hash_tags.all())
                        if tag in list(each_topic.hash_tags.all()):
                            print each_topic.title
                            each_topic.first_hash_tag = tag
                            each_topic.save()
                            print "#################"
                            break
        except Exception as e:
            print e
            
