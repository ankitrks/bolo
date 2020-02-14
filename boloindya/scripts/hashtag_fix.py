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
        return string

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
        return string

    TongueTwister.objects.all().update(hash_counter=0)
    topic_remove = 0
    all_topic = Topic.objects.exclude(hash_tags=None)
    for each_topic in all_topic:
        print "#######################topic_remove   ",topic_remove,"/",len(all_topic),"      ##########################"
        topic_remove+=1
        if each_topic.hash_tags.all():
            for each_tag in each_topic.hash_tags.all():
                    each_topic.hash_tags.remove(each_tag)
    comment_remove = 0
    all_comment = Comment.objects.exclude(hash_tags=None)
    for each_comment in all_comment:
        print "#######################comment_remove   ",comment_remove,"/",len(all_comment),"      ##########################"
        comment_remove+=1
        if each_comment.hash_tags.all():
            for each_tag in each_comment.hash_tags.all():
                    each_comment.hash_tags.remove(each_tag)


    post_counter = 0
    all_topics = Topic.objects.filter(title__icontains="#")
    for each_topic in all_topics:
        print "#######################post_counter   ",post_counter,"/",len(all_topics),"      ##########################"
        # print each_topic.title   
        # print check_space_before_hash(strip_tags(each_topic.title))
        title = check_space_before_hash(strip_tags(each_topic.title))
        Topic.objects.filter(pk=each_topic.id).update(title=title)
        post_counter+=1

    comment_counter = 0
    all_comments = Comment.objects.filter(Q(comment__icontains="#")|Q(comment_html__icontains="#")|Q(comment__icontains="@")|Q(comment_html__icontains="@"))

    for each_comment in all_comments:
        # print each_comment.comment_html
        # print check_space_before_hash(strip_tags(each_comment.comment_html))
        print "#######################all_comments   ",comment_counter,"/",len(all_comments),"      ##########################"
        comment_html = check_space_before_hash(strip_tags(each_comment.comment_html))
        comment = check_space_before_hash(strip_tags(each_comment.comment_html))
        Comment.objects.filter(pk=each_comment.id).update(comment_html=comment_html,comment=comment)
        comment_counter+=1

    topic_hash_tag_counter = 0
    all_topics = Topic.objects.filter(title__icontains="#")
    for each_topic in all_topics:
        print "#######################topic_hash_tag_counter   ",topic_hash_tag_counter,"/",len(all_topics),"      ##########################"
        topic_hash_tag_counter+=1
        try:
            title = each_topic.title
            hash_tag = title.split()
            # print hash_tag
            if hash_tag:
                for index, value in enumerate(hash_tag):
                    if value.startswith("#"):
                        hash_tag[index]='<a href="/get_challenge_details/?ChallengeHash='+value.strip('#')+'">'+value+'</a>'
                        tag,is_created = TongueTwister.objects.get_or_create(hash_tag=value.strip('#'))
                        if not is_created:
                            tag.hash_counter = F('hash_counter')+1
                        tag.save()
                        each_topic.hash_tags.add(tag)
                title = " ".join(hash_tag)
                title = title[0].upper()+title[1:]
                Topic.objects.filter(pk=each_topic.id).update(title = title)
        except Exception as e:
            print e
            


    all_comment = Comment.objects.filter(Q(comment__icontains="#")|Q(comment_html__icontains="#"))
    regex = r"#\w+"
    comment_hash_tag_counter = 0
    for each_comment in all_comment:
        print "#######################comment_hash_tag_counter   ",comment_hash_tag_counter,"/",len(all_comment),"      ##########################"
        comment_hash_tag_counter+=1
        try:
            comment = each_comment.comment
            hash_tag = comment.split()
            print hash_tag
            if hash_tag:
                for index, value in enumerate(hash_tag):
                    if value.startswith("#"):
                        hash_tag[index]='<a href="/get_challenge_details/?ChallengeHash='+value.strip('#')+'">'+value+'</a>'
                        tag,is_created = TongueTwister.objects.get_or_create(hash_tag=value.strip('#'))
                        if not is_created:
                            tag.hash_counter = F('hash_counter')+1
                        tag.save()
                        each_comment.hash_tags.add(tag)
                comment = " ".join(hash_tag)
                Comment.objects.filter(pk=each_comment.id).update(comment_html=comment,comment=comment)

        except Exception as e:
            print e

    all_comments = Comment.objects.filter(Q(comment__icontains="@")|Q(comment_html__icontains="@"))
    comment_mention_counter = 0
    for each_comment in all_comments:
        print "#######################comment_mention_counter   ",comment_mention_counter,"/",len(all_comments),"      ##########################"
        comment_mention_counter+=1
        comment =each_comment.comment
        try:
            mention_tag=[mention for mention in comment.split() if mention.startswith("@")]
            if mention_tag:
                for each_mention in mention_tag:
                    try:
                        user = User.objects.get(username=each_mention.strip('@'))
                        comment = comment.replace(each_mention,'<a href="/timeline/?username='+each_mention.strip('@')+'">'+each_mention+'</a>')
                        print comment
                        Comment.objects.filter(pk=each_comment.id).update(comment_html=comment,comment=comment)
                    except:
                        pass
        except Exception as e:
            print e
