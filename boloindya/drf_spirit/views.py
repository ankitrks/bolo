 # -*- coding: utf-8 -*-
import os
import ast
import copy
import time
import json
import boto3
import random
import urllib2
import itertools
from random import shuffle
from collections import OrderedDict
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, imencode

from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models import F,Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
from datetime import datetime,timedelta,date
from django.db.models.signals import post_save
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TopicFilter, CommentFilter
from .models import SingUpOTP
from .models import UserJarvisDump, UserLogStatistics, UserFeedback
from .permissions import IsOwnerOrReadOnly
from .utils import get_weight, add_bolo_score, shorcountertopic, calculate_encashable_details, state_language, language_options,short_time,\
    solr_object_to_db_object, solr_userprofile_object_to_db_object,get_paginated_data ,shortcounterprofile, get_ranked_topics

from forum.userkyc.models import UserKYC, KYCBasicInfo, KYCDocumentType, KYCDocument, AdditionalInfo, BankDetail
from forum.payment.models import PaymentCycle,EncashableDetail,PaymentInfo
from forum.category.models import Category,CategoryViewCounter
from forum.comment.models import Comment,CommentHistory
from forum.user.models import UserProfile,Follower,AppVersion,AndroidLogs,UserPay,VideoPlaytime,UserPhoneBook,Contact,ReferralCode
from jarvis.models import FCMDevice,StateDistrictLanguage, BannerUser, Report
from forum.topic.models import Topic,TopicHistory, ShareTopic, Like, SocialShare, Notification, CricketMatch, Poll, Choice, Voting, \
    Leaderboard, VBseen, TongueTwister, HashtagViewCounter
from forum.topic.utils import get_redis_vb_seen,update_redis_vb_seen
from forum.user.utils.follow_redis import get_redis_follower,update_redis_follower,get_redis_following,update_redis_following
from .serializers import *
from tasks import vb_create_task,user_ip_to_state_task,sync_contacts_with_user,cache_follow_post,cache_popular_post
from haystack.query import SearchQuerySet, SQ
from django.core.exceptions import MultipleObjectsReturned
from forum.topic.utils import get_redis_category_paginated_data,get_redis_hashtag_paginated_data,get_redis_language_paginated_data,get_redis_follow_paginated_data, get_popular_paginated_data
# from haystack.inputs import Raw, AutoQuery
# from haystack.utils import Highlighter
from django.contrib.contenttypes.models import ContentType

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
def timestamp_to_datetime(timestamp):
    try:
        if timestamp:
            return datetime.fromtimestamp(int(timestamp)/1000)
        return timestamp
    except Exception as e:
        print e


class ShufflePagination(LimitOffsetPagination):

    def get_paginated_response(self, data):
        shuffle(data)
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

class NotificationAPI(GenericAPIView):
    permissions_classes = (IsOwnerOrReadOnly,)
    serializer_class   = NotificationSerializer
    # pagination_class = LimitOffsetPagination

    limit = 15

    def post(self, request, action, format = None):
        # print "request user", request.user, action

        if action == 'get':
            notifications,next_offset = self.get_notifications(request.user.id)
            notification_data = self.serialize_notification(notifications)
            return JsonResponse({'notification_data':notification_data,'next_offset':next_offset}, safe=False)

        elif action == 'click':
            self.mark_notification_as_read()
            return JsonResponse({
                    'status': "SUCCESS"
                })
        elif action == 'mark_all_read':
            self.mark_all_read()
            return JsonResponse({
                    'status': "SUCCESS"
                })

    def get_notifications(self, user_id):
        user_id = self.request.user.id
        # last_read = get_redis(redis_keymap%(user_id))
        # notifications = Notification.get_notification(self.request.user, count = 100)

        offset = int(self.request.data.get('offset') or 0)
        limit = int(self.request.data.get('limit') or self.limit)
        next_offset=''

        # print "offset",offset,"page_size",page_size

        notifications = Notification.objects.filter(for_user = self.request.user, is_active = True).order_by('-created_at')[offset:offset+limit]
        total_notification_count = Notification.objects.filter(for_user = self.request.user, is_active = True).order_by('-created_at').count()
        total_offset = total_notification_count/limit
        if total_notification_count > 0 and not total_notification_count%limit:
            total_offset = total_offset-1
        if notifications:
            if total_offset > offset:
                next_offset = offset+limit
            update_notification_ids = list(Notification.objects.filter(for_user = self.request.user, is_active = True).order_by('-created_at').values_list('pk',flat=True))[offset:offset+limit]
            #print update_notification_ids
            Notification.objects.filter(pk__in=update_notification_ids).exclude(status=2).update(status=1)

        result = []
        for notification in notifications:
            result.append(notification)
        return result,next_offset


    def serialize_notification(self, notifications):
        serialized_data =[]
        for each_noti in notifications:
            try:
                serialized_data.append(each_noti.get_notification_json())
            except:
                pass
        return serialized_data

    
    def mark_notification_as_read(self):
        notification = Notification.objects.get(id = self.request.data.get("id"))
        notification.status = 2
        notification.save()

    def mark_all_read(self):
        Notification.objects.filter(for_user=self.request.user).update(status=2)

class TopicList(generics.ListCreateAPIView):
    serializer_class    = TopicSerializer
    filter_backends     = (DjangoFilterBackend,)
    filter_class        = TopicFilter
    permission_classes  = (IsAuthenticatedOrReadOnly,)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
        }
    

    def get_queryset(self):
        topics = []

        search_term=self.request.GET.keys()
        if search_term:
            filter_dic={}
            for term_key in search_term:
                if term_key not in ['limit','offset']:
                    if term_key:
                        value=self.request.GET.get(term_key)
                        filter_dic[term_key]=value
            if filter_dic:
                filter_dic['is_removed'] = False
                topics              = Topic.objects.filter(**filter_dic)
                pagination_class    = LimitOffsetPagination
        else:
                topics              = Topic.objects.filter(is_removed = False)
                pagination_class    = LimitOffsetPagination
        return topics


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Timeline 

class Usertimeline(generics.ListCreateAPIView):
    serializer_class   = TopicSerializerwithComment
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class    = LimitOffsetPagination


    """
    get:
    Search By Topic Title,Audio,Video...
    term        = request.GET.get('term', '')
    Required Parameters:
    term---Topic Title

    post:


    Required Parameters:
    title and category_id 
    """
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
        }


    def get_queryset(self):
        topics              = []
        is_user_timeline    = False
        search_term         =self.request.GET.keys()
        filter_dic      ={}
        sort_recent= False
        if search_term:
            post            = []
            for term_key in search_term:
                if term_key not in ['limit','offset','order_by']:
                    if term_key =='category':
                        filter_dic['m2mcategory__slug'] = self.request.GET.get(term_key)
                    elif term_key:
                        value               =self.request.GET.get(term_key)
                        filter_dic[term_key]=value
                        if term_key =='user_id':
                            is_user_timeline = True
            if 'order_by' in search_term:
                sort_recent = True

            if filter_dic:
                #print filter_dic
                if is_user_timeline:
                    filter_dic['is_removed'] = False
                    topics = Topic.objects.filter(**filter_dic)
                    all_shared_post = ShareTopic.objects.filter(user_id = filter_dic['user_id'])
                    if all_shared_post:
                        for each_post in all_shared_post:
                            if each_post.topic:
                                post.append(each_post.topic)
                            elif each_post.comment:
                                post.append(each_post.comment.topic)
                    if topics:
                        for each_post in topics:
                            post.append(each_post)
                    topics=sorted(itertools.chain(post),key=lambda x: x.date, reverse=True)
                else:
                    # all_follower = Follower.objects.filter(user_follower = self.request.user).values_list('user_following_id',flat=True)
                    all_follower = get_redis_following(self.request.user.id)
                    category_follow = UserProfile.objects.get(user= self.request.user).sub_category.all().values_list('id',flat = True)
                    # all_follower = [1,2,3,5]
                    # category_follow = [57,58,59,60,61,62,63]
                    post=[]
                    topics=[]
                    # startdate = datetime.today()
                    # enddate = startdate - timedelta(days=1)
                    # print search_term
                    if 'language_id' in search_term and not 'category' in search_term:
                        # print "a"
                        # post1 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(category_id__in = category_follow),language_id = self.request.GET.get('language_id'),is_removed = False,date__gte=enddate)
                        if not sort_recent:
                            post2 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(m2mcategory_id__in = category_follow),language_id = self.request.GET.get('language_id'),is_removed = False,is_vb = False)
                        else:
                            post2 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(m2mcategory_id__in = category_follow),language_id = self.request.GET.get('language_id'),is_removed = False,is_vb = False).order_by('-last_commented')
                    elif 'category' in search_term and not 'language_id' in search_term:
                        # print "b"
                        # post1 = Topic.objects.filter(category__slug =self.request.GET.get('category'),is_removed = False,date__gte=enddate)
                        if not sort_recent:
                            post2 = Topic.objects.filter(m2mcategory__slug =self.request.GET.get('category'),is_removed = False,is_vb = False)
                        else:
                            post2 = Topic.objects.filter(m2mcategory__slug =self.request.GET.get('category'),is_removed = False,is_vb = False).order_by('-last_commented')
                    elif 'language_id' in search_term and 'category' in search_term:
                        # print "maaz"
                        # post1 = Topic.objects.filter(language_id = self.request.GET.get('language_id'),category__slug =self.request.GET.get('category'),is_removed = False,date__gte=enddate)
                        if not sort_recent:
                            post2 = Topic.objects.filter(language_id = self.request.GET.get('language_id'),m2mcategory__slug =self.request.GET.get('category'),is_removed = False,is_vb = False)
                        else:
                            post2 = Topic.objects.filter(language_id = self.request.GET.get('language_id'),m2mcategory__slug =self.request.GET.get('category'),is_removed = False,is_vb = False).order_by('-last_commented')
                    else:
                        # print "d"
                        # post1 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(category_id__in = category_follow),is_removed = False,date__gte=enddate)
                        if not sort_recent:
                            post2 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(m2mcategory_id__in = category_follow),is_removed = False,is_vb = False)
                        else:
                            post2 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(m2mcategory_id__in = category_follow),is_removed = False,is_vb = False).order_by('-last_commented')
                    # print post1,post2
                    # if post1:
                    #     topics = topics+list(post1)
                    if post2:
                        topics = topics+list(post2)

        else:
            # all_follower = Follower.objects.filter(user_follower = self.request.user).values_list('user_following_id',flat=True)
            all_follower = get_redis_following(self.request.user.id)
            category_follow = UserProfile.objects.get(user= self.request.user).sub_category.all().values_list('id',flat = True)
            post=[]
            topics=[]
            # startdate = datetime.today()
            # enddate = startdate - timedelta(days=1)
            # post1 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(category_id__in = category_follow),is_removed = False,date__gte=enddate)
            if not sort_recent:
                post2 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(m2mcategory_id__in = category_follow),is_removed = False,is_vb = False)
            else:
                post2 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(m2mcategory_id__in = category_follow),is_removed = False,is_vb = False).order_by('-last_commented')
            # if post1:
            #     topics = topics+list(post1) 
            if post2:
                topics = topics+list(post2)
        return topics


@api_view(['GET'])
def VBList(request):
    topics = []
    is_user_timeline = False
    search_term = request.GET.keys()
    filter_dic = {}
    sort_recent = False
    category__slug = False
    m2mcategory__slug = False
    popular_post = False
    page_no = int(request.GET.get('page',1))
    if search_term:
        for term_key in search_term:
            if term_key not in ['limit','page','offset','order_by','is_popular', 'vb_score']:
                if term_key:
                    value = request.GET.get(term_key)
                    filter_dic[term_key]=value
                    if term_key =='user_id':
                        is_user_timeline = True
                        pagination_class = LimitOffsetPagination
                    if term_key =='category':
                        m2mcategory__slug = request.GET.get(term_key)
        filter_dic['is_vb'] = True

        if filter_dic:
            if is_user_timeline:
                filter_dic['is_removed'] = False
                topics = Topic.objects.filter(**filter_dic)
                post = topics
                topics=sorted(itertools.chain(post),key=lambda x: x.date, reverse=True)
            else:
                topics = []
                if m2mcategory__slug:
                    topics = get_redis_category_paginated_data(request.GET.get('language_id'),Category.objects.get(slug=m2mcategory__slug).id,page_no)
                else:
                    topics = get_redis_language_paginated_data(request.GET.get('language_id'),page_no)
    else:
        topics = Topic.objects.filter(is_removed = False,is_vb = True).order_by('-id')
    total_objects = len(topics)
    paginator = Paginator(topics, settings.REST_FRAMEWORK['PAGE_SIZE'])
    if 'offset' in search_term and int(request.GET.get('offset') or 0):
        page_no = int(int(request.GET.get('offset') or 0)/settings.REST_FRAMEWORK['PAGE_SIZE'])+1
    if not is_user_timeline:
        page_no = 1
    try:
        topics = paginator.page(page_no)
    except:
        topics = []
    return JsonResponse({"results":TopicSerializerwithComment(topics,context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),\
		'is_expand':request.GET.get('is_expand',True)},many=True).data,"count":total_objects})

def replace_query_param(url, key, val):
    try:
        from urllib import parse as urlparse
    except ImportError:
        import urlparse
    from django.http import QueryDict
    """
    Given a URL and a key/val pair, set or replace an item in the query
    parameters of the URL, and return the new URL.
    """
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)
    query_dict = QueryDict(query).copy()
    query_dict[key] = val
    query = query_dict.urlencode()
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))

class GetChallenge(generics.ListCreateAPIView):
    serializer_class = TopicSerializerwithComment
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = ShufflePagination 

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
        }

    def get_queryset(self):
        challenge_hash = self.request.GET.get('challengehash')
        language_id = self.request.GET.get('language_id')
        language_filter = {}
        if language_id:
            language_filter['language_id']=language_id
        challengehash = '#' + challenge_hash
        hash_tag = TongueTwister.objects.get(hash_tag__iexact=challengehash[1:])
        all_seen_vb = []
        if self.request.user.is_authenticated:
            all_seen_vb = get_redis_vb_seen(self.request.user.id)
            # all_seen_vb = VBseen.objects.filter(user = self.request.user, topic__title__icontains=challengehash).distinct('topic_id').values_list('topic_id',flat=True)
        excluded_list =[]
        boosted_post = Topic.objects.filter(is_removed = False,is_vb = True,hash_tags=hash_tag,is_boosted=True,boosted_end_time__gte=datetime.now()).filter(**language_filter).exclude(pk__in=all_seen_vb).distinct('user_id')
        if boosted_post:
            boosted_post = sorted(boosted_post, key=lambda x: x.date, reverse=True)
        for each in boosted_post:
            excluded_list.append(each.id)
        superstar_post = Topic.objects.filter(is_removed = False,is_vb = True,hash_tags=hash_tag,user__st__is_superstar = True).filter(**language_filter).exclude(pk__in=all_seen_vb).distinct('user_id')
        if superstar_post:
            superstar_post = sorted(superstar_post, key=lambda x: x.date, reverse=True)
        for each in superstar_post:
            excluded_list.append(each.id)
        popular_user_post = Topic.objects.filter(is_removed = False,is_vb = True,hash_tags=hash_tag,user__st__is_superstar = False,user__st__is_popular=True).filter(**language_filter).exclude(pk__in=all_seen_vb).distinct('user_id')
        if popular_user_post:
            popular_user_post = sorted(popular_user_post, key=lambda x: x.date, reverse=True)
        for each in popular_user_post:
            excluded_list.append(each.id)
        popular_post = Topic.objects.filter(is_removed = False,is_vb = True,hash_tags=hash_tag,user__st__is_superstar = False,user__st__is_popular=False,is_popular=True).filter(**language_filter).exclude(pk__in=all_seen_vb).distinct('user_id')
        if popular_post:
            popular_post = sorted(popular_post, key=lambda x: x.date, reverse=True)
        for each in popular_post:
            excluded_list.append(each.id)
        normal_user_post = Topic.objects.filter(is_removed = False,is_vb = True,hash_tags=hash_tag,user__st__is_superstar = False,user__st__is_popular=False,is_popular=False).filter(**language_filter).exclude(pk__in=all_seen_vb).distinct('user_id')
        if normal_user_post:
            normal_user_post = sorted(normal_user_post, key=lambda x: x.date, reverse=True)
        for each in normal_user_post:
            excluded_list.append(each.id)
        other_post = Topic.objects.filter(is_removed = False,is_vb = True,hash_tags=hash_tag).filter(**language_filter).exclude(pk__in=list(all_seen_vb)+list(excluded_list)).order_by('-date')
        orderd_all_seen_post=[]
        all_seen_post = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=all_seen_vb, hash_tags=hash_tag).filter(**language_filter)
        if all_seen_post:
            for each_id in all_seen_vb:
                for each_vb in all_seen_post:
                    if each_vb.id == each_id:
                        orderd_all_seen_post.append(each_vb)
        topics=list(boosted_post)+list(superstar_post)+list(popular_user_post)+list(popular_post)+list(normal_user_post)+list(other_post)+list(orderd_all_seen_post)


        return topics



@api_view(['GET'])
def newAlgoGetChallenge(request):
    challenge_hash = request.GET.get('challengehash')
    language_id = request.GET.get('language_id')
    challengehash = '#' + challenge_hash
    hash_tag = TongueTwister.objects.get(hash_tag__iexact=challengehash[1:])
    all_seen_vb = []
    topics =[]
    page_no = int(request.GET.get('page',1))
    if 'offset' in request.GET.keys() and int(request.GET.get('offset') or 0):
        page_no = int(int(request.GET.get('offset') or 0)/settings.REST_FRAMEWORK['PAGE_SIZE'])+1
    filter_dict = {'hash_tags':hash_tag}
    if language_id:
        filter_dict['language_id']=language_id
    topics = get_redis_hashtag_paginated_data(language_id,hash_tag.id,page_no)
    my_data = TopicSerializerwithComment(topics,context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand':request.GET.get('is_expand',True)},many=True).data

    return JsonResponse({"results":my_data})

class SmallSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'

class GetPopularHashTag(generics.ListCreateAPIView):
    serializer_class = TongueTwisterWithVideoByteSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = SmallSetPagination 

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
            'language_id': self.request.GET.get('language_id',None),
            'user_id': self.request.user.id
        }

    def get_queryset(self):
        hashtag_ids = self.request.GET.get('hashtag_ids',None)
        try:
            hashtag_ids = hashtag_ids.split(',')
        except:
            hashtag_ids = []
        hash_tags = TongueTwister.objects.filter(pk__in=hashtag_ids).order_by('-is_popular','-popular_date','-hash_counter')
        return hash_tags

@api_view(['GET'])
def GetFollowPost(request):
    all_follower = get_redis_following(request.user.id)
    category_follow = UserProfile.objects.get(user= request.user).sub_category.all()
    all_seen_vb = []
    topics =[]
    page_no = request.GET.get('page',1)
    topics = get_redis_follow_paginated_data(request.user.id,page_no)
    return JsonResponse({"results":TopicSerializerwithComment(topics,context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand':request.GET.get('is_expand',True)},many=True).data})


        

@api_view(['POST'])
def GetChallengeDetails(request):
    """
    post:
    user_id = request.POST.get('user_id', '')
    """ 
    challengehash = request.POST.get('ChallengeHash')
    language_id = request.POST.get('language_id', '2')
    challengehash = '#' + challengehash
    try:
        hash_tag = TongueTwister.objects.get(hash_tag__iexact=request.POST.get('ChallengeHash'))
        hash_tag_counter=HashtagViewCounter.objects.get(hashtag = hash_tag, language = language_id)
        #all_vb = Topic.objects.filter(hash_tags=hash_tag,is_removed=False,is_vb=True)
        vb_count = hash_tag_counter.video_count
        if hash_tag:
            tongue = hash_tag
            return JsonResponse({'message': 'success', 'hashtag':tongue.hash_tag,'vb_count':vb_count,\
                'en_tongue_descp':tongue.en_descpription,'hi_tongue_descp':tongue.hi_descpription,\
                'ta_tongue_descp':tongue.ta_descpription,'te_tongue_descp':tongue.te_descpription,\
                'be_descpription':tongue.be_descpription,'ka_descpription':tongue.ka_descpription,\
                'ma_descpription':tongue.ma_descpription,'gj_descpription':tongue.gj_descpription,\
                'mt_descpription':tongue.mt_descpription,'picture':tongue.picture,\
                'all_seen':shorcountertopic(hash_tag_counter.view_count)},status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'success', 'hashtag' : challengehash[1:],'vb_count':vb_count,\
                'en_tongue_descp':'','hi_tongue_descp':'',\
                'ta_tongue_descp':'','te_tongue_descp':'',\
                'be_descpription':'','ka_descpription':'',\
                'ma_descpription':'','gj_descpription':'',\
                'mt_descpription':'','picture':'',\
                'all_seen':shorcountertopic(hash_tag_counter.view_count)},status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Invalid','error':str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetTopic(generics.ListCreateAPIView):
    serializer_class   = SingleTopicSerializerwithComment
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class    = LimitOffsetPagination
    """
    post:
    topic_id =self.request.POST.get('topic_id','')
    """
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
        }

    def get_queryset(self):
        topic_id =self.request.GET.get('topic_id','')
        topic = Topic.objects.filter(id=topic_id)
        return topic


class GetQuestion(generics.ListCreateAPIView):
    serializer_class   = TopicSerializerwithComment
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class    = LimitOffsetPagination
    """
    post:
    """
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
        }
    

    def get_queryset(self):
        user_id = self.request.GET.get('user_id','')
        topic = Topic.objects.filter(user_id=user_id, is_removed=False,is_vb=False)
        return topic


class GetAnswers(generics.ListCreateAPIView):
    serializer_class   = UserAnswerSerializerwithComment
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class    = LimitOffsetPagination
    """
    post:
    """ 
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'user_id': self.request.GET.get('user_id',''),
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
        } 

    def get_queryset(self):
        user_id = self.request.GET.get('user_id','')
        get_topic_user_commented = Comment.objects.filter(user_id = user_id,is_removed=False).values_list('topic_id',flat=True)
        topics=[]
        if get_topic_user_commented:
            topics = Topic.objects.exclude(is_vb = True).filter(id__in=get_topic_user_commented,is_removed=False)

        return topics

class GetHomeAnswer(generics.ListCreateAPIView):
    serializer_class   = TopicSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class    = LimitOffsetPagination
    """
    post:
    """ 
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
        }
     
    def get_queryset(self):
        language_id = self.request.GET.get('language_id','')
        get_topic_user_commented = Comment.objects.filter(user_id = self.request.user,is_removed=False).values_list('topic_id',flat=True)
        topics=[]
        if get_topic_user_commented:
            topics = Topic.objects.exclude(is_vb = True).filter(language_id = language_id, is_removed=False)\
                .exclude(id__in=get_topic_user_commented).order_by('-date')
        else:
            topics = Topic.objects.exclude(is_vb = True).filter(language_id = language_id, is_removed=False)\
                .order_by('-date')

        return topics


@api_view(['POST'])
def RegisterDevice(request):
    """
    

    post:
    reg_id = request.POST.get('reg_id','')

   
    """

    fcm_decvice = FCMDevice()
    return fcm_decvice.register_device(request)


@api_view(['POST'])
def UnregisterDevice(request):
    """
    

    post:
    reg_id = request.POST.get('reg_id','')

    Required Parameters:
    title and category_id 
    """

    fcm_decvice = FCMDevice()
    return fcm_decvice.remove_device(request)

class BoloIndyaGenericAPIView(GenericAPIView):
    permissions_classes = (IsOwnerOrReadOnly,)

    def initialize_request(self, request, *args, **kwargs):
        new_request = super(BoloIndyaGenericAPIView, self).initialize_request(request, *args, **kwargs)
        return new_request

def search_break_word(term):
    q_objects = SQ()
    if term:
        term_list = term.split(' ')
        i=0
        for i, each_term in enumerate(term_list):
            if i==0:
                q_objects = SQ(content=each_term)
            else:
                q_objects |= SQ(content=each_term)
        return q_objects
    else:
        return SQ(content='')



class SolrSearchTop(BoloIndyaGenericAPIView):
    def get(self, request):
        topics      = []
        search_term = self.request.GET.get('term')
        language_id = self.request.GET.get('language_id', 1)
        page = int(request.GET.get('page',1))
        page_size = self.request.GET.get('page_size',5)
        is_expand=self.request.GET.get('is_expand',False)
        last_updated=timestamp_to_datetime(self.request.GET.get('last_updated',False))
        response ={}
        if search_term:
            topics =[]
            sqs = SearchQuerySet().models(Topic).raw_search(search_term).filter(SQ(language_id=language_id)|SQ(language_id='1')).filter(is_removed = False)
            if not sqs:
                suggested_word = SearchQuerySet().models(Topic).auto_query(search_term).spelling_suggestion()
                if suggested_word:
                    sqs = SearchQuerySet().models(Topic).raw_search(suggested_word).filter(SQ(language_id=language_id)|SQ(language_id='1')).filter(is_removed = False)
            if not sqs:
                sqs = SearchQuerySet().models(Topic).autocomplete(**{'text':search_term}).filter(SQ(language_id=language_id)|SQ(language_id='1')).filter(is_removed = False)
            if sqs:
                result_page = get_paginated_data(sqs, int(page_size), int(page))
                topics = solr_object_to_db_object(result_page[0].object_list)
            response["top_vb"]=TopicSerializerwithComment(topics,many=True,context={'is_expand':is_expand,'last_updated':last_updated}).data
            users  =[]
            sqs = SearchQuerySet().models(UserProfile).filter(search_break_word(search_term))
            if not sqs:
                suggested_word = SearchQuerySet().models(UserProfile).auto_query(search_term).spelling_suggestion()
                if suggested_word:
                    sqs = SearchQuerySet().models(UserProfile).filter(search_break_word(search_term))
            if not sqs:
                sqs = SearchQuerySet().models(UserProfile).autocomplete(**{'text':search_term})
            if sqs:
                result_page = get_paginated_data(sqs, int(page_size), int(page))
                users = solr_userprofile_object_to_db_object(result_page[0].object_list)
            response["top_user"]=UserSerializer(users,many=True).data
            hash_tags  =[]
            sqs = SearchQuerySet().models(TongueTwister).raw_search('hash_tag:'+search_term)
            if not sqs:
                suggested_word = SearchQuerySet().models(TongueTwister).auto_query(search_term).spelling_suggestion()
                if suggested_word:
                    sqs = SearchQuerySet().models(TongueTwister).raw_search('hash_tag:'+suggested_word)
            if not sqs:
                sqs = SearchQuerySet().models(TongueTwister).autocomplete(**{'text':search_term})
            if sqs:
                result_page = get_paginated_data(sqs, int(page_size), int(page))
                hash_tags = solr_object_to_db_object(result_page[0].object_list)
            response["top_hash_tag"] = TongueTwisterSerializer(hash_tags,many=True).data
        return JsonResponse(response, safe = False)


class SolrSearchTopic(BoloIndyaGenericAPIView):
    def get(self, request):
        topics      = []
        search_term = self.request.GET.get('term')
        language_id = self.request.GET.get('language_id', 1)
        page = int(request.GET.get('page',1))
        page_size = self.request.GET.get('page_size', settings.REST_FRAMEWORK['PAGE_SIZE'])
        is_expand=self.request.GET.get('is_expand',False)
        last_updated=timestamp_to_datetime(self.request.GET.get('last_updated',False))
        if search_term:
            sqs = SearchQuerySet().models(Topic).raw_search(search_term).filter(Q(language_id=language_id)|Q(language_id='1'),is_removed = False)
            if not sqs:
                suggested_word = SearchQuerySet().models(Topic).auto_query(search_term).spelling_suggestion()
                if suggested_word:
                    sqs = SearchQuerySet().models(Topic).raw_search(suggested_word).filter(Q(language_id=language_id)|Q(language_id='1'),is_removed = False)
            if not sqs:
                sqs = SearchQuerySet().models(Topic).autocomplete(**{'text':search_term}).filter(Q(language_id=language_id)|Q(language_id='1'),is_removed = False)
            if sqs:
                result_page = get_paginated_data(sqs, int(page_size), int(page))
                topics = solr_object_to_db_object(result_page[0].object_list)
            # topics  = Topic.objects.filter(title__icontains = search_term,is_removed = False,is_vb=True, language_id=language_id)
            next_page_number = page+1 if page_size*page<len(sqs) else ''
            response ={"count":len(sqs),"results":TopicSerializerwithComment(topics,many=True,context={'is_expand':is_expand,'last_updated':last_updated}).data,"next_page_number":next_page_number} 
        return JsonResponse(response, safe = False)


class SearchTopic(generics.ListCreateAPIView):
    """
    get:
    Search By Topic.
    term        = request.GET.get('term', '')
    Required Parameters:
    term---Topic Title

    post:

    Required Parameters:
    title and category_id 
    """


    serializer_class    = TopicSerializerwithComment
    permission_classes  = (IsOwnerOrReadOnly,)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
        }

    def get_queryset(self):
        topics      = []
        search_term = self.request.GET.get('term')
        language_id = self.request.GET.get('language_id', 1)
        if search_term:
            topics  = Topic.objects.filter(title__icontains = search_term,is_removed = False,is_vb=True, language_id=language_id)

        return topics



class SolrSearchHashTag(BoloIndyaGenericAPIView):
    def get(self, request):
        hash_tags      = []
        search_term = self.request.GET.get('term')
        page = int(request.GET.get('page',1))
        page_size = self.request.GET.get('page_size', settings.REST_FRAMEWORK['PAGE_SIZE'])
        if search_term:
            sqs = SearchQuerySet().models(TongueTwister).raw_search('hash_tag:'+search_term)
            if not sqs:
                suggested_word = SearchQuerySet().models(TongueTwister).auto_query(search_term).spelling_suggestion()
                if suggested_word:
                    sqs = SearchQuerySet().models(TongueTwister).raw_search('hash_tag:'+suggested_word)
            if not sqs:
                sqs = SearchQuerySet().models(TongueTwister).autocomplete(**{'text':search_term})
            if sqs:
                result_page = get_paginated_data(sqs, int(page_size), int(page))
                hash_tags = solr_object_to_db_object(result_page[0].object_list)
            # hash_tags  = TongueTwister.objects.filter(hash_tag__icontains = search_term)
            next_page_number = page+1 if page_size*page<len(sqs) else ''
            response ={"count":len(sqs),"results":TongueTwisterSerializer(hash_tags,many=True).data,"next_page_number":next_page_number} 
        return JsonResponse(response, safe = False)


class SearchHashTag(generics.ListCreateAPIView):
    """
    get:
    Search By Topic.
    term        = request.GET.get('term', '')
    Required Parameters:
    term---Topic Title

    post:

    Required Parameters:
    term 
    """


    serializer_class    = TongueTwisterSerializer
    permission_classes  = (IsOwnerOrReadOnly,)
    pagination_class    = LimitOffsetPagination

    def get_queryset(self):
        hash_tags      = []
        search_term = self.request.GET.get('term')
        if search_term:
            hash_tags  = TongueTwister.objects.filter(hash_tag__icontains = search_term)

        return hash_tags


@api_view(['POST'])
def GetUserProfile(request):
    """
    post:
    user_id = request.POST.get('user_id', '')
    """ 
    # serializer_class    = UserSerializer
    # permission_classes  = (IsOwnerOrReadOnly,)
    try:
        user_id = request.POST.get('user_id','')
        if user_id:
            user = User.objects.get(id=user_id)
        user_json = UserSerializer(user).data
        return JsonResponse({'message': 'success','result':user_json}, status=status.HTTP_200_OK)
    except:
        return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)

    # def get_queryset(self):
    #     user_id = self.request.POST.get('user_id','')
    #     if user_id:
    #         user = User.objects.get(id=user_id)

    #     return [user]



class SolrSearchUser(BoloIndyaGenericAPIView):
    def get(self, request):
        topics      = []
        search_term = self.request.GET.get('term')
        page = int(request.GET.get('page',1))
        page_size = self.request.GET.get('page_size', settings.REST_FRAMEWORK['PAGE_SIZE'])
        users = []
        if search_term:
            sqs = SearchQuerySet().models(UserProfile).filter(search_break_word(search_term))
            if not sqs:
                suggested_word = SearchQuerySet().models(UserProfile).auto_query(search_term).spelling_suggestion()
                if suggested_word:
                    sqs = SearchQuerySet().models(UserProfile).filter(search_break_word(search_term))
            if not sqs:
                sqs = SearchQuerySet().models(UserProfile).autocomplete(**{'text':search_term})
            if sqs:
                result_page = get_paginated_data(sqs, int(page_size), int(page))
                users = solr_userprofile_object_to_db_object(result_page[0].object_list)
            # users = User.objects.filter( Q(username__icontains = search_term) | Q(st__name__icontains = search_term) | Q(first_name__icontains = search_term) | \
            #        Q(last_name__icontains = search_term) )
            next_page_number = page+1 if page_size*page<len(sqs) else ''
            response ={"count":len(sqs),"results":UserSerializer(users,many=True).data,"next_page_number":next_page_number} 
        return JsonResponse(response, safe = False)


class SearchUser(generics.ListCreateAPIView):

    """
    get:
    Search By User.
    term        = request.GET.get('term', '')
    Required Parameters:
    term--- Username and First Name

    post: 


    Required Parameters:
    title and category_id 
    """

    serializer_class    = UserSerializer
    permission_classes  = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        users       = []
        search_term = self.request.GET.get('term')
        if search_term:
            name_list = search_term.split()
            users = User.objects.filter( Q(username__icontains = search_term) | Q(st__name__icontains = search_term) | Q(first_name__icontains = search_term) | \
                    Q(last_name__icontains = search_term) )
            #user_ids = UserProfile.objects.filter(reduce(lambda x, y: x | y, [Q(name__icontains=word) for word in name_list])).values_list('user_id',flat=True)
            #users = User.objects.filter(Q(username__icontains = search_term)|Q(reduce(lambda x, y: x | y, [Q(username__icontains=word) \
            #    for word in name_list]))|Q(first_name__icontains = search_term)|Q(last_name__icontains = search_term)|Q(id__in = user_ids)).order_by('-st__question_count')
        return users

def get_search_suggestion(request):
    term = request.GET.get('term',None)
    sqs = []
    if term:
        sqs1 = SearchQuerySet().models(UserProfile).autocomplete(**{'name':term}).values_list('name',flat=True)[:5]
        sqs2 = SearchQuerySet().models(Topic,TongueTwister).autocomplete(**{'text':term}).values_list('text',flat=True)[:10-len(sqs1)]
        sqs = sqs1+ sqs2
        if not sqs:
            suggested_word = SearchQuerySet().auto_query(term).spelling_suggestion()
            if suggested_word:
                sqs1 = SearchQuerySet().models(UserProfile).autocomplete(**{'name':suggested_word}).values_list('name',flat=True)[:5]
                sqs2 = SearchQuerySet().models(Topic,TongueTwister).autocomplete(**{'text':suggested_word}).values_list('text',flat=True)[:10-len(sqs1)]
                sqs = sqs1+ sqs2
                # sqs = SearchQuerySet().autocomplete(**{'text':suggested_word}).filter(is_removed = False).values_list('text',flat=True)[:10]
            if not sqs:
                sqs1 = SearchQuerySet().models(UserProfile).raw_search(term).values_list('name',flat=True)[:5]
                sqs2 = SearchQuerySet().models(Topic,TongueTwister).raw_search(term).values_list('text',flat=True)[:5]
                sqs = sqs1+sqs2
    return JsonResponse({"suggestion":remove_change_line(sqs)},safe=False)

def remove_change_line(term_list):
    final_term_list=[]
    if term_list:
        for each in term_list:
            final_term_list.append(each.strip())
    return final_term_list

def get_video_thumbnail(video_url):
    video = VideoCapture(video_url)
    frames_count = int(video.get(CAP_PROP_FRAME_COUNT))
    frame_no = frames_count*2/3
    video.set(CAP_PROP_POS_FRAMES, frame_no)
    success, frame = video.read()
    if success:
        b = imencode('.jpg', frame)[1].tostring()
        ts = time.time()
        virtual_thumb_file = ContentFile(b, name = "img-" + str(ts).replace(".", "")  + ".jpg" )
        url_thumbnail= upload_thumbail(virtual_thumb_file)
        # obj.thumbnail = url_thumbnail
        # obj.media_duration = media_duration
        # obj.save()
        return url_thumbnail
    else:
        return False

#from moviepy.editor import VideoFileClip
def getVideoLength(input_video):
    clip = VideoFileClip(input_video)
    dt = timedelta(seconds = int(clip.duration))
    minutes = '00'
    seconds = '00'
    if dt.seconds/60:
        if len(str(dt.seconds/60))==1:
            minutes = '0'+str(dt.seconds/60)
        else:
            minutes = str(dt.seconds/60)
    else:
        minutes='00'
    if dt.seconds:
        if dt.seconds<60:
            if len(str(dt.seconds))==1:
                seconds = '0'+str(dt.seconds)
            else:
                seconds = str(dt.seconds)
        else:
            seconds = str(dt.seconds -(dt.seconds/60)*60)
            if len(seconds)==1:
                seconds = '0'+seconds
    else:
        seconds='00'
    duration= minutes+":"+seconds
    return duration

def upload_thumbail(virtual_thumb_file):
    try:
        client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
        ts = time.time()
        created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        final_filename = "img-" + str(ts).replace(".", "")  + ".jpg" 
        client.put_object(Bucket=settings.BOLOINDYA_AWS_BUCKET_NAME, Key='thumbnail/' + final_filename, Body=virtual_thumb_file, ACL='public-read')
        # client.resource('s3').Object(settings.BOLOINDYA_AWS_BUCKET_NAME, 'thumbnail/' + final_filename).put(Body=open(virtual_thumb_file, 'rb'))
        filepath = "https://s3.amazonaws.com/"+settings.BOLOINDYA_AWS_BUCKET_NAME+"/thumbnail/"+final_filename
        # if os.path.exists(file):
        #     os.remove(file)
        return filepath
    except:
        return None

def upload_media(media_file):
    try:
        client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
        ts = time.time()
        created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        filenameNext= str(media_file.name).split('.')
        final_filename = str(filenameNext[0])+"_"+ str(ts).replace(".", "")+"."+str(filenameNext[1])
        client.put_object(Bucket=settings.BOLOINDYA_AWS_BUCKET_NAME, Key='media/' + final_filename, Body=media_file)
        filepath = "https://s3.amazonaws.com/"+settings.BOLOINDYA_AWS_BUCKET_NAME+"/media/"+final_filename
        # if os.path.exists(file):
        #     os.remove(file)
        return filepath
    except:
        return None

@api_view(['POST'])
def upload_profile_image(request):
    try:
        my_image = request.FILES['file']
        my_image_url = upload_thumbail(my_image)
        if my_image_url:
            return JsonResponse({'status': 'success','body':my_image_url}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)





import random, string
def get_random_username():
    today_datetime = datetime.now()
    year = str(today_datetime.year%100)
    month = today_datetime.month
    if month <10:
        month = '0'+str(month)
    else:
        month = str(month)
    x = 'bi'+year+month+''.join(random.choice(string.digits) for _ in range(6))
    x = x.lower()
    # x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    try:
        user = User.objects.get(username=x)
        x = get_random_username()
    except:
        return x

def check_username_valid(username):
    if re.match(r"^[a-z0-9_.-]+$", username):
        return True
    else:
        return False


@api_view(['POST'])
def upload_video_to_s3(request):
    media_file = request.FILES['media']
    if media_file:
        media_url = upload_media(media_file)
        path = default_storage.save(media_file.name, ContentFile(media_file.read()))
        with default_storage.open(media_file.name, 'wb+') as destination:
            for chunk in media_file.chunks():
                destination.write(chunk)
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        thumbnail_url  = get_video_thumbnail(tmp_file)
        videolength = getVideoLength(tmp_file)
        os.remove(tmp_file)
        return JsonResponse({'status': 'success','body':media_url,'thumbnail':thumbnail_url,'media_duration':videolength}, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_audio_to_s3(request):
    media_file = request.FILES['media']
    if media_file:
        media_url = upload_media(media_file)
        return JsonResponse({'status': 'success','body':media_url,'thumbnail':'','media_duration':''}, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def replyOnTopic(request):

    """
    get:
    Return a list of all the existing users.

    post:
    Reply on topic.
    topic_id     = request.POST.get('topic_id', '')
    language_id  = request.POST.get('language_id', '')
    comment_html = request.POST.get('comment', '')
    mobile_no    = request.POST.get('mobile_no', '')
    thumbnail = request.POST.get('thumbnail', '')
    media_duration = request.POST.get('media_duration', '')

    Required Parameters:
    user_id and topic_id and comment_html

    """

    user_id      = request.user.id
    topic_id     = request.POST.get('topic_id', '')
    language_id  = request.user.st.language
    comment_html = request.POST.get('comment', '').strip()
    mobile_no    = request.POST.get('mobile_no', '')
    thumbnail = request.POST.get('thumbnail', '')
    media_duration = request.POST.get('media_duration', '')
    comment      = Comment()

    if request.POST.get('is_media'):
        comment.is_media = request.POST.get('is_media')
    if request.POST.get('is_audio'):
        comment.is_audio = request.POST.get('is_audio')

    if user_id and topic_id and comment_html:
        comment_html = check_space_before_hash(comment_html)
        try:
            comment_html,username_list = get_mentions(comment_html)
            temp_comment = comment_html
            tag_list=check_space_before_hash(temp_comment).split()
            if tag_list:
                for index,value in enumerate(tag_list):
                    if value.startswith("#"):
                        has_hashtag = True
                        tag_list[index]='<a href="/get_challenge_details/?ChallengeHash='+value.strip('#')+'">'+value+'</a>'
                temp_comment=" ".join(tag_list)
                temp_comment = temp_comment[0].upper()+temp_comment[1:]
            recent_comment = Comment.objects.filter(comment = temp_comment,topic_id=topic_id,user=request.user,date__gt=datetime.now()-timedelta(minutes=5))
            if recent_comment:
                return JsonResponse({'message': 'Already commented same comment'}, status=status.HTTP_400_BAD_REQUEST)
            comment.comment       = comment_html.strip()
            comment.comment_html  = comment_html.strip()
            comment.language_id   = language_id
            comment.user_id       = user_id
            comment.topic_id      = topic_id
            comment.mobile_no     = mobile_no
            comment.save()
            has_hashtag,hashtagged_title = check_hashtag(comment)
            if has_hashtag:
                comment.comment = hashtagged_title.strip()
                comment.comment_html = hashtagged_title.strip()
                comment.save()
            if username_list:
                send_notification_to_mentions(username_list,comment)
            topic = Topic.objects.get(pk = topic_id)
            topic.comment_count = F('comment_count')+1
            topic.last_commented = timezone.now()
            topic.save()
            userprofile = UserProfile.objects.get(user = request.user)
            userprofile.answer_count = F('answer_count')+1
            userprofile.save()
            if thumbnail:
                comment.thumbnail = thumbnail
            if media_duration:
                comment.media_duration = media_duration
            comment.save()
            add_bolo_score(request.user.id, 'reply_on_topic', comment)
            return JsonResponse({'message': 'Reply Submitted','comment':CommentSerializer(comment).data}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'Topic Id / User Id / Comment provided'}, status=status.HTTP_204_NO_CONTENT)

def check_hashtag(comment):
    has_hashtag = False
    title = comment.comment
    tag_list=check_space_before_hash(title).split()
    if tag_list:
        for index,value in enumerate(tag_list):
            if value.startswith("#"):
                has_hashtag = True
                tag_list[index]='<a href="/get_challenge_details/?ChallengeHash='+value.strip('#')+'">'+value+'</a>'
                # tag,is_created = TongueTwister.objects.get_or_create(hash_tag__iexact=value.strip('#'))
                try:
                    tag = TongueTwister.objects.get(hash_tag__iexact=value.strip('#'))
                    is_created = False
                except:
                    tag = TongueTwister.objects.create(hash_tag=value.strip('#'))
                    is_created = True
                if not is_created:
                    tag.hash_counter = F('hash_counter')+1
                tag.save()
                comment.hash_tags.add(tag)
        title=" ".join(tag_list)
        title = title[0].upper()+title[1:]
    return has_hashtag, title

def remove_old_hashtag(comment,history_comment):
    hash_tags = comment.hash_tags.all()
    for each_hashtag in hash_tags:
        history_comment.hash_tags.add(each_hashtag)
        each_hashtag.hash_counter = F('hash_counter')-1
        comment.hash_tags.remove(each_hashtag)
        each_hashtag.save()


def get_mentions(comment):
    mention_tag=[mention for mention in comment.split() if mention.startswith("@")]
    if mention_tag:
        username_list = [each_mention.strip('@') for each_mention in mention_tag]
        for each_mention in mention_tag:
            try:
                user = User.objects.get(username=each_mention.strip('@'))
                comment = comment.replace(each_mention,'<a href="/timeline/?username='+each_mention.strip('@')+'">'+each_mention+'</a>')
            except:
                pass
        return comment,username_list
    else:
        return comment,[]

def send_notification_to_mentions(username_list,comment_obj):
    for each_username in username_list:
        try:
            notify_mention = Notification.objects.create(for_user = User.objects.get(username=each_username) ,topic = comment_obj,notification_type='10',user = comment_obj.user)
        except:
            pass

@api_view(['POST'])
def mention_suggestion(request):
    term = request.POST.get('term', '')
    mention_list = []
    if term:
        all_follower_user = list(Follower.objects.filter((Q(user_following__username__icontains=term)|Q(user_following__st__name__icontains=term)),user_follower=request.user,is_active=True).values_list('user_following_id',flat=True))[:5]  #need to replace with redis
        other_user = list(UserProfile.objects.filter(Q(user__username__icontains=term)|Q(name__icontains=term)).values_list('user_id',flat=True).order_by('-vb_count'))[:10-len(all_follower_user)]
    else:
        # all_follower_user = list(Follower.objects.filter(user_follower=request.user,is_active=True).values_list('user_following_id',flat=True))[:10]
        all_follower_user = get_redis_following(request.user.id)[:10]
        other_user=[]
    mention_list= all_follower_user + other_user
    mention_users=User.objects.filter(pk__in=mention_list)
    user_data = BasicUserSerializer(mention_users,many=True).data
    return JsonResponse({'mention_users':user_data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reply_delete(request):

    """
    get:
    Delete Specific.

    post:
    Delete Reply.
    comment_id     = request.POST.get('comment_id', '')

    Required Parameters:
    user_id and comment_id

    """

    comment_id     = request.POST.get('comment_id', '')
    comment = Comment.objects.get(pk= comment_id)

    if comment.user == request.user or comment.topic.user == request.user:
        try:
            comment.delete()
            return JsonResponse({'message': 'Comment Deleted'}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'Invalid Delete Request'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def hashtag_suggestion(request):
    term = request.POST.get('term', '')
    hash_tags = []
    # if term:
    #     sqs = SearchQuerySet().models(TongueTwister).autocomplete(**{'text':term})[:10]
    #     if sqs:
    #         hash_tags = solr_object_to_db_object(sqs)
    if term:
        hash_tags = TongueTwister.objects.filter(hash_tag__icontains=term).order_by('-hash_counter')[:10]
    hash_data = BaseTongueTwisterSerializer(hash_tags,many=True).data
    return JsonResponse({'hash_data':hash_data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def solr_hashtag_suggestion(request):
    term = request.POST.get('term', '')
    hash_tags = []
    if term:
        sqs = SearchQuerySet().models(TongueTwister).autocomplete(**{'text':term})[:10]
        if sqs:
            hash_tags = solr_object_to_db_object(sqs)
    # hash_tags = TongueTwister.objects.filter(hash_tag__icontains=term).order_by('-hash_counter')[:10]
    hash_data = BaseTongueTwisterSerializer(hash_tags,many=True).data
    return JsonResponse({'hash_data':hash_data}, status=status.HTTP_200_OK)

def find(string, char):
    return [i for i, ltr in enumerate(string) if ltr == char]

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

@api_view(['POST'])
def createTopic(request):

    """
    get:
    Return a list of all the existing users.

    post:
    Create Topic.
    title        = request.POST.get('title', '')
    language_id  = request.POST.get('language_id', '')
    category_id  = request.POST.get('category_id', '')
    topic.question_audio = request.POST.get('question_video')
    topic.question_video = request.POST.get('question_audio')
    request.POST.get('question_image')

    Required Parameters:
    title and category_id 

    """

    topic           = Topic()
    user_id         = request.user.id
    title           = request.POST.get('title', '').strip()
    language_id     = request.POST.get('language_id', '')
    category_id     = request.POST.get('category_id', '')
    media_duration  = request.POST.get('media_duration', '')
    question_image  = request.POST.get('question_image', '')
    is_vb           = request.POST.get('is_vb',False)
    vb_width        = request.POST.get('vb_width',0)
    vb_height       = request.POST.get('vb_height',0)
    question_video  = request.POST.get('question_video')
    m3u8_url        = request.POST.get('m3u8_url')
    data_dump       = request.POST.get('data_dump')
    job_id          = request.POST.get('job_id')
    # media_file = request.FILES.get['media']
    # print media_file

    if title:
        topic.title          = (title[0].upper()+title[1:]).strip()
    if request.POST.get('question_audio'):
        topic.question_audio = request.POST.get('question_audio')
    if question_video:
        # topic.question_video = request.POST.get('question_video')
        topic.safe_backup_url = question_video
        topic.backup_url      = question_video

    if m3u8_url:
        topic.question_video = m3u8_url
        topic.transcode_dump = data_dump
        topic.transcode_job_id = job_id

    if request.POST.get('question_image'):
        topic.question_image = request.POST.get('question_image')

    if m3u8url and question_video and not request.user.st.is_test_user:
        already_exist_topic = Topic.objects.filter(Q(question_video=m3u8url)|Q(backup_url=question_video))
        if already_exist_topic:
            topic_json = TopicSerializerwithComment(already_exist_topic[0], context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data
            return JsonResponse({'message': 'Video Byte Created','topic':topic_json}, status=status.HTTP_201_CREATED)



    try:

        topic.language_id   = request.user.st.language
        topic.category_id   = category_id
        topic.user_id       = user_id
        if is_vb:
            topic.is_vb = True
            topic.media_duration = media_duration
            topic.question_image = question_image
            topic.vb_width = vb_width
            topic.vb_height = vb_height
            view_count = random.randint(1,5)
            topic.view_count = view_count
            topic.save()
            vb_create_task.delay(topic.id)
            # topic.update_vb()
            tag_list=check_space_before_hash(title).split()
            hash_tag = copy.deepcopy(tag_list)
            if tag_list:
                for index, value in enumerate(tag_list):
                    if value.startswith("#"):
                        tag_list[index]='<a href="/get_challenge_details/?ChallengeHash='+value.strip('#')+'">'+value+'</a>'
                title = " ".join(tag_list).strip()
                topic.title = (title[0].upper()+title[1:]).strip()
                # for each_tag in tag_list:
                for index, value in enumerate(hash_tag):
                    if value.startswith("#"):
                        # tag,is_created = TongueTwister.objects.get_or_create(hash_tag__iexact=value.strip('#'))
                        try:
                            tag = TongueTwister.objects.get(hash_tag__iexact=value.strip('#'))
                            is_created = False
                        except:
                            tag = TongueTwister.objects.create(hash_tag=value.strip('#'))
                            is_created = True
                        if not is_created:
                            tag.hash_counter = F('hash_counter')+1
                        tag.save()
                        topic.hash_tags.add(tag)
        else:
            view_count = random.randint(10,30)
            topic.view_count = view_count
        topic.save()
        try:
            provide_view_count(view_count,topic)
        except:
            pass
        topic.m2mcategory.add(Category.objects.get(pk=category_id))
        if not is_vb:
            userprofile = UserProfile.objects.get(user = request.user)
            userprofile.question_count = F('question_count')+1
            userprofile.save()
            add_bolo_score(request.user.id,'create_topic', topic)
            topic_json = TopicSerializerwithComment(topic, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data
            message = 'Topic Created'
        else:
            userprofile = UserProfile.objects.get(user = request.user)
            userprofile.vb_count = F('vb_count')+1
            userprofile.save()
            # add_bolo_score(request.user.id, 'create_topic', topic)
            topic_json = TopicSerializerwithComment(topic, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data
            message = 'Video Byte Created'
        return JsonResponse({'message': message,'topic':topic_json}, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)

def provide_view_count(view_count,topic):
    all_test_userprofile_id = UserProfile.objects.filter(is_test_user=True).values_list('user_id',flat=True)[:view_count]
    for each_user_id in all_test_userprofile_id:
        vb_obj = VBseen.objects.create(topic= topic,user_id =each_user_id)
        UserProfile.objects.filter(user=topic.user).update(view_count=F(view_count)+1,own_vb_view_count = F('own_vb_view_count')+1)
        update_redis_vb_seen(each_user_id,topic.id)

@api_view(['POST'])
def editTopic(request):

    """
    get:
    Return a list of all the existing users.

    post:
    edit Topic.
    title        = request.POST.get('title', '')
    category_id  = request.POST.get('category_id', '')
    language_id  = request.POST.get('language_id', '')
    topic_id = request.POST.get('topic_id', '')

    Required Parameters:
    title and category_id 

    """
    try:
        topic_id = request.POST.get('topic_id', '')
        title        = request.POST.get('title', '').strip()
        topic        = Topic.objects.get(pk = topic_id)

        if topic.user == request.user:
            tag_list=check_space_before_hash(title).split()
            hash_tag = copy.deepcopy(tag_list)
            if tag_list:
                for index, value in enumerate(tag_list):
                    if value.startswith("#"):
                        tag_list[index]='<a href="/get_challenge_details/?ChallengeHash='+value.strip('#')+'">'+value+'</a>'
                title = " ".join(tag_list)
                new_title = (title[0].upper()+title[1:]).strip()
            if not new_title == topic.title:
                history_topic = TopicHistory.objects.create(source=topic,title=topic.title)
                hash_tags = topic.hash_tags.all()
                for each_hashtag in hash_tags:
                    history_topic.hash_tags.add(each_hashtag)
                    each_hashtag.hash_counter = F('hash_counter')-1
                    topic.hash_tags.remove(each_hashtag)
                    each_hashtag.save()
                topic.title = new_title.strip()
                if hash_tag:
                    for index, value in enumerate(hash_tag):
                        if value.startswith("#"):
                            # tag, is_created = TongueTwister.objects.get_or_create(hash_tag__iexact=value.strip("#"))
                            try:
                                tag = TongueTwister.objects.get(hash_tag__iexact=value.strip('#'))
                                is_created = False
                            except:
                                tag = TongueTwister.objects.create(hash_tag=value.strip('#'))
                                is_created = True
                            if not is_created:
                                tag.hash_counter = F('hash_counter')+1
                            tag.save()
                            topic.hash_tags.add(tag)
                topic.save()

                topic_json = TopicSerializerwithComment(topic, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data
                return JsonResponse({'message': 'Topic Edited','topic':topic_json}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({'message': 'No Changes made'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Invalid Edit Request'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Invalid Edit Request'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def editComment(request):
    """

    post:
    edit Topic.
    comment        = request.POST.get('comment', '')
    comment_id = request.POST.get('comment_id',None)

    Required Parameters:
    comment
    """
    try:
        comment_id = request.POST.get('comment_id',None)
        comment_text = request.POST.get('comment_text','').strip()
        comment = Comment.objects.get(pk=comment_id)
        if comment.user == request.user:
            comment_text,username_list = get_mentions(comment_text)
            old_comment = strip_tags(comment.comment_html)
            old_comment_text,old_username_list = get_mentions(old_comment)
            if not old_comment == comment_text:
                history_comment = CommentHistory.objects.create(source=comment,comment=comment.comment,comment_html=comment.comment_html)
                remove_old_hashtag(comment,history_comment)
                comment.comment_html=comment_text
                comment.comment = comment_text
                comment.save()
                for each_username in username_list:
                    if not each_username in old_username_list:
                        send_notification_to_mentions([each_username],comment)
                has_hashtag,hashtagged_title = check_hashtag(comment)
                if has_hashtag:
                    comment.comment = hashtagged_title.strip()
                    comment.comment_html = hashtagged_title.strip()
                    comment.save()
                return JsonResponse({'message': 'Reply Updated','comment':CommentSerializer(comment).data}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({'message': 'No Changes made'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Invalid Edit Request'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Invalid Edit Request','error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

from HTMLParser import HTMLParser

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

@api_view(['POST'])
def topic_delete(request):

    """
    get:
    Delete Specific.

    post:
    Delete Reply.
    topic_id     = request.POST.get('topic_id', '')

    Required Parameters:
    user_id and topic_id

    """

    user_id      = request.user.id
    topic_id     = request.POST.get('topic_id', '')

    topic = Topic.objects.get(pk= topic_id)
    now = datetime.now()
    allowed_date = datetime.strptime('01-'+str(now.month)+'-'+str(now.year)+' 00:00:00', "%d-%m-%Y %H:%M:%S")

    if allowed_date <= topic.date:
        if topic.user == request.user:
            try:
                topic.delete()
                return JsonResponse({'message': 'Topic Deleted'}, status=status.HTTP_201_CREATED)
            except:
                return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'message': 'Invalid Delete Request'}, status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({'message': 'can not delete old videos'}, status=status.HTTP_204_NO_CONTENT)

# @api_view(['POST'])
def notification_topic(request):

    """
    post:
    Return a list of all the existing users.

    get:
    edit Topic.
    topic_id = request.GET.get('topic_id', '')

    Required Parameters:
    title and category_id 

    """
    try:
        topic_id = request.GET.get('topic_id', '')
        topic        = Topic.objects.get(pk = topic_id)
        topic_json = TopicSerializerwithComment(topic, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data
        return JsonResponse({'result':[topic_json]}, status=status.HTTP_201_CREATED)   
    except:
        return JsonResponse({'message': 'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)

                
class TopicDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class    = TopicSerializer
    queryset            = Topic.objects.all()
    permission_classes  = (IsOwnerOrReadOnly,)
    lookup_field        = 'slug'

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'is_expand': self.request.GET.get('is_expand',True),
            'last_updated': timestamp_to_datetime(self.request.GET.get('last_updated',None)),
        }

class TopicCommentList(generics.ListAPIView):
    serializer_class    = CommentSerializer
    queryset            = Comment.objects.all()
    permission_classes  = (IsOwnerOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        topic_slug = self.kwargs['slug']
        topic_id = self.kwargs['topic_id']
        comment_id = self.request.GET.get('comment_id',None)
        limit = int(self.request.GET.get('limit',15))
        if comment_id:
            offset = int(self.request.GET.get('offset',0))
            all_comments = list(self.queryset.filter(topic_id=topic_id,is_removed = False).order_by('-id'))
            index_of_comment=0
            try:
                index_of_comment=all_comments.index(Comment.objects.get(pk=comment_id))
            except:
                index_of_comment=0
            if index_of_comment:
                index_of_comment+=1
                comment_remainder = index_of_comment%limit
                comment_offset = (index_of_comment/limit)*limit
                if comment_offset and comment_remainder==0:
                    offset = comment_offset-limit
                else:
                    offset = comment_offset
            self.request.GET._mutable = True
            self.request.GET.update({'offset':offset})
            self.request.GET.update({'comment_id':''})
            return self.queryset.filter(topic_id=topic_id,is_removed = False).order_by('-id')


        return self.queryset.filter(topic_id=topic_id,is_removed = False).order_by('-id')

class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_engagement = False).exclude(parent__isnull = False)
    pagination_class=None
    # permission_classes = (IsAuthenticated,)
    permission_classes  = (AllowAny,)


class UserPayDatatableList(generics.ListAPIView):
    serializer_class = UserPayDatatableSerializer
    # queryset = User.objects.filter(is_active = True)
    def get_queryset(self):
        return UserProfile.objects.all().order_by('-bolo_score')

class ActiveReoprtsDatatableList(generics.ListAPIView):
    serializer_class = ReportDatatableSerializer
    # queryset = User.objects.filter(is_active = True)
    def get_queryset(self):
        filter_dict = {}
        if self.request.GET.get('is_active',None):
            if self.request.GET.get('is_active')=='1':
                filter_dict = {'is_active': True}
            elif self.request.GET.get('is_active')=='0':
                filter_dict = {'is_active': False}
        return Report.objects.filter(**filter_dict).order_by('-id')


class KYCDocumentTypeList(generics.ListAPIView):
    serializer_class = KYCDocumnetsTypeSerializer
    queryset = KYCDocumentType.objects.all()
    pagination_class=None
    # permission_classes = (IsAuthenticated,)
    permission_classes  = (AllowAny,)
 
def Convert_tuple_to_dict(tup, di): 
    for a, b in tup: 
        di.setdefault(a, []).append(b) 
    return di

@api_view(['POST'])
def kyc_profession_status(request):
    profession_option = Convert_tuple_to_dict(AdditionalInfo.profession_options,{})
    status_option = Convert_tuple_to_dict(AdditionalInfo.status_options,{})
    mode_of_transaction_options = Convert_tuple_to_dict(UserKYC.mode_of_transaction_options,{})
    return JsonResponse({'message': 'succeess','profession_option':profession_option,'status_option':status_option,'mode_of_transaction_options':mode_of_transaction_options}, status=status.HTTP_200_OK)

class EncashableDetailList(generics.ListAPIView):
    serializer_class = EncashableDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        username = self.request.GET.get('username',None)
        user = User.objects.get(username=username)
        calculate_encashable_details(user)
        all_encash_detail = EncashableDetail.objects.filter(user =user)
        return all_encash_detail


class SubCategoryList(generics.ListAPIView):
    """
    post:
        Required Parameters
        self.request.POST.get('category_id')
    """
    serializer_class = CategorySerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes  = (AllowAny,)
    pagination_class=None
    def get_queryset(self):
        sub_category =[]
        category_id = self.request.GET.get('category_id')
        if category_id:
            return Category.objects.filter(is_engagement = False, parent_id = category_id)
        return Category.objects.filter(is_engagement = False, parent__isnull = False)

class ExpertList(generics.ListAPIView):
    """
    GET:
        Required Parameters
        None.
    """
    serializer_class = UserProfileSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes  = (AllowAny,)
    pagination_class=None
    
    def get_queryset(self):
        return UserProfile.objects.filter(is_expert = True).order_by('name')

class CommentList(generics.ListCreateAPIView):
    serializer_class    = CommentSerializer
    queryset            = Comment.objects.all()
    filter_backends     = (DjangoFilterBackend,)
    filter_class        = CommentFilter
    permission_classes  = (IsAuthenticatedOrReadOnly,)
    pagination_class    = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class    = CommentSerializer
    queryset            = Comment.objects.all()
    permission_classes  = (IsOwnerOrReadOnly,)
    lookup_field        = 'id'

def generateOTP(n):
    import math, random 
    digits = "0123456789"
    OTP = "" 
    for i in range(n) : 
        OTP += digits[int(math.floor(random.random() * 10))] 
    return OTP

def validate_indian_number(mobile_no):
    if mobile_no and len(mobile_no)>8 and len(mobile_no)<=14:
        if mobile_no.startswith('091'):
            mobile_no = validate_indian_number(mobile_no[3:])
        elif mobile_no.startswith('+91'):
            mobile_no = validate_indian_number(mobile_no[3:])
        elif mobile_no.startswith('0'):
            mobile_no = validate_indian_number(mobile_no[1:])
        elif mobile_no.startswith('91') and len(mobile_no)==12:
            mobile_no = validate_indian_number(mobile_no[2:])
        return mobile_no
    else:
        return mobile_no

def send_sms(phone_number, otp):
    import json
    import urllib2
    sms_url         = 'https://2factor.in/API/V1/' + settings.TWO_FACTOR_SMS_API_KEY +  '/SMS/' +  phone_number +\
             '/' + otp + '/' + settings.TWO_FACTOR_SMS_TEMPLATE
    response        = urllib2.urlopen(sms_url).read()
    json_response   = json.loads( response )
    if json_response.has_key('Status') and json_response['Status'] == 'Success':
        return response, True
    return response, False


#Known Issue ... Please ignore at the time of merging
@api_view(['GET'])
def send_sms_link(phone_number):
    import json
    import urllib2
    response=""
    try:
        phone='9807148552';
        currentOTP='23322';
        TWO_FACTOR_SMS_API_KEY = "e239bb09-f16c-11e9-b828-0200cd936042";
        templateName='BOLOIN'

        sms_url         = 'https://2factor.in/API/R1/?module=PROMO_SMS&apikey='+TWO_FACTOR_SMS_API_KEY+'&to=%20'+phone+'%20&from=BOLOIN&msg=Please%20use%20below%20link%20to%20download%20bolo%20indya%20app.%20https%3A%2F%2Fbit.ly%2F2APNUpb'
        response        = urllib2.urlopen(sms_url).read()
        json_response   = json.loads( response )
        if json_response.has_key('Status') and json_response['Status'] == 'Success':
            return JsonResponse({'message': 'True'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'False'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return JsonResponse({'message': 'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)

class SingUpOTPView(generics.CreateAPIView):
    permission_classes  = (AllowAny,)
    serializer_class    = SingUpOTPSerializer

    """
    post:
        Required Parameters
        request.POST.get('is_reset_password')
        request.POST.get('is_for_change_phone')
    """

    def perform_create(self, serializer):
        old_otp = SingUpOTP.objects.filter(mobile_no=validate_indian_number(serializer.validated_data['mobile_no']).strip(),created_at__gte=datetime.now()-timedelta(hours=2)).order_by('-id')
        if old_otp:
            instance=old_otp[0]
            response, response_status   = send_sms(instance.mobile_no, instance.otp)
            instance.api_response_dump  = response
            instance.save()
        else:
            serializer.validated_data['mobile_no'] = validate_indian_number(serializer.validated_data['mobile_no']).strip()
            instance        = serializer.save()
            instance.otp    = generateOTP(6)
            instance.save()
            response, response_status   = send_sms(instance.mobile_no, instance.otp)
            instance.api_response_dump  = response
            instance.save()
        # response, response_status   = send_sms(instance.mobile_no, instance.otp)
        # instance.api_response_dump  = response
        if self.request.POST.get('is_reset_password') and self.request.POST.get('is_reset_password') == '1':
            instance.is_reset_password = True
        if self.request.POST.get('is_for_change_phone') and self.request.POST.get('is_for_change_phone') == '1':
            instance.is_for_change_phone = True
        # if not response_status:
        #     instance.is_active = False
        # instance.save()
        if not response_status:
            return JsonResponse({'message': 'OTP could not be sent'}, status=status.HTTP_417_EXPECTATION_FAILED)
        return JsonResponse({'message': 'OTP sent'}, status=status.HTTP_200_OK)

import calendar
@api_view(['POST'])
def get_user_bolo_info(request):
    """
    post:
        Required Parameters
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date',None)
        month = request.POST.get('month', None)
        year = request.POST.get('year',None)
    """
    try:
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date',None)
        month = request.POST.get('month', None)
        year = request.POST.get('year',None)
        total_earn = 0
        video_playtime = 0
        spent_time = 0
        total_view_count=0
        total_like_count=0
        total_comment_count = 0
        total_share_count = 0
        if start_date and end_date:
            start_date= datetime.strptime(start_date, "%d-%m-%Y")
            end_date = datetime.strptime(end_date+' 23:59:59', "%d-%m-%Y %H:%M:%S")
        elif month and year:
            days = calendar.monthrange(int(year),int(month))[1]
            start_date = datetime.strptime('01-'+str(month)+'-'+str(year), "%d-%m-%Y")
            end_date = datetime.strptime(str(days)+'-'+str(month)+'-'+str(year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
        if not start_date or not end_date:
            total_video = Topic.objects.filter(is_vb = True,is_removed=False,user=request.user)
            #total_video_id = list(Topic.objects.filter(is_vb = True,user=request.user).values_list('pk',flat=True))
            total_video_id = list(total_video.values_list('pk',flat=True))
            all_pay = UserPay.objects.filter(user=request.user,is_active=True)
            top_3_videos = Topic.objects.filter(is_vb = True,is_removed=False,user=request.user).order_by('-view_count')[:3]
            video_playtime = request.user.st.total_vb_playtime
        else:
            total_video = Topic.objects.filter(is_vb = True,is_removed=False,user=request.user,date__gte=start_date, date__lte=end_date)
            total_video_id = list(Topic.objects.filter(is_vb = True,user=request.user,is_removed=False).values_list('pk',flat=True))
            # total_video_id = list(total_video.values_list('pk',flat=True))
            all_pay = UserPay.objects.filter(user=request.user,is_active=True,for_month__gte=start_date.month,for_month__lte=start_date.month,\
                for_year__gte=start_date.year,for_year__lte=start_date.year)
            top_3_videos = Topic.objects.filter(is_vb = True,is_removed=False,user=request.user,date__gte=start_date, date__lte=end_date).order_by('-view_count')[:3]
            all_play_time = VideoPlaytime.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date,videoid__in = total_video_id).aggregate(Sum('playtime'))
            if all_play_time.has_key('playtime__sum') and all_play_time['playtime__sum']:
                video_playtime = all_play_time['playtime__sum']
            exclude_video_id = total_video.values_list('pk',flat=True)
            total_view_count += VBseen.objects.filter(created_at__gte = start_date, created_at__lte = end_date, topic__user = request.user).exclude(topic_id__in = exclude_video_id).count()
            total_like_count += Like.objects.filter(created_at__gte = start_date, created_at__lte = end_date, topic__user = request.user).exclude(topic_id__in = exclude_video_id).count()
            total_comment_count += Comment.objects.filter(date__gte = start_date, date__lte = end_date, topic__user = request.user).exclude(topic_id__in = exclude_video_id).count()
            total_share_count += SocialShare.objects.filter(created_at__gte = start_date, created_at__lte = end_date, topic__user = request.user).exclude(topic_id__in = exclude_video_id).count()

        for each_pay in all_pay:
            total_earn+=each_pay.amount_pay
        total_video_count = total_video.count()
        monetised_video_count = total_video.filter(is_monetized = True).count()
        unmonetizd_video_count= total_video.filter(is_monetized = False,is_moderated = True).count()
        left_for_moderation = total_video.filter(is_moderated = False).count()
        for each_vb in total_video:
            total_view_count+=each_vb.view_count
            total_like_count+=each_vb.likes_count
            total_comment_count+=each_vb.comment_count
            total_share_count+=each_vb.total_share_count
        total_view_count = shorcountertopic(total_view_count)
        total_comment_count = shorcountertopic(total_comment_count)
        total_like_count = shorcountertopic(total_like_count)
        total_share_count = shorcountertopic(total_share_count)
        video_playtime = short_time(video_playtime)
        return JsonResponse({'message': 'success', 'total_video_count' : total_video_count, \
                        'monetised_video_count':monetised_video_count, 'total_view_count':total_view_count,'total_comment_count':total_comment_count,\
                        'total_like_count':total_like_count,'total_share_count':total_share_count,'left_for_moderation':left_for_moderation,\
                        'total_earn':total_earn,'video_playtime':video_playtime,'spent_time':spent_time,\
                        'top_3_videos':TopicSerializer(top_3_videos,many=True, \
                            context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),\
                            'is_expand': request.GET.get('is_expand',True)}).data,'unmonetizd_video_count':unmonetizd_video_count,\
                        'bolo_score':shortcounterprofile(request.user.st.bolo_score)}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp(request):
    """
    post:
        Required Parameters
        mobile_no = request.POST.get('mobile_no', None)
        otp = request.POST.get('otp', None)
        request.POST.get('is_reset_password')
        request.POST.get('is_for_change_phone')
    """
    mobile_no = validate_indian_number(request.POST.get('mobile_no', None)).strip()
    language = request.POST.get('language','1')
    otp = request.POST.get('otp', None)
    is_geo_location = request.POST.get('is_geo_location',None)
    lat = request.POST.get('lat',None)
    lang = request.POST.get('lang',None)
    click_id = request.POST.get('click_id',None)
    user_ip = request.POST.get('user_ip',None)
    is_reset_password = False
    is_for_change_phone = False
    all_category_follow = []
    if request.POST.get('is_reset_password') and request.POST.get('is_reset_password') == '1':
        is_reset_password = True # inverted because of exclude
    if request.POST.get('is_for_change_phone') and request.POST.get('is_for_change_phone') == '1':
        is_for_change_phone = True

    if mobile_no and otp:
        try:
            # exclude_dict = {'is_active' : True, 'is_reset_password' : is_reset_password,"mobile_no":mobile_no, "otp":otp}
            exclude_dict = {'is_reset_password' : is_reset_password,"mobile_no":mobile_no, "otp":otp,"created_at__gte":datetime.now()-timedelta(hours=2)}
            if is_for_change_phone:
                # exclude_dict = {'is_active' : True, 'is_for_change_phone' : is_for_change_phone,"mobile_no":mobile_no, "otp":otp}
                exclude_dict = {'is_for_change_phone' : is_for_change_phone,"mobile_no":mobile_no, "otp":otp,"created_at__gte":datetime.now()-timedelta(hours=2)}

            otp_obj = SingUpOTP.objects.filter(**exclude_dict).order_by('-id')
            # if otp_obj:
            #     otp_obj=otp_obj[0]
            # otp_obj.is_active = False
            # otp_obj.used_at = timezone.now()
            otp_obj.update(used_at = timezone.now())
            if not is_reset_password and not is_for_change_phone and otp_obj:
                if mobile_no in ['7726080653']:
                    return JsonResponse({'message': 'Invalid Mobile No / OTP'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    userprofile = UserProfile.objects.get(mobile_no = mobile_no)
                except:
                    try:
                        userprofile = UserProfile.objects.get(Q(social_identifier='')|Q(social_identifier=None),mobile_no = mobile_no)
                    except MultipleObjectsReturned:
                        userprofile = UserProfile.objects.filter(Q(social_identifier='')|Q(social_identifier=None),mobile_no = mobile_no).order_by('id').last()
                        is_created=False
                    except:
                        userprofile = None
                if userprofile:
                    if not userprofile.user.is_active:
                        return JsonResponse({'message': 'You have been banned permanently for violating terms of usage.'}, status=status.HTTP_400_BAD_REQUEST)
                    user = userprofile.user
                    message = 'User Logged In'
                else:
                    user = User.objects.create(username = get_random_username())
                    message = 'User created'
                    userprofile = UserProfile.objects.get(user = user)
                    userprofile.mobile_no = mobile_no
                    Contact.objects.filter(contact_number=mobile_no).update(is_user_registered=True,user=user)
                    if user_ip:
                        user_ip_to_state_task.delay(user.id,user_ip)
                        # url = 'http://ip-api.com/json/'+user_ip
                        # response = urllib2.urlopen(url).read()
                        # json_response = json.loads(response)
                        # userprofile.state_name = json_response['regionName']
                        # userprofile.city_name = json_response['city']
                    if str(is_geo_location) =="1":
                        userprofile.lat = lat
                        userprofile.lang = lang
                    if click_id:
                        userprofile.click_id = click_id
                        click_url = 'http://res.taskbucks.com/postback/res_careeranna/dAppCheck?Ad_network_transaction_id='+str(click_id)+'&eventname=register'
                        response = urllib2.urlopen(click_url).read()
                        userprofile.click_id_response = str(response)
                    userprofile.save()
                    if str(language):
                        default_follow = deafult_boloindya_follow(user,str(language))
                    add_bolo_score(user.id, 'initial_signup', userprofile)
                user_tokens = get_tokens_for_user(user)
                otp_obj.update(for_user = user)
                # otp_obj.for_user = user
                # otp_obj.save()
                cache_follow_post.delay(user.id)
                cache_popular_post.delay(user.id,language)
                return JsonResponse({'message': message, 'username' : mobile_no, \
                        'access_token':user_tokens['access'], 'refresh_token':user_tokens['refresh'],'user':UserSerializer(user).data}, status=status.HTTP_200_OK)
            otp_obj.save()
            return JsonResponse({'message': 'OTP Validated', 'username' : mobile_no}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Invalid Mobile No / OTP'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No Mobile No / OTP provided'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def password_set(request):
    """
    post:
        Required Parameters
        password = request.POST.get('password', '')
    """
    password = request.POST.get('password', '')
    
    if password:
        try:
            user = request.user
            user.set_password( password )
            return JsonResponse({'message': 'Password updated!'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No user found/password provided'}, status=status.HTTP_204_NO_CONTENT)

class GetProfile(generics.ListAPIView):
    """
    post:
        Required Parameters
        user witc access and refresh code
    """
    serializer_class    = UserSerializer
    permission_classes  = (IsAuthenticatedOrReadOnly,)
    def get_queryset(self):
        user = self.request.user

        return [user]

@api_view(['POST'])
def cache_user_data(request):
    cache_follow_post.delay(request.user.id)
    cache_popular_post.delay(request.user.id,request.user.st.language)
    return JsonResponse({'message': 'Data Cached'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def fb_profile_settings(request):
    """
    post:
        Required Parameters
        activity        = request.POST.get('activity',None) #Mandatory [facebook_login,profile_save,settings_changed]
        profile_pic     = request.POST.get('profile_pic',None) #Optional
        name            = request.POST.get('name',None) #Optional
        bio             = request.POST.get('bio',None) #Optional
        about           = request.POST.get('about',None) #Optional
        username        = request.POST.get('username',None) #Optional
        refrence        = request.POST.get('refrence',None) #Optional
        extra_data      = request.POST.get('extra_data',None) #Optional
        language        = request.POST.get('language',None) #Optional
        sub_category_prefrences = request.POST.get('categories',None) #Optional
    """
    profile_pic     = request.POST.get('profile_pic',None)
    cover_pic       = request.POST.get('cover_pic',None)
    name            = request.POST.get('name',None)
    bio             = request.POST.get('bio',None)
    about           = request.POST.get('about',None)
    username        = request.POST.get('username',None)
    refrence        = request.POST.get('refrence',None)
    extra_data      = request.POST.get('extra_data',None)
    activity        = request.POST.get('activity',None)
    language        = request.POST.get('language','1')
    is_geo_location = request.POST.get('is_geo_location',None)
    likedin_url = request.POST.get('likedin_url',None)
    instagarm_id = request.POST.get('instagarm_id',None)
    twitter_id = request.POST.get('twitter_id',None)
    d_o_b = request.POST.get('d_o_b',None)
    gender = request.POST.get('gender',None)
    click_id = request.POST.get('click_id',None)
    lat = request.POST.get('lat',None)
    lang = request.POST.get('lang',None)
    user_ip = request.POST.get('user_ip',None)
    sub_category_prefrences = request.POST.get('categories',None)
    is_dark_mode_enabled = request.POST.get('is_dark_mode_enabled',None)
    android_did = request.POST.get('android_did',None)
    try:
        sub_category_prefrences = sub_category_prefrences.split(',')
    except:
        sub_category_prefrences = []
    if extra_data:
        extra_data = json.loads(extra_data)
    try:
        if activity == 'facebook_login' and refrence == 'facebook':
            try:
                userprofile = UserProfile.objects.get(social_identifier = extra_data['id'])
                user=userprofile.user
                is_created=False
            except MultipleObjectsReturned:
                userprofile = UserProfile.objects.filter(social_identifier = extra_data['id']).order_by('id').last()
                user=userprofile.user
                is_created=False
            except Exception as e:
                print e
                user_exists,num_user = check_user(extra_data['first_name'],extra_data['last_name'])
                #username = generate_username(extra_data['first_name'],extra_data['last_name'],num_user) if user_exists else str(str(extra_data['first_name'])+str(extra_data['last_name']))
                username = get_random_username()
                user = User.objects.create(username = username)
                userprofile = UserProfile.objects.get(user = user)
                is_created = True

            if not userprofile.user.is_active:
                return JsonResponse({'message': 'You have been banned permanently for violating terms of usage.'}, status=status.HTTP_400_BAD_REQUEST)
            cache_follow_post.delay(user.id)
            cache_popular_post.delay(user.id,language)
            if is_created:
                add_bolo_score(user.id, 'initial_signup', userprofile)
                user.first_name = extra_data['first_name']
                user.last_name = extra_data['last_name']
                userprofile.name = extra_data['name']
                userprofile.social_identifier = extra_data['id']
                userprofile.bio = bio
                if not userprofile.d_o_b and d_o_b:
                    add_bolo_score(user.id, 'dob_added', userprofile)
                userprofile.d_o_b = d_o_b
                if not userprofile.gender and gender:
                    add_bolo_score(user.id, 'gender_added', userprofile)
                if user_ip:
                    user_ip_to_state_task.delay(user.id,user_ip)
                    # url = 'http://ip-api.com/json/'+user_ip
                    # response = urllib2.urlopen(url).read()
                    # json_response = json.loads(response)
                    # userprofile.state_name = json_response['regionName']
                    # userprofile.city_name = json_response['city']
                userprofile.gender = gender
                userprofile.about = about
                userprofile.refrence = refrence
                userprofile.extra_data = extra_data
                userprofile.user = user
                userprofile.bolo_score += 95
                userprofile.linkedin_url = likedin_url
                userprofile.twitter_id = twitter_id
                userprofile.instagarm_id = instagarm_id

                # userprofile.follow_count += 1
                if str(is_geo_location) =="1":
                    userprofile.lat = lat
                    userprofile.lang = lang
                if click_id:
                    userprofile.click_id = click_id
                    click_url = 'http://res.taskbucks.com/postback/res_careeranna/dAppCheck?Ad_network_transaction_id='+str(click_id)+'&eventname=register'
                    response = urllib2.urlopen(click_url).read()
                    userprofile.click_id_response = str(response)
                userprofile.save()
                if str(language):
                    default_follow = deafult_boloindya_follow(user,str(language))
                userprofile.language = str(language)
                userprofile.save()
                user.save()
                user_tokens = get_tokens_for_user(user)
                return JsonResponse({'message': 'User created', 'username' : user.username,'access':user_tokens['access'],'refresh':user_tokens['refresh'],'user':UserSerializer(user).data}, status=status.HTTP_200_OK)
            else:
                user_tokens = get_tokens_for_user(user)
                return JsonResponse({'message': 'User Logged In', 'username' :user.username ,'access':user_tokens['access'],'refresh':user_tokens['refresh'],'user':UserSerializer(user).data}, status=status.HTTP_200_OK)
        elif activity == 'google_login' and refrence == 'google':
            try:
                userprofile = UserProfile.objects.get(social_identifier = extra_data['google_id'])
                user=userprofile.user
                is_created=False
            except MultipleObjectsReturned:
                userprofile = UserProfile.objects.filter(social_identifier = extra_data['id']).order_by('id').last()
                user=userprofile.user
                is_created = False
            except Exception as e:
                print e
                # user_exists,num_user = check_user(extra_data['first_name'],extra_data['last_name'])
                #username = generate_username(extra_data['first_name'],extra_data['last_name'],num_user) if user_exists else str(str(extra_data['first_name'])+str(extra_data['last_name']))
                username = get_random_username()
                user = User.objects.create(username = username)
                userprofile = UserProfile.objects.get(user = user)
                is_created = True
            if not userprofile.user.is_active:
                return JsonResponse({'message': 'You have been banned permanently for violating terms of usage.'}, status=status.HTTP_400_BAD_REQUEST)
            cache_follow_post.delay(user.id)
            cache_popular_post.delay(user.id,language)
            if is_created:
                add_bolo_score(user.id, 'initial_signup', userprofile)
                # user.first_name = extra_data['first_name']
                # user.last_name = extra_data['last_name']
                userprofile.name = extra_data['name']
                userprofile.social_identifier = extra_data['google_id']
                userprofile.bio = bio
                if extra_data['profile_pic']:
                    userprofile.profile_pic = profile_pic
                if not userprofile.d_o_b and d_o_b:
                    add_bolo_score(user.id, 'dob_added', userprofile)
                userprofile.d_o_b = d_o_b
                if not userprofile.gender and gender:
                    add_bolo_score(user.id, 'gender_added', userprofile)
                if user_ip:
                    user_ip_to_state_task.delay(user.id,user_ip)
                    # url = 'http://ip-api.com/json/'+user_ip
                    # response = urllib2.urlopen(url).read()
                    # json_response = json.loads(response)
                    # userprofile.state_name = json_response['regionName']
                    # userprofile.city_name = json_response['city']
                userprofile.gender = gender
                userprofile.about = about
                userprofile.refrence = refrence
                userprofile.extra_data = extra_data
                userprofile.user = user
                userprofile.bolo_score += 95
                userprofile.linkedin_url = likedin_url
                userprofile.twitter_id = twitter_id
                userprofile.instagarm_id = instagarm_id

                # userprofile.follow_count += 1
                if str(is_geo_location) =="1":
                    userprofile.lat = lat
                    userprofile.lang = lang
                if click_id:
                    userprofile.click_id = click_id
                    click_url = 'http://res.taskbucks.com/postback/res_careeranna/dAppCheck?Ad_network_transaction_id='+str(click_id)+'&eventname=register'
                    response = urllib2.urlopen(click_url).read()
                    userprofile.click_id_response = str(response)
                userprofile.save()
                if str(language):
                    default_follow = deafult_boloindya_follow(user,str(language))
                userprofile.language = str(language)
                userprofile.save()
                user.save()
                user_tokens = get_tokens_for_user(user)
                return JsonResponse({'message': 'User created', 'username' : user.username,'access':user_tokens['access'],'refresh':user_tokens['refresh'],'user':UserSerializer(user).data}, status=status.HTTP_200_OK)
            else:
                user_tokens = get_tokens_for_user(user)
                return JsonResponse({'message': 'User Logged In', 'username' :user.username ,'access':user_tokens['access'],'refresh':user_tokens['refresh'],'user':UserSerializer(user).data}, status=status.HTTP_200_OK)
        elif activity == 'profile_save':
            try:
                userprofile = UserProfile.objects.get(user = request.user)
                userprofile.name= name
                userprofile.bio = bio
                userprofile.about = about
                if not userprofile.d_o_b and d_o_b:
                    add_bolo_score(userprofile.user.id, 'dob_added', userprofile)
                userprofile.d_o_b = d_o_b
                if not userprofile.gender and gender:
                    add_bolo_score(userprofile.user.id, 'gender_added', userprofile)
                if str(is_dark_mode_enabled) == '1':
                    userprofile.is_dark_mode_enabled = True
                else:
                    userprofile.is_dark_mode_enabled = False
                if user_ip:
                    user_ip_to_state_task.delay(request.user.id,user_ip)
                    # url = 'http://ip-api.com/json/'+user_ip
                    # response = urllib2.urlopen(url).read()
                    # json_response = json.loads(response)
                    # userprofile.state_name = json_response['regionName']
                    # userprofile.city_name = json_response['city']
                userprofile.gender = gender
                userprofile.profile_pic =profile_pic
                userprofile.cover_pic=cover_pic
                userprofile.linkedin_url = likedin_url
                userprofile.twitter_id = twitter_id
                userprofile.instagarm_id = instagarm_id
                userprofile.save()
                if username:
                    if not check_username_valid(username):
                        return JsonResponse({'message': 'Username Invalid. It can contains only lower case letters,numbers and special character[ _ - .]'}, status=status.HTTP_200_OK)
                    check_username = User.objects.filter(username = username).exclude(pk =request.user.id)
                    if not check_username:
                        userprofile.slug = username
                        user = userprofile.user
                        user.username = username
                        userprofile.save()
                        user.save()
                    else:
                        return JsonResponse({'message': 'Username already exist'}, status=status.HTTP_200_OK)
                return JsonResponse({'message': 'Profile Saved'}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)
        elif activity == 'settings_changed':
            try:
                userprofile = UserProfile.objects.get(user = request.user)
                userprofile.linkedin_url = likedin_url
                userprofile.twitter_id = twitter_id
                userprofile.instagarm_id = instagarm_id
                if sub_category_prefrences:
                    for each_sub_category in sub_category_prefrences:
                        category = Category.objects.get(pk = each_sub_category)
                        userprofile.sub_category.add(category)
                        userprofile.save()
                    if userprofile.sub_category.all():
                        for each_category in userprofile.sub_category.all():
                            if not str(each_category.id) in sub_category_prefrences:
                                userprofile.sub_category.remove(each_category)
                if language:
                    default_follow = deafult_boloindya_follow(request.user,str(language))
                    userprofile.language = str(language)
                    cache_popular_post.delay(request.user.id,language)
                    userprofile.save()
                return JsonResponse({'message': 'Settings Chnaged'}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)
        elif activity == 'android_login':
            try:
                userprofile = UserProfile.objects.get(android_did = android_did,user__is_active = True)
                user=userprofile.user
                is_created=False
            except Exception as e:
                print e
                username = get_random_username()
                user = User.objects.create(username = username)
                userprofile = UserProfile.objects.get(user = user)
                is_created = True
            if not userprofile.is_guest_user:
                userprofile.is_guest_user = True
                userprofile.save()
            cache_follow_post.delay(user.id)
            cache_popular_post.delay(user.id,language)
            if is_created:
                add_bolo_score(user.id, 'initial_signup', userprofile)
                if user_ip:
                    user_ip_to_state_task.delay(user.id,user_ip)
                if str(is_geo_location) =="1":
                    userprofile.lat = lat
                    userprofile.lang = lang
                if click_id:
                    userprofile.click_id = click_id
                    click_url = 'http://res.taskbucks.com/postback/res_careeranna/dAppCheck?Ad_network_transaction_id='+str(click_id)+'&eventname=register'
                    response = urllib2.urlopen(click_url).read()
                    userprofile.click_id_response = str(response)
                userprofile.save()
                if str(language):
                    default_follow = deafult_boloindya_follow(user,str(language))
                userprofile.language = str(language)
                userprofile.save()
                user.save()
                user_tokens = get_tokens_for_user(user)
                return JsonResponse({'message': 'User created', 'username' : user.username,'access':user_tokens['access'],'refresh':user_tokens['refresh'],'user':UserSerializer(user).data}, status=status.HTTP_200_OK)
            else:
                user_tokens = get_tokens_for_user(user)
                return JsonResponse({'message': 'User Logged In', 'username' :user.username ,'access':user_tokens['access'],'refresh':user_tokens['refresh'],'user':UserSerializer(user).data}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

#### KYC Views ####

@api_view(['POST'])
def get_kyc_status(request):
    try:
        user_kyc,is_created = UserKYC.objects.get_or_create(user = request.user)
        return JsonResponse({'message': 'success','user_kyc':UserKYCSerializer(user_kyc).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def save_kyc_basic_info(request):
    try:
        first_name = request.POST.get('first_name',None)
        middle_name = request.POST.get('middle_name',None)
        last_name = request.POST.get('last_name',None)
        d_o_b = request.POST.get('d_o_b',None)
        mobile_no = request.POST.get('mobile_no',None)
        email = request.POST.get('email',None)
        data_dict = {
        'first_name':first_name,
        'middle_name':middle_name,
        'last_name':last_name,
        'd_o_b':d_o_b,
        'mobile_no':mobile_no,
        'email':email,
        'user':request.user
        }
        if not (first_name and d_o_b and (mobile_no or email)):
            return JsonResponse({'message': 'Mandatory Data Missing'}, status=status.HTTP_400_BAD_REQUEST)

        user_kyc,is_created = UserKYC.objects.get_or_create(user=request.user)
        kyc_basic_info,kyc_basic_info_is_created = KYCBasicInfo.objects.update_or_create(user=request.user,defaults=data_dict)
        if not kyc_basic_info_is_created:
            kyc_basic_info.is_rejected = False
            kyc_basic_info.is_active = True
            kyc_basic_info.save()

        user_kyc.kyc_basic_info_submitted = True
        user_kyc.save()
        return JsonResponse({'message': 'basic_info_saved'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def save_kyc_documents(request):
    try:
        document_type = request.POST.get('document_type',None)
        frontside_url = request.POST.get('frontside_url',None)
        backside_url = request.POST.get('backside_url',None)
        data_dict = {
            'kyc_document_type_id':document_type,
            'frontside_url':frontside_url,
            'backside_url':backside_url,
            'user':request.user
        }
        kyc_document_type = KYCDocumentType.objects.get(pk=document_type)
        if (not frontside_url or not backside_url) and kyc_document_type.no_image_required == 2:
            return JsonResponse({'message': 'Need front and back both images url'}, status=status.HTTP_400_BAD_REQUEST)
        elif not frontside_url and kyc_document_type.no_image_required == 1:
            return JsonResponse({'message': 'please share the front image url'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                kyc_document = KYCDocument.objects.get(kyc_document_type=document_type,user=request.user,is_active=True)
                kyc_document.is_active=False
                kyc_document.save()
            except:
                pass
            kyc_document = KYCDocument.objects.create(**data_dict)
            user_kyc = UserKYC.objects.get(user=request.user)
            if kyc_document_type.document_name in ['PAN','pan']:
                message = 'PAN Info Saved'
                user_kyc.kyc_pan_info_submitted = True
                user_kyc.save()
            else:
                message = 'Document Info Saved'
                user_kyc.kyc_document_info_submitted = True
                user_kyc.save()
        return JsonResponse({'message': message}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def save_kyc_selfie(request):
    try:
        pic_selfie_url = request.POST.get('pic_selfie_url',None)
        data_dict={
        'pic_selfie_url':pic_selfie_url,
        'user':request.user
        }
        user_kyc = UserKYC.objects.get(user=request.user)
        selfie_info,is_created = KYCBasicInfo.objects.update_or_create(user=request.user,defaults=data_dict)
        if not is_created:
            selfie_info.is_rejected = False
            selfie_info.is_active = True
            selfie_info.save()
        user_kyc.kyc_selfie_info_submitted = True
        user_kyc.save()
        return JsonResponse({'message': 'additional info saved'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def save_kyc_additional_info(request):
    try:
        father_firstname = request.POST.get('father_firstname',None)
        father_lastname = request.POST.get('father_lastname',None)
        mother_firstname = request.POST.get('mother_firstname',None)
        mother_lastname = request.POST.get('mother_lastname',None)
        profession = request.POST.get('profession',None)
        marrigae_status = request.POST.get('status',None)
        data_dict={
        'father_firstname':father_firstname,
        'father_lastname':father_lastname,
        'mother_firstname':mother_firstname,
        'mother_lastname':mother_lastname,
        'profession':profession,
        'status':marrigae_status,
        'user':request.user
        }
        user_kyc = UserKYC.objects.get(user=request.user)
        additional_info,is_created = AdditionalInfo.objects.update_or_create(user=request.user,defaults=data_dict)
        user_kyc.kyc_additional_info_submitted = True
        user_kyc.save()
        return JsonResponse({'message': 'additional info saved'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def save_bank_details_info(request):
    try:
        mode_of_transaction = request.POST.get('mode_of_transaction',None)
        account_name = request.POST.get('account_name',None)
        account_number = request.POST.get('account_number',None)
        IFSC_code = request.POST.get('IFSC_code',None)
        paytm_number = request.POST.get('paytm_number',None)
        if mode_of_transaction:
            if mode_of_transaction=='1' and not (account_name and account_number and IFSC_code):
                return JsonResponse({'message': 'Mandatory Bank Data Missing'}, status=status.HTTP_400_BAD_REQUEST)
            elif mode_of_transaction=='2' and not paytm_number:
                return JsonResponse({'message': 'Mandatory Paytm Data Missing'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'message': 'Mode Of Transaction Missing'}, status=status.HTTP_400_BAD_REQUEST)
        data_dict = {
            'account_number':account_number,
            'account_name':account_name,
            'IFSC_code':IFSC_code,
            'user':request.user
        }
        user_kyc = UserKYC.objects.get(user=request.user)
        if mode_of_transaction == '1':
            try:
                user_bank_details = BankDetail.objects.get(user=request.user ,is_active=True)
                user_bank_details.is_active = False
                user_bank_details.save()
            except:
                pass
            user_bank_details = BankDetail.objects.create(**data_dict)
            user_kyc.kyc_bank_details_submitted = True
            message = 'bank details saved'
        elif mode_of_transaction == '2':
            try:
                user_bank_details = BankDetail.objects.get(user=request.user ,is_active=True)
                user_bank_details.is_active = False
                user_bank_details.save()
            except:
                pass
            user_bank_details = BankDetail.objects.create(user=request.user,paytm_number=paytm_number)
            user_kyc.mode_of_transaction = 2
            message = 'payment to paytm'
        user_kyc.is_kyc_completed=True
        user_kyc.save()
        return JsonResponse({'message': message}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_bolo_details(request):
    try:
        username = request.GET.get('username',None)
        user = User.objects.get(username=username)
        kyc_details,is_careted = UserKYC.objects.get_or_create(user=user)
        all_encash_details = EncashableDetail.objects.filter(user = user).order_by('-id')
        return JsonResponse({'all_encash_details': EncashableDetailSerializer(all_encash_details).data,'kyc_details':UserKYCSerializer(kyc_details).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)





def generate_username(first,last,num_of_users):
    username=first+last+str(num_of_users)
    while(check_username(username)):
        num_of_users+=1
        username=first+last+str(num_of_users)
    return username

def check_username(name):
    return User.objects.filter(username__iexact=name)


def check_user(first,last):
    all_users = User.objects.filter(first_name__iexact=first,last_name__iexact=last)    
    if all_users:
        return True,len(all_users)
    else:
        return False,0

@api_view(['POST'])
def follow_user(request):
    """
    post:
        Required Parameters
        user_following_id = request.POST.get('user_following_id',None)
    """
    user_following_id = request.POST.get('user_following_id',None)
    try:
        follow,is_created = Follower.objects.get_or_create(user_follower = request.user,user_following_id=user_following_id)
        userprofile = UserProfile.objects.get(user = request.user)
        followed_user = UserProfile.objects.get(user_id = user_following_id)
        if is_created:
            add_bolo_score(request.user.id, 'follow', userprofile)
            add_bolo_score(user_following_id, 'followed', followed_user)
            userprofile.follow_count = F('follow_count')+1
            userprofile.save()
            followed_user.follower_count = F('follower_count')+1
            followed_user.save()
            update_redis_following(request.user.id,int(user_following_id),True)
            update_redis_follower(int(user_following_id),request.user.id,True)
            return JsonResponse({'message': 'Followed'}, status=status.HTTP_200_OK)
        else:
            if follow.is_active:
                follow.is_active = False
                follow.save()
                userprofile.follow_count = F('follow_count')-1
                followed_user.follower_count = F('follower_count')-1
                userprofile.save()
                followed_user.save()
                update_redis_following(request.user.id,int(user_following_id),False)
                update_redis_follower(int(user_following_id),request.user.id,False)
                return JsonResponse({'message': 'Unfollowed'}, status=status.HTTP_200_OK)
            else:
                follow.is_active = True
                userprofile.follow_count = F('follow_count')+1
                followed_user.follower_count = F('follower_count')+1
                follow.save()
                followed_user.save()
                userprofile.save()
                update_redis_following(request.user.id,int(user_following_id),True)
                update_redis_follower(int(user_following_id),request.user.id,True)
                return JsonResponse({'message': 'Followed'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def follow_sub_category(request):
    """
    post:
        Required Parameters
        user_sub_category_id = request.POST.get('sub_category_id',None)
    """
    user_sub_category_id = request.POST.get('sub_category_id',None)
    try:
        userprofile = UserProfile.objects.get(user = request.user)
        all_sub_category = userprofile.sub_category.all().values_list('id', flat=True)
        for each_sub_category in all_sub_category:
            if str(each_sub_category) == str(user_sub_category_id):
                userprofile.sub_category.remove(Category.objects.get(pk = user_sub_category_id))
                return JsonResponse({'message': 'Unfollowed'}, status=status.HTTP_200_OK)
            else:
                category = Category.objects.get(pk = user_sub_category_id)
                userprofile.sub_category.add(category)
                userprofile.save()
                return JsonResponse({'message': 'Followed'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def like(request):
    """
    post:
        Required Parameters
        topic_id = request.POST.get('topic_id',None)
    """
    topic_id = request.POST.get('topic_id',None)
    comment_id = request.POST.get('comment_id',None)
    userprofile = UserProfile.objects.get(user = request.user)
    try:
        if topic_id:
            liked,is_created = Like.objects.get_or_create(topic_id = topic_id,user = request.user)
            acted_obj = Topic.objects.get(pk = topic_id)
        elif comment_id:
            liked,is_created = Like.objects.get_or_create(comment_id = comment_id,user = request.user)
            acted_obj = Comment.objects.get(pk = comment_id)
        if is_created:
            acted_obj.likes_count = F('likes_count')+1
            if topic_id:
                acted_obj.topic_like_count = F('topic_like_count')+1
            acted_obj.save()
            add_bolo_score(request.user.id, 'liked', acted_obj)
            userprofile.like_count = F('like_count')+1
            userprofile.save()
            return JsonResponse({'message': 'liked'}, status=status.HTTP_200_OK)
        else:
            if liked.like:
                liked.like = False
                liked.save()
                acted_obj.likes_count = F('likes_count')-1
                if topic_id:
                    acted_obj.topic_like_count = F('topic_like_count')-1
                acted_obj.save()
                userprofile.like_count = F('like_count')-1
                userprofile.save()
                return JsonResponse({'message': 'unliked'}, status=status.HTTP_200_OK)
            else:
                liked.like = True
                liked.save()
                acted_obj.likes_count = F('likes_count')+1
                if topic_id:
                    acted_obj.topic_like_count = F('topic_like_count')+1
                acted_obj.save()
                userprofile.like_count = F('like_count')+1
                userprofile.save()
                return JsonResponse({'message': 'liked'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def shareontimeline(request):
    """
    post:
        Required Parameters
        topic_id = request.POST.get('topic_id',None)
        topic_id = request.POST.get('topic_id',None)
        share_on = request.POST.get('share_on',None)
    """
    topic_id = request.POST.get('topic_id',None)
    share_on = request.POST.get('share_on',None)
    userprofile = UserProfile.objects.get(user = request.user)
    if share_on == 'share_timeline':
        try:
            shared = ShareTopic.objects.create(topic_id = topic_id,user = request.user)
            add_bolo_score(request.user.id, 'share_timeline', liked)
            topic = Topic.objects.get(pk = topic_id)
            topic.share_count = F('share_count')+1
            topic.total_share_count = F('total_share_count')+1
            topic.topic_share_count = F('topic_share_count')+1
            topic.save()
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)
    elif share_on == 'facebook_share':
        try:
            shared = SocialShare.objects.create(topic_id = topic_id,user = request.user,share_type = '0')
            topic = Topic.objects.get(pk = topic_id)
            topic.facebook_share_count = F('facebook_share_count')+1    
            topic.total_share_count = F('total_share_count')+1
            topic.topic_share_count = F('topic_share_count')+1
            topic.save()
            add_bolo_score(request.user.id, 'facebook_share', topic)
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'fb shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)
    elif share_on == 'whatsapp_share':
        try:
            shared = SocialShare.objects.create(topic_id = topic_id,user = request.user,share_type = '1')
            topic = Topic.objects.get(pk = topic_id)
            topic.whatsapp_share_count = F('whatsapp_share_count')+1
            topic.total_share_count = F('total_share_count')+1
            topic.topic_share_count = F('topic_share_count')+1
            topic.save()
            add_bolo_score(request.user.id, 'whatsapp_share', topic)
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'whatsapp shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)
    elif share_on == 'linkedin_share':
        try:
            shared = SocialShare.objects.create(topic_id = topic_id,user = request.user,share_type = '2')
            topic = Topic.objects.get(pk = topic_id)
            topic.linkedin_share_count = F('linkedin_share_count')+1
            topic.total_share_count = F('total_share_count')+1
            topic.topic_share_count = F('topic_share_count')+1
            topic.save()
            add_bolo_score(request.user.id, 'linkedin_share', topic)
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'linkedin shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)
    elif share_on == 'twitter_share':
        try:
            shared = SocialShare.objects.create(topic_id = topic_id,user = request.user,share_type = '3')
            topic = Topic.objects.get(pk = topic_id)
            topic.twitter_share_count = F('twitter_share_count')+1
            topic.total_share_count = F('total_share_count')+1
            topic.topic_share_count = F('topic_share_count')+1
            topic.save()
            add_bolo_score(request.user.id, 'twitter_share', topic)
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'twitter shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

def comment_view(request):
    topic_id = request.GET.get('topic_id',None)
    """
    get:
        Required Parameters
        comment_ids = request.GET.get('comment_ids',None)
    """
    #### add models for seen users
    try:
        # comment_list = comment_ids.split(',')
        # for each_comment_id in comment_list:
        topic = Topic.objects.get(pk = topic_id)
        # topic= comment.topic
        topic.view_count = F('view_count') +1
        topic.imp_count = F('imp_count') +1
        topic.save()
        userprofile = topic.user.st
        userprofile.view_count = F('view_count')+1
        userprofile.own_vb_view_count = F('own_vb_view_count') +1
        userprofile.save()
        return JsonResponse({'message': 'item viewed'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def vb_seen(request):
    topic_id = request.POST.get('topic_id',None)
    """
    get:
        Required Parameters
        topic_id = request.POST.get('topic_id',None)
        authorixation token
    """
    #### add models for seen users
    try:
        # comment_list = comment_ids.split(',')
        # for each_comment_id in comment_list:
        topic = Topic.objects.get(pk = topic_id)
        # topic= comment.topic
        topic.view_count = F('view_count')+1
        topic.imp_count = F('imp_count') +1
        topic.save()
        userprofile = topic.user.st
        userprofile.view_count = F('view_count')+1
        userprofile.own_vb_view_count = F('own_vb_view_count') +1
        userprofile.save()
        all_vb_seen = get_redis_vb_seen(request.user.id)
        # vbseen = VBseen.objects.filter(user = request.user,topic_id = topic_id)
        if not topic_id in all_vb_seen:
            vbseen = VBseen.objects.create(user = request.user,topic_id = topic_id)
            update_redis_vb_seen(request.user.id,topic_id)
            add_bolo_score(topic.user.id, 'vb_view', vbseen)
        else:
            vbseen = VBseen.objects.create(user = request.user,topic_id = topic_id)
        return JsonResponse({'message': 'vb seen'}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def follow_like_list(request):
    try:
        comment_like = Like.objects.filter(user = request.user,like = True,topic_id__isnull = True).values_list('comment_id', flat=True)
        topic_like = Like.objects.filter(user = request.user,like = True,comment_id__isnull = True).values_list('topic_id', flat=True)
        # all_follow = Follower.objects.filter(user_follower = request.user,is_active = True).values_list('user_following_id', flat=True)
        all_follow = get_redis_following(request.user.id)
        # all_follower = Follower.objects.filter(user_following = request.user,is_active = True).values_list('user_follower_id', flat=True)
        all_follower = get_redis_follower(request.user.id)
        userprofile = UserProfile.objects.get(user = request.user)
        all_category_follow = userprofile.sub_category.all().values_list('id', flat=True)
        detialed_category = userprofile.sub_category.all()
        app_version = AppVersion.objects.get(app_name = 'android')
        app_version = AppVersionSerializer(app_version).data
        notification_count = Notification.objects.filter(for_user= request.user,status=0).count()
        block_hashes = TongueTwister.objects.filter(is_blocked=True).values_list('hash_tag', flat=True)
        reported_user = Report.objects.filter(reported_by=request.user,target_type=ContentType.objects.get(model='user')).distinct('target_id').values_list('target_id',flat=True)
        reported_topic = Report.objects.filter(reported_by=request.user,target_type=ContentType.objects.get(model='topic')).distinct('target_id').values_list('target_id',flat=True)
        cache_follow_post.delay(request.user.id)
        cache_popular_post.delay(request.user.id,request.user.st.language)
        return JsonResponse({'comment_like':list(comment_like),'topic_like':list(topic_like),'all_follow':list(all_follow),'all_follower':list(all_follower),\
            'all_category_follow':list(all_category_follow),'app_version':app_version,\
            'notification_count':notification_count, 'is_test_user':userprofile.is_test_user,'user':UserSerializer(request.user).data,\
            'detialed_category':CategorySerializer(detialed_category,many = True).data,'block_hashes':list(block_hashes),\
            'reported_user':list(reported_user),'reported_topic':list(reported_topic)},status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def my_app_version(request):
    try:
        app_version = AppVersion.objects.get(app_name = 'android')
        app_version = AppVersionSerializer(app_version).data
        return JsonResponse({'app_version':app_version}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_follow_user(request):
    try:
        language = request.POST.get('language', None)
        #all_follow_id = Follower.objects.filter(user_follower = request.user,is_active = True).values_list('user_following_id', flat=True)
        #all_vb_of_follower = Topic.objects.filter(is_vb=True,is_removed=False,user_id__in=all_follow_id).values_list('user_id',flat=True)
        #if all_vb_of_follower:
        #    all_user = User.objects.filter(pk__in = all_vb_of_follower)
        #    return JsonResponse({'all_follow':UserSerializer(all_user,many= True).data}, status=status.HTTP_200_OK)
        all_user = []
        if language:
            all_user = User.objects.filter(st__is_popular = True, st__language=language)
        else:
            all_user = User.objects.filter(st__is_popular = True)
        if all_user.count():
            return JsonResponse({'all_follow':UserSerializer(all_user.order_by('?'), many= True).data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'all_follow':[]}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

class GetFollowigList(generics.ListCreateAPIView):
    serializer_class   = UserSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class    = LimitOffsetPagination

    def get_queryset(self):
        # all_following_id = Follower.objects.filter(user_following_id = self.request.GET.get('user_id', ''),is_active = True).values_list('user_follower_id', flat=True)
        all_following_id = None
        if self.request.GET.get('user_id', None):
            all_following_id = get_redis_follower(self.request.GET.get('user_id', None))
        all_user = User.objects.filter(pk__in = all_following_id)
        return all_user

class GetFollowerList(generics.ListCreateAPIView):
    serializer_class   = UserSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class    = LimitOffsetPagination

    def get_queryset(self):
        # all_follower_id = Follower.objects.filter(user_follower_id = self.request.GET.get('user_id', ''),is_active = True).values_list('user_following_id', flat=True)
        all_follower_id = None
        if self.request.GET.get('user_id', None):
            all_follower_id = get_redis_following(self.request.GET.get('user_id', None))
        all_user = User.objects.filter(pk__in = all_follower_id)
        return all_user
    
@api_view(['POST'])
def get_following_list(request):
    try:
        # all_following_id = Follower.objects.filter(user_following_id = request.POST.get('user_id', ''),is_active = True).values_list('user_follower_id', flat=True)[:50]
        all_following_id = None
        if request.POST.get('user_id', None):
            all_following_id = get_redis_follower(request.POST.get('user_id', None))
        if all_following_id:
            all_user = User.objects.filter(pk__in = all_following_id)
            return JsonResponse({'result':UserSerializer(all_user,many= True).data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'result':[]}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_follower_list(request):
    try:
        # all_follower_id = Follower.objects.filter(user_follower_id = request.POST.get('user_id', ''),is_active = True).values_list('user_following_id', flat=True)[:50]
        all_follower_id = None
        if request.POST.get('user_id', None):
            all_follower_id = get_redis_following(request.POST.get('user_id', None))
        if all_follower_id:
            all_user = User.objects.filter(pk__in = all_follower_id)
            return JsonResponse({'result':UserSerializer(all_user,many= True).data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'result':[]}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)


def deafult_boloindya_follow(user,language):
    try:
        if language == '2':
            bolo_indya_user = User.objects.get(username = 'boloindya_hindi')
        elif language == '3':
            bolo_indya_user = User.objects.get(username = 'boloindya_tamil')
        elif language == '4':
            bolo_indya_user = User.objects.get(username = 'boloindya_telgu')
        else:
            bolo_indya_user = User.objects.get(username = 'boloindya')
        follow,is_created = Follower.objects.get_or_create(user_follower = user,user_following=bolo_indya_user)
        if is_created:
            add_bolo_score(user.id, 'follow', follow)
            userprofile = UserProfile.objects.get(user = user)
            bolo_indya_profile = UserProfile.objects.get(user = bolo_indya_user)
            userprofile.follow_count = F('follow_count') + 1
            userprofile.save()
            bolo_indya_profile.follower_count = F('follower_count') + 1
            bolo_indya_profile.save()
            update_redis_following(user.id,int(bolo_indya_user.id),True)
            update_redis_follower(int(bolo_indya_user.id),user.id,True)
        if not follow.is_active:
            follow.is_active = True
            follow.save()
            update_redis_following(user.id,int(bolo_indya_user.id),True)
            update_redis_follower(int(bolo_indya_user.id),user.id,True)
        return True
    except:
        return False

@api_view(['POST'])
def get_bolo_score(request):
    try:
        userprofile = UserProfile.objects.get(user = request.user)
        return JsonResponse({'bolo_score':userprofile.bolo_score,'message':'success'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

####
# Prediction
####

class CricketMatchList(generics.ListCreateAPIView):
    serializer_class    = CricketMatchSerializer
    # queryset            = CricketMatch.objects.filter(is_active = True)
    permission_classes  = (IsAuthenticatedOrReadOnly,)
    # pagination_class    = LimitOffsetPagination
    pagination_class = None

    def get_queryset(self):
        matches = []
        startdate = datetime.today().date()
        enddate = startdate - timedelta(days=1)
        match_list_1 = CricketMatch.objects.filter(match_datetime__gte=startdate).order_by('match_datetime')
        match_list_2 = CricketMatch.objects.filter(match_datetime__lte=startdate).order_by('match_datetime')
        if match_list_1:
            for each in match_list_1:
                matches.append(each)
        if match_list_2:
            for each in match_list_2:
                matches.append(each)
        return matches


@api_view(['POST'])
def get_single_match(request):
    """
    post:
        Required Parameters
        password = request.POST.get('password', '')
    """
    match_id = request.POST.get('match_id', '')
    
    if match_id:
        try:
            cricket_match = CricketMatch.objects.get(pk=match_id)
            cricketmatch_json = CricketMatchSerializer(cricket_match).data
            polls = Poll.objects.filter(cricketmatch = cricket_match,is_active = True)
            polls_json = PollSerializer(polls,many=True).data
            new_polls_json = []
            if polls:
                for each in polls_json:
                    try:
                        Voting.objects.get(poll_id=each['id'],user = request.user)
                        voting_status = True
                    except:
                        voting_status = False
                    each['voting_status'] = voting_status
                    new_polls_json.append(each)
            return JsonResponse({'message': 'success','polls':new_polls_json,\
                    'cricketmatch':cricketmatch_json, 'prediction_start_hour' : settings.PREDICTION_START_HOUR}, \
                        status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No user found/password provided'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def get_single_poll(request):
    """
    post:
        Required Parameters
        password = request.POST.get('password', '')
    """
    poll_id = request.POST.get('poll_id', '')
    if poll_id:
        try:
            poll = Poll.objects.get(pk=poll_id)
            polls_json = PollSerializerwithChoice(poll).data
            new_polls_json = []
            if poll:
                try:
                    voted = Voting.objects.get(poll_id=polls_json['id'],user = request.user)
                    if voted:
                        voted_on = OnlyChoiceSerializer(voted.choice, many = False).data
                except:
                     voted_on = {}
                polls_json['voted_on'] = voted_on
            return JsonResponse({'message': 'success', 'polls' : polls_json, 'prediction_start_hour' : settings.PREDICTION_START_HOUR}\
                        , status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No user found/password provided'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def predict(request):
    """
    post:
        Required Parameters
        password = request.POST.get('password', '')
    """
    poll_id = request.POST.get('poll_id', '')
    choice_id = request.POST.get('choice_id', '')
    message = ''
    
    if request.user:
        try:
            poll = Poll.objects.get(pk=poll_id)
            cricketmatch = poll.cricketmatch
            try:
                voted = Voting.objects.get(poll_id = poll_id,user= request.user)
                is_created = False
            except:
                voted = Voting.objects.create(poll_id = poll_id,user= request.user,choice_id = choice_id)
                is_created = True
            if is_created:
                voted.cricketmatch = poll.cricketmatch
                message = "Prediction Created"
            else:
                if not str(voted.choice_id)  == str(choice_id):
                    voted.choice_id = choice_id
                    message = "Prediction Updated"
                else:
                    message = "No change"
            voted.save()
            return JsonResponse({'message': message}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No user found/password provided'}, status=status.HTTP_204_NO_CONTENT)

class LargeResultsSetPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000


class LeaderBoradList(generics.ListCreateAPIView):
    serializer_class    = LeaderboardSerializer
    # queryset            = CricketMatch.objects.filter(is_active = True)
    permission_classes  = (IsAuthenticatedOrReadOnly,)
    pagination_class    = LargeResultsSetPagination

    def get_queryset(self):
        return Leaderboard.objects.all().order_by('-total_score')
        # leaderboard = []
        # leaderboard_list_1 = Leaderboard.objects.filter(user = self.request.user)
        # leaderboard_list_2 = Leaderboard.objects.exclude(user = self.request.user).order_by('-total_score')
        # if leaderboard_list_1:
        #     for each in leaderboard_list_1:
        #         leaderboard.append(each)
        # if leaderboard_list_2:
        #     for each in leaderboard_list_2:
        #         leaderboard.append(each)
        # return leaderboard

@csrf_exempt
def transcoder_notification(request):
    try:
        # if request.POST:
        jobId = json.loads(json.loads(request.body)['Message'])['jobId']
        status = json.loads(json.loads(request.body)['Message'])['state']
        # f =open('maz.txt','a')
        # f.write(jobId)
        # f.write(status)
        # f.close()
        topic = Topic.objects.get(is_vb = True, is_transcoded = False, transcode_job_id = jobId)
        if status == 'COMPLETED':
            topic.is_transcoded = True
            topic.is_transcoded_error = False
        else:
            topic.is_transcoded_error = True
            topic.is_transcoded = False
        topic.update_m3u8_content()
        topic.transcode_status_dump = json.dumps(request.body)
        topic.save()
        if topic.is_transcoded:
            notify_owner = Notification.objects.create(for_user = topic.user ,topic = topic,notification_type='6',user = topic.user)
            # post_save.send(Topic, instance=topic, created=False)
            # send notification to user table for success
        else:
            pass
            # send notification to user table for error
        return JsonResponse({'post' : 'post'})
    except:
        return JsonResponse({'post' : 'post'})

@api_view(['POST'])
def vb_transcode_status(request):
    topic_id = request.POST.get('topic_id', '')
    topic = Topic.objects.get(pk=topic_id)
    if topic.is_transcoded:
        try:
            cloudfront_status = check_url(get_cloudfront_url(topic))
        except:
            cloudfront_status = '400'
        return JsonResponse({'messgae' : 'success','cloudfront_status':cloudfront_status})
    elif topic.is_transcoded_error:
        return JsonResponse({'messgae' : 'fail'})
    return JsonResponse({'messgae' : 'waiting'})

import urllib2
import re
def check_url(file_path):
    try:
        u = urllib2.urlopen(str(file_path))
        return "200"
    except Exception as e:
        # print e,file_path
        return "403"
def get_cloudfront_url(instance):
    if instance.question_video:
        regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
        find_urls_in_string = re.compile(regex, re.IGNORECASE)
        url = find_urls_in_string.search(instance.question_video)
        return str(instance.question_video.replace(str(url.group()), "https://d1fa4tg1fvr6nj.cloudfront.net"))

@csrf_exempt
@api_view(['POST'])
def SyncDump(request):
    if request.user:
        if request.method == "POST":
            #Storing the dump in database
            try:
                if request.user.id == None:
                    dump = request.POST.get('dump')
                    dump_type = request.POST.get('dump_type')
                    stored_data = UserJarvisDump(dump=dump, dump_type=dump_type, android_id=request.POST.get('android_id',''))
                    stored_data.save()
                else:
                    user = request.user
                    dump = request.POST.get('dump')
                    dump_type = request.POST.get('dump_type')
                    stored_data = UserJarvisDump(user=user, dump=dump, dump_type=dump_type, android_id=request.POST.get('android_id',''))
                    stored_data.save()
                return JsonResponse({'message': 'success'}, status=status.HTTP_200_OK)    
            except Exception as e:
                return JsonResponse({'message' : 'fail','error':str(e)})
    else:
        return JsonResponse({'messgae' : 'user_missing'})

@api_view(['POST'])
def save_android_logs(request):
    try:
        if request.user.id == None:
            AndroidLogs.objects.create(logs=request.POST.get('error_log', ''),log_type = request.POST.get('log_type',None), android_id=request.POST.get('android_id',''))
            return JsonResponse({'messgae' : 'success'})
        else:
            AndroidLogs.objects.create(user=request.user, logs=request.POST.get('error_log', ''),log_type = request.POST.get('log_type',None), android_id=request.POST.get('android_id',''))
            if request.POST.get('log_type',None)=='user_ip':
                cache_follow_post.delay(request.user.id)
                cache_popular_post.delay(request.user.id,request.user.st.language)
            return JsonResponse({'messgae' : 'success'})
    except Exception as e:
        return JsonResponse({'message' : 'fail','error':str(e)})

@api_view(['POST'])
def get_hash_list(request):
    tags = TongueTwister.objects.all()
    hashtaglist = []
    try:
        for tag in tags:
            all_videos = Topic.objects.filter(title__icontains=tag.hash_tag)
            videos = all_videos[:3]
            hash_data = TongueTwisterSerializer(tag).data
            videos_dict = []
            for video in videos:    
                videos_dict.append(TopicSerializer(video, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data)
            hash_data['videos'] = videos_dict
            hashtaglist.append(hash_data)
        return JsonResponse({'data':hashtaglist,'message':'Success'})
    except Exception as e:
        return JsonResponse({'message':'fail','error':str(e)})


def redirect_to_store(request):
    if request.GET.urlencode():
        return HttpResponseRedirect('https://play.google.com/store/apps/details?' + request.GET.urlencode())
    return HttpResponseRedirect('https://play.google.com/store/apps/details?id=com.boloindya.boloindya')



# this view is repsonsible for dumping values in already created models
#
# @api_view(['POST'])
# def user_statistics(request):
#     #user_log_fname = os.getcwd() + '/drf_spirit/user_log.json'
#     # user_data_dump = json.loads(request.body)         # loading data from body of request
#     #dump_data = models.TextField()
#     user_data_list = []                 # the list which will be returned for putting values in model

#     #with open(user_log_fname) as json_file:
#     #    user_data_dump = json.load(json_file)       # storing the data in a dict

#     all_traction_data = UserJarvisDump.objects.filter(is_executed=False)
#     # print all_traction_data
    
#     for user_jarvis in all_traction_data:

#         try:
#             user_data_string = user_jarvis.dump
#             user_data_dump = ast.literal_eval(user_data_string)

#             user_data_list = []                 # the list which will be returned for putting values in model

#             #with open(user_log_fname) as json_file:
#             #    user_data_dump = json.load(json_file)       # storing the data in a dict

#             user_id = user_data_dump['user_id']
#             user_phone_info = user_data_dump['user_phone_info']
#             user_language = len(set(user_data_dump['user_languages']))
#             user_data_list.append(user_id)
#             user_data_list.append(user_phone_info)
#             user_data_list.append(user_language)

#             #vb_viewed_count = len(set(user_data_dump['vb_viewed']))
#             #vb_commented_count = len(set(user_data_dump['vb_commented']))
#             #vb_unliked_count = len(set(user_data_dump['vb_unliked']))
#             #vb_share_count= len(set(user_data_dump['vb_share']))
#             #profile_follow_count = len(set(user_data_dump['profile_follow']))
#             #profile_unfollow_count = len(set(user_data_dump['profile_unfollow']))
#             #profile_report_count = len(set(user_data_dump['profile_report']))

#             vb_viewed = []
#             for (a,b) in user_data_dump['vb_viewed']:
#                 vb_viewed.append(a)
#             vb_viewed_count = len(set(vb_viewed))
#             user_data_list.append(vb_viewed_count)

#             vb_commented = []
#             for (a,b) in user_data_dump['vb_commented']:
#                 vb_commented.append(a)
#             vb_commented_count = len(set(vb_commented))
#             user_data_list.append(vb_commented_count)

#             vb_unliked = []
#             for (a,b) in user_data_dump['vb_unliked']:
#                 vb_unliked.append(a)
#             vb_unliked_count = len(set(vb_unliked))
#             user_data_list.append(vb_unliked_count)

#             vb_liked = []
#             for (a,b) in user_data_dump['vb_liked']:
#                 vb_liked.append(a)
#             vb_liked_count = len(set(vb_liked))
#             user_data_list.append(vb_liked_count)

#             profile_follow = []
#             for (a,b) in user_data_dump['profile_follow']:
#                 profile_follow.append(a)
#             profile_follow_count = len(set(profile_follow))
#             user_data_list.append(profile_follow_count)

#             profile_unfollow = []
#             for (a,b) in user_data_dump['profile_unfollow']:
#                 profile_unfollow.append(a)
#             profile_unfollow_count = len(set(profile_unfollow))
#             user_data_list.append(profile_unfollow_count)

#             profile_report = []
#             for (a,b) in user_data_dump['profile_report']:
#                 profile_report.append(a)
#             profile_report_count = len(set(profile_report))
#             user_data_list.append(profile_report_count)

#             vb_share = []
#             for (a,b) in user_data_dump['vb_share']:
#                 vb_share.append(a)
#             vb_share_count = len(set(vb_share))
#             user_data_list.append(vb_share_count)

#             profile_viewed_following = []    
#             for(a,b) in user_data_dump['profile_viewed_following']:
#                 profile_viewed_following.append(a)
#             profile_viewed_following_count = len(set(profile_viewed_following))
#             user_data_list.append(profile_viewed_following_count)

#             profile_viewed_followers = []
#             for (a,b) in user_data_dump['profile_viewed_followers']:
#                 profile_viewed_followers.append(a)
#             profile_viewed_followers_count = len(set(profile_viewed_followers))
#             user_data_list.append(profile_viewed_followers_count)

#             profile_visit_entry = []
#             for (a,b,c) in user_data_dump['profile_visit_entry']:
#                 profile_visit_entry.append(a)
#             profile_visit_entry_count = len(set(profile_visit_entry))
#             user_data_list.append(profile_visit_entry_count)

#             #return user_data_list           #return the list of entries in the form of list

#             #p1 = user_log_statistics()
#             #user_data_list = p1.user_statistics()               # take data from the method in the form of list
#             user_data_obj = user_log_statistics(user = user_data_list[0], user_phone_details = user_data_list[1], user_lang = user_data_list[2], num_vb_viewed = user_data_list[3],
#                 num_vb_commented = user_data_list[4], num_vb_unliked = user_data_list[5], num_vb_liked = user_data_list[6], num_profile_follow = user_data_list[7], num_profile_unfollow = user_data_list[8],
#                 num_profile_reported = user_data_list[9], num_vb_shared = user_data_list[10], num_viewed_following_list = user_data_list[11], num_entry_points = user_data_list[13]
#             )
#             user_data_obj.save()
#             print(user_data_obj)

#         except Exception as e:
#             print(str(e))

#     return JsonResponse({'message':'success'}, status=status.HTTP_201_CREATED)    


@api_view(['POST'])
def get_category_detail(request):
    try:
        category_id = request.POST.get('category_id', None)
        category = Category.objects.get(pk=category_id)
        return JsonResponse({'category_details': CategorySerializer(category).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_category_with_video_bytes(request):
    try:
        category=[]
        paginator_category = PageNumberPagination()
        paginator = PageNumberPagination()
        page_size = request.GET.get('page_size', 3)
        paginator_category.page_size = page_size
        language_id = request.GET.get('language_id', 1)
        is_discover = request.GET.get('is_discover', False)
        popular_bolo = []
        trending_videos = []
        following_user = []
        if request.user.id and not is_discover:
            userprofile = UserProfile.objects.get(user = request.user)
            category = userprofile.sub_category.all()
        else:
            category = Category.objects.filter(parent__isnull=False)

        category = paginator_category.paginate_queryset(category, request)
        if request.GET.get('popular_boloindyans'):
            if language_id:
                all_user = User.objects.filter(st__is_popular = True, st__language=language_id)
            else:
                all_user = User.objects.filter(st__is_popular = True)
            if all_user.count():
                try:
                    popular_bolo = paginator.paginate_queryset(all_user, request)
                    popular_bolo = UserSerializer(popular_bolo, many=True).data
                except Exception as e1:
                    popular_bolo = []
        if request.GET.get('is_with_popular'):
            topics = get_popular_paginated_data(request.user.id,language_id,1)
            try:
                topics = paginator.paginate_queryset(topics, request)
                trending_videos = CategoryVideoByteSerializer(topics, many=True, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data
            except Exception as e1:
                trending_videos = []
        category_details = CategoryWithVideoSerializer(category, many=True, context={'language_id': language_id,'user_id':request.user.id,'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True),'page':'0'}).data
        return JsonResponse({'category_details': category_details, 'trending_topics': trending_videos, \
            'popular_boloindyans': popular_bolo, 'following_user': following_user}, \
            status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_category_detail_with_views(request):
    try:
        category_id = request.POST.get('category_id', None)
        language_id = request.POST.get('language_id', 1)
        category = Category.objects.get(pk=category_id)
        vb_count = Topic.objects.filter(m2mcategory=category, is_removed=False, is_vb=True, language_id=language_id).count()
        all_seen = category.view_count
        current_language_view = CategoryViewCounter.objects.get(category=category,language=language_id).view_count
        return JsonResponse({'category_details': CategoryWithVideoSerializer(category, context={'language_id': language_id,'user_id':request.user.id,'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True),'page':int(request.GET.get('page','1'))}).data, 'video_count': vb_count, 'all_seen':shorcountertopic(all_seen),'current_language_view':shorcountertopic(current_language_view)}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_category_video_bytes(request):
    try:
        category_id = request.POST.get('category_id', None)
        language_id = request.POST.get('language_id', 1)
        category = Category.objects.get(pk=category_id)
        topics = []
        topics = get_redis_category_paginated_data(language_id,category.id,int(request.POST.get('page', 2)))
        paginator = Paginator(topics, settings.REST_FRAMEWORK['PAGE_SIZE'])
        topic_page = paginator.page(1)
        return JsonResponse({'topics': CategoryVideoByteSerializer(topic_page, many=True, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def old_algo_get_popular_video_bytes(request):
    """
    GET:
    """
    try:
        paginator_topics = PageNumberPagination()
        language_id = request.GET.get('language_id', 1)
        all_seen_vb = []
        post_till = datetime.now() - timedelta(days=190)
        if request.user.is_authenticated:
            all_seen_vb = get_redis_vb_seen(request.user.id)
            # all_seen_vb = VBseen.objects.filter(user = request.user, topic__language_id=language_id, topic__is_popular=True).distinct('topic_id').values_list('topic_id',flat=True)
        excluded_list =[]
        boosted_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,is_boosted=True,boosted_end_time__gte=datetime.now(),is_popular=True,date__gte = post_till).exclude(pk__in=all_seen_vb).distinct('user_id')
        if boosted_post:
            boosted_post = sorted(boosted_post, key=lambda x: x.date, reverse=True)
        for each in boosted_post:
            excluded_list.append(each.id)
        superstar_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = True,is_popular=True,date__gte = post_till).exclude(pk__in=all_seen_vb).distinct('user_id')
        if superstar_post:
            superstar_post = sorted(superstar_post, key=lambda x: x.date, reverse=True)
        for each in superstar_post:
            excluded_list.append(each.id)
        popular_user_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=True,is_popular=True,date__gte = post_till).exclude(pk__in=all_seen_vb).distinct('user_id')
        if popular_user_post:
            popular_user_post = sorted(popular_user_post, key=lambda x: x.date, reverse=True)
        for each in popular_user_post:
            excluded_list.append(each.id)
        popular_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=False,is_popular=True,date__gte = post_till).exclude(pk__in=all_seen_vb).distinct('user_id')
        if popular_post:
            popular_post = sorted(popular_post, key=lambda x: x.date, reverse=True)
        for each in popular_post:
            excluded_list.append(each.id)
        other_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,is_popular=True,date__gte = post_till).exclude(pk__in=list(all_seen_vb)+list(excluded_list))
        if other_post:
            other_post = sorted(other_post, key=lambda x: x.date, reverse=True)
        orderd_all_seen_post=[]
        all_seen_post = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=all_seen_vb, language_id=language_id, is_popular=True,date__gte = post_till)
        if all_seen_post:
            for each_id in all_seen_vb:
                for each_vb in all_seen_post:
                    if each_vb.id == each_id:
                        orderd_all_seen_post.append(each_vb)
        
        ''' Manual added post'''
        manual_added_post = Topic.objects.filter(pk=43351)
        topics=list(manual_added_post)+list(boosted_post)+list(superstar_post)+list(popular_user_post)+list(popular_post)+list(other_post)+list(orderd_all_seen_post)
        
        ''' Uncomment below line to remove manual added post'''
        # topics=list(boosted_post)+list(superstar_post)+list(popular_user_post)+list(popular_post)+list(other_post)+list(orderd_all_seen_post)
        topics = paginator_topics.paginate_queryset(topics, request)
        return JsonResponse({'topics': CategoryVideoByteSerializer(topics, many=True, context={'is_expand': request.GET.get('is_expand',True)}).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_popular_video_bytes(request):
    try:
        language_id = request.GET.get('language_id', 1)
        topics = get_popular_paginated_data(request.user.id,language_id,int(request.GET.get('page',1)))
        return JsonResponse({'topics': CategoryVideoByteSerializer(topics, many=True, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data}, status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return JsonResponse({'message': 'Error Occured:' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def pubsub_popular(request):
    try:
        paginator_topics = PageNumberPagination()
        language_id = request.GET.get('language_id', 1)
        startdate = datetime.today()
        enddate = startdate - timedelta(days=30)
        topics_all = Topic.objects.filter(is_removed=False, is_vb=True, language_id=language_id, is_popular=True, \
            date__gte=enddate).order_by('-date')
        topics = paginator_topics.paginate_queryset(topics_all, request)
        return JsonResponse({'topics': PubSubPopularSerializer(topics, many=True).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_user_follow_and_like_list(request):
    try:
        comment_like = Like.objects.filter(user = request.user,like = True,topic_id__isnull = True).values_list('comment_id', flat=True)
        topic_like = Like.objects.filter(user = request.user,like = True,comment_id__isnull = True).values_list('topic_id', flat=True)
        # all_follow = Follower.objects.filter(user_follower = request.user,is_active = True).values_list('user_following_id', flat=True)
        all_follow = get_redis_following(request.user.id)
        # all_follower = Follower.objects.filter(user_following = request.user,is_active = True).values_list('user_follower_id', flat=True)
        all_follower = get_redis_follower(request.user.id)
        notification_count = Notification.objects.filter(for_user= request.user,status=0).count()
        block_hashes = TongueTwister.objects.filter(is_blocked=True).values_list('hash_tag', flat=True)
        return JsonResponse({'comment_like':list(comment_like),'topic_like':list(topic_like),'all_follow':list(all_follow),'all_follower':list(all_follower), \
                             'notification_count':notification_count, 'user':UserSerializer(request.user).data, \
                             'block_hashes':list(block_hashes)}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_recent_videos(request):
    try:
        paginator_topics = PageNumberPagination()
        language_id = request.GET.get('language_id', 1)
        topics = []
        post_till = datetime.now() - timedelta(days=30)
        category = Category.objects.filter(parent__isnull=True).first()
        all_seen_vb = []
        if request.user.is_authenticated:
            all_seen_vb = get_redis_vb_seen(request.user.id)
            # all_seen_vb = VBseen.objects.filter(user = request.user, topic__language_id=language_id, topic__m2mcategory=category).distinct('topic_id').values_list('topic_id',flat=True)
        excluded_list =[]
        boosted_post = Topic.objects.filter(is_removed = False,is_vb = True,m2mcategory=category,language_id = language_id,is_boosted=True,boosted_end_time__gte=datetime.now(), date__gte=post_till).exclude(pk__in=all_seen_vb).distinct('user_id')
        if boosted_post:
            boosted_post = sorted(boosted_post, key=lambda x: x.date, reverse=True)
        for each in boosted_post:
            excluded_list.append(each.id)
        superstar_post = Topic.objects.filter(is_removed = False,is_vb = True,m2mcategory=category,language_id = language_id,user__st__is_superstar = True, date__gte=post_till).exclude(pk__in=all_seen_vb).distinct('user_id')
        if superstar_post:
            superstar_post = sorted(superstar_post, key=lambda x: x.date, reverse=True)
        for each in superstar_post:
            excluded_list.append(each.id)
        popular_user_post = Topic.objects.filter(is_removed = False,is_vb = True,m2mcategory=category,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=True, date__gte=post_till).exclude(pk__in=all_seen_vb).distinct('user_id')
        if popular_user_post:
            popular_user_post = sorted(popular_user_post, key=lambda x: x.date, reverse=True)
        for each in popular_user_post:
            excluded_list.append(each.id)
        popular_post = Topic.objects.filter(is_removed = False,is_vb = True,m2mcategory=category,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=False,is_popular=True, date__gte=post_till).exclude(pk__in=all_seen_vb).distinct('user_id')
        if popular_post:
            popular_post = sorted(popular_post, key=lambda x: x.date, reverse=True)
        for each in popular_post:
            excluded_list.append(each.id)
        normal_user_post = Topic.objects.filter(is_removed = False,is_vb = True,m2mcategory=category,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=False,is_popular=False, date__gte=post_till).exclude(pk__in=all_seen_vb).distinct('user_id')
        if normal_user_post:
            normal_user_post = sorted(normal_user_post, key=lambda x: x.date, reverse=True)
        for each in normal_user_post:
            excluded_list.append(each.id)
        other_post = Topic.objects.filter(is_removed = False,is_vb = True,m2mcategory=category,language_id = language_id).exclude(pk__in=list(all_seen_vb)+list(excluded_list)).order_by('-date')
        orderd_all_seen_post=[]
        all_seen_post = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=all_seen_vb, language_id=language_id, m2mcategory=category)
        if all_seen_post:
            for each_id in all_seen_vb:
                for each_vb in all_seen_post:
                    if each_vb.id == each_id:
                        orderd_all_seen_post.append(each_vb)
        topics=list(boosted_post)+list(superstar_post)+list(popular_user_post)+list(popular_post)+list(normal_user_post)+list(other_post)+list(orderd_all_seen_post)
        topics = paginator_topics.paginate_queryset(topics, request)
        return JsonResponse({'topics': CategoryVideoByteSerializer(topics, many=True, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_popular_bolo(request):
    try:
        paginator = PageNumberPagination()
        language_id = request.GET.get('language_id', 1)
        all_user = []
        if language_id:
            all_user = User.objects.filter(st__is_popular = True, st__language=language_id)
        else:
            all_user = User.objects.filter(st__is_popular = True)
        if all_user.count():
            popular_bolo = paginator.paginate_queryset(all_user, request)
            popular_bolo = UserSerializer(popular_bolo, many=True).data
            return JsonResponse({'results': popular_bolo}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'results': []}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def submit_user_feedback(request):
    try:
        contact_email = request.POST.get('contact_email', '')
        contact_number = request.POST.get('contact_mobile', '')
        description = request.POST.get('description', '')
        feedback_image = request.POST.get('feedback_image', '')
        if request.user.id:
            user_feedback = UserFeedback(by_user=request.user, description=description, contact_email=contact_email, \
                        feedback_image=feedback_image, contact_number=contact_number)
            user_feedback.save()
            user_feedback.send_feedback_email()
            return JsonResponse({'message': 'saved feedback'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'invalid user'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

def get_authorised_user_ids():
    from django.contrib.auth.models import User,Group
    from django.db.models import F,Q
    groups = list(Group.objects.all().values_list('name',flat=True))
    user_ids = list(User.objects.filter(Q(groups__name__in=groups)|Q(is_superuser=True)|Q(is_staff=True)|Q(st__social_identifier='1612763608805245')).values_list('id',flat=True))
    return list(set(user_ids))


@api_view(['POST'])
def get_auth_login_as_user_id(request):
    user_ids = get_authorised_user_ids()
    return JsonResponse({'user_ids': user_ids}, status=status.HTTP_200_OK)

@api_view(['POST'])
def generate_login_data(request):
    """
    post:
        Required Parameters
        mobile_no = request.POST.get('id', None)

    """
    auth_user_ids = get_authorised_user_ids()
    if request.user.id in auth_user_ids:
        user_id = request.POST.get('user_id', None)
        try:
            user_id = request.POST.get('user_id', None)
            userprofile = UserProfile.objects.filter(user__id = user_id,user__is_active = True)
            if userprofile:
                userprofile = userprofile[0]
                user = userprofile.user
                username = userprofile.slug
                message = 'User Logged In'
                user_tokens = get_tokens_for_user(user)

                return JsonResponse({'message': message, 'username' : username, \
                            'access_token':user_tokens['access'], 'refresh_token':user_tokens['refresh'],'user':UserSerializer(user).data}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Invalid User Id'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        JsonResponse({'message': 'Invalid Auth User Id'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def get_landing_page_video(request):
    try:
        language_id = request.POST.get('language_id', 1)
        startdate = datetime.today()
        enddate = startdate - timedelta(days=30)
        topics = Topic.objects.filter(is_removed=False, is_vb=True, language_id=language_id, is_popular=True, date__gte=enddate).order_by('-date')[0:2]
        return JsonResponse({'topics': CategoryVideoByteSerializer(topics, many=True, context={'last_updated': timestamp_to_datetime(request.GET.get('last_updated',None)),'is_expand': request.GET.get('is_expand',True)}).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['GET'])
def get_ip_to_language(request):
    try:
        user_ip = request.GET.get('user_ip',None)
        if user_ip:
            url = 'http://ip-api.com/json/'+user_ip
            response = urllib2.urlopen(url).read()
            json_response = json.loads(response)
            my_language,is_created = StateDistrictLanguage.objects.get_or_create(state_name=json_response['regionName'],district_name=json_response['city'])
            if is_created:
                if json_response['regionName'] in state_language:
                    language_option = dict(language_options)
                    for key,value in language_option.items():
                        if value==state_language[json_response['regionName']]:
                            my_language.state_language = key
                            my_language.district_language = key
                else:
                    my_language.state_language = '1'
                    my_language.district_language = '1'
                my_language.save()
            return JsonResponse({'language_id': my_language.district_language}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Error Occured: IP not in GET request',}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def set_user_email(request):
    try:
        email = request.POST.get('email',None)
        if email:
            user = request.user
            user.email = email
            user.save()
            return JsonResponse({'success': 'email saved'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def store_phone_book(request):
    try:
        phone_book = request.POST.get('phone_book',None)
        if phone_book and request.user:
            phone_book = json.loads(phone_book)
            user_phonebook, is_created = UserPhoneBook.objects.get_or_create(user=request.user)
            all_user_contact = list(user_phonebook.contact.all().values('contact_name','contact_number'))
            for each_contact in phone_book:
                temp ={'contact_name':each_contact['name'],'contact_number':validate_indian_number(each_contact['phone_no'])}
                if not temp in all_user_contact:
                    single_conatct = Contact.objects.create(contact_name=each_contact['name'],contact_number=validate_indian_number(each_contact['phone_no']))
                    user_phonebook.contact.add(single_conatct)
            sync_contacts_with_user.delay(request.user.id)
            return JsonResponse({'success': 'phonebook stored'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Error Occured: phonebook empty not User not found',}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def update_mobile_no(request):
    try:
        mobile_no = request.POST.get('mobile_no',None)
        if mobile_no:
            old_otp = SingUpOTP.objects.filter(mobile_no=validate_indian_number(mobile_no).strip(),created_at__gte=datetime.now()-timedelta(minutes=5)).order_by('-id')
            if old_otp:
                return JsonResponse({'message':'otp send'}, status=status.HTTP_200_OK)
            else:
                instance = SingUpOTP.objects.create(mobile_no=validate_indian_number(mobile_no).strip(),otp=generateOTP(6))
                response, response_status = send_sms(instance.mobile_no, instance.otp)
                if not response_status:
                    instance.is_active=False
                    instance.save()
                    return JsonResponse({'message': 'Error Occured: sms Api not working'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return JsonResponse({'message':'otp send'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Error Occured: mobile_no empty'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp_and_update_profile(request):
    try:
        mobile_no = validate_indian_number(request.POST.get('mobile_no',None))
        otp = request.POST.get('otp',None)
        otp_obj = SingUpOTP.objects.filter(mobile_no=mobile_no,otp=otp,is_active=True).order_by('-id')
        if otp_obj:
            otp_obj=otp_obj[0]
            otp_obj.is_active = False
            otp_obj.used_at = timezone.now()
            otp_obj.for_user = request.user
            otp_obj.save()
            UserProfile.objects.filter(user=request.user).update(mobile_no=mobile_no)
            userprofile=request.user.st
            add_bolo_score(request.user.id, 'mobile_no_added', userprofile)
            return JsonResponse({'message':'Mobile No updated','user':UserSerializer(request.user).data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Invalid Mobile No / OTP'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp_and_update_paytm_number(request):
    try:
        mobile_no = validate_indian_number(request.POST.get('mobile_no',None))
        otp = request.POST.get('otp',None)
        otp_obj = SingUpOTP.objects.filter(mobile_no=mobile_no,otp=otp,is_active=True).order_by('-id')
        if otp_obj:
            otp_obj=otp_obj[0]
            otp_obj.is_active = False
            otp_obj.used_at = timezone.now()
            otp_obj.for_user = request.user
            otp_obj.save()
            UserProfile.objects.filter(user=request.user).update(paytm_number=mobile_no)
            # add_bolo_score(request.user.id, 'mobile_no_added', userprofile)
            return JsonResponse({'message':'Mobile No updated','user':UserSerializer(request.user).data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Invalid Mobile No / OTP'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def userprofile_update_paytm_number(request):
    try:
        UserProfile.objects.filter(user=request.user).update(paytm_number=request.user.st.mobile_no)
        return JsonResponse({'message':'Success','user':UserSerializer(request.user).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_refer_earn_data(request):
    try:
        user_phonebook,is_created = UserPhoneBook.objects.get_or_create(user=request.user)
        invite_users = user_phonebook.contact.filter(is_user_registered=False).order_by('contact_name')
        # all_follower = get_redis_following(request.user.id)
        registerd_user = user_phonebook.contact.filter(is_user_registered=True).order_by('contact_name')#.exclude(user_id__in=all_follower)
        paginator_invite_user = PageNumberPagination()
        page_size = request.GET.get('page_size', 100)
        paginator_invite_user.page_size = page_size
        invite_users = paginator_invite_user.paginate_queryset(invite_users, request)
        invite_users_data = ContactSerializer(invite_users, many=True).data
        registerd_user_data = ContactSerializer(registerd_user, many=True).data
        try:
            user_refer_url = ReferralCode.objects.get(for_user= request.user,is_refer_earn_code=True,purpose='refer_n_earn').referral_url()
        except:
            from drf_spirit.utils import generate_refer_earn_code
            user_refer_url = ReferralCode.objects.create(for_user=request.user,code=generate_refer_earn_code(),purpose='refer_n_earn',is_refer_earn_code=True).referral_url()
        return JsonResponse({'registerd_user':registerd_user_data,'invite_user':invite_users_data,'user_refer_url':user_refer_url}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_refer_earn_url(request):
    try:
        user_refer_url = ReferralCode.objects.get(for_user= request.user,is_refer_earn_code=True,purpose='refer_n_earn').referral_url()
    except:
        from drf_spirit.utils import generate_refer_earn_code
        user_refer_url = ReferralCode.objects.create(for_user=request.user,code=generate_refer_earn_code(),purpose='refer_n_earn',is_refer_earn_code=True).referral_url()
    return JsonResponse({'user_refer_url':user_refer_url}, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_mobile_invited(request):
    try:
        user_phonebook,is_created = UserPhoneBook.objects.get_or_create(user=request.user)
        contact_id = request.POST.get('contact_id',None)
        if contact_id:
            invite_users = user_phonebook.contact.filter(pk=contact_id).update(is_invited=True,invited_on=datetime.now())
            return JsonResponse({'message':'invited'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'conatct_id not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_refer_earn_stat(request):
    try:
        page = int(request.GET.get('page',1))
        page_size = request.GET.get('page_size', settings.REST_FRAMEWORK['PAGE_SIZE'])
        try:
            referalcode = ReferralCode.objects.get(for_user=request.user,is_refer_earn_code=True,purpose='refer_n_earn')
        except MultipleObjectsReturned:
            referalcode = ReferralCode.objects.get(for_user=request.user,is_refer_earn_code=True,purpose='refer_n_earn')[0]
        except ReferralCode.DoesNotExist:
            referalcode = ReferralCode.objects.get_or_create(for_user=request.user,code=generate_refer_earn_code(),is_refer_earn_code=True,purpose='refer_n_earn')
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)
        downloaded =ReferralCodeUsed.objects.filter(code = referalcode, is_download = True, by_user__isnull = True).distinct('android_id')
        signedup = ReferralCodeUsed.objects.filter(code = referalcode, is_download = True, by_user__isnull = False).distinct('android_id')
        download_count = downloaded.count()
        signedup_count = signedup.count()
        signedup_users = list(ReferralCodeUsed.objects.filter(code = referalcode, is_download = True, by_user__isnull = False).distinct('android_id'))
        signedup_users.sort(key=lambda x: x.created_at, reverse=True)
        result_page = get_paginated_data(signedup_users, int(page_size), int(page))
        if result_page[1]<int(page):
            return JsonResponse({'message': 'No page exist'}, status=status.HTTP_400_BAD_REQUEST)
        # print result_page[1]
        return JsonResponse({'message': 'success','download_count':download_count,'signedup_count':signedup_count,'users':ReferralCodeUsedStatSerializer(result_page[0].object_list,many=True).data,'total_page':result_page[1]}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def save_banner_response(request):
    try:
        term = request.POST.get('term', None)
        response_type = request.POST.get('response_type', None)
        if term:
            bannerUser=BannerUser.objects.create(user = request.user, term=term, response_type=response_type)
            return JsonResponse({'message': 'Data Created'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'No Data'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_hash_discover(request):
    try:
        page = int(request.GET.get('page',1))
        page_size = request.GET.get('page_size', 10)
        language_id = request.GET.get('language_id','2')
        hash_tags = TongueTwisterCounter.objects.exclude(tongue_twister__is_blocked = True).filter(language_id=language_id).order_by('-tongue_twister__is_popular', 'tongue_twister__order', \
            '-tongue_twister__popular_date','-hash_counter')
        result_page = get_paginated_data(hash_tags, int(page_size), int(page))
        if result_page[1]<int(page):
            return JsonResponse({'message': 'No page exist'}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'message': 'success', 'results':TongueTwisterCounterSerializer(result_page[0].object_list,many=True).data,'total_page':result_page[1]}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_hash_discover_topics(request):
    try:
        ids = request.GET.get('ids',None)
        hash_tags = TongueTwister.objects.filter(pk__in=ids.split(','))
        return JsonResponse({'message': 'success', 'results':TongueTwisterWithOnlyVideoByteSerializer(hash_tags, context={'language_id': request.GET.get('language_id','2')}, many=True).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_m3u8_of_ids(request):
    try:
        ids = request.GET.get('ids',None)
        topics=Topic.objects.filter(pk__in=ids.split(','))
        return JsonResponse({'message': 'success', 'results':TopicsWithOnlyContent(topics, many=True).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_video_to_s3_for_app(request):
    media_file = request.FILES['media']
    if media_file:
        media_url = upload_media(media_file)
        path = default_storage.save(media_file.name, ContentFile(media_file.read()))
        with default_storage.open(media_file.name, 'wb+') as destination:
            for chunk in media_file.chunks():
                destination.write(chunk)
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        os.remove(tmp_file)
        return JsonResponse({'status': 'success','body':media_url}, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def report(request):
    try:
        if request.user.is_authenticated:
            report_type = request.POST.get('report_type', None)
            target_id = request.POST.get('target_id', None)
            target_type = request.POST.get('target_type', None) # choices 'topic','user'
            print report_type,target_type,target_id
            try:
                target_type = ContentType.objects.get(model=target_type)
            except Exception as e:
                return JsonResponse({'message': 'Target type is not topic or user','error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
            Report.objects.create(reported_by = request.user, report_type = report_type, target_type = target_type, target_id = target_id)
            return JsonResponse({'status': 'success','message':'post reported'}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({'message': 'User Unauthorised'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)





