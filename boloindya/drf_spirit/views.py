 # -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.base import ContentFile
from rest_framework.generics import GenericAPIView


from .filters import TopicFilter, CommentFilter
from .models import SingUpOTP
from .permissions import IsOwnerOrReadOnly
from .serializers import TopicSerializer, CategorySerializer, CommentSerializer, SingUpOTPSerializer,TopicSerializerwithComment,AppVersionSerializer,UserSerializer,SingleTopicSerializerwithComment,\
UserAnswerSerializerwithComment,CricketMatchSerializer,PollSerializer,ChoiceSerializer,VotingSerializer,LeaderboardSerializer,\
PollSerializerwithChoice, OnlyChoiceSerializer, NotificationSerializer, UserProfileSerializer
from forum.topic.models import Topic,ShareTopic,Like,SocialShare,FCMDevice,Notification,CricketMatch,Poll,Choice,Voting,Leaderboard,VBseen,TongueTwister
from forum.category.models import Category
from forum.comment.models import Comment
from forum.user.models import UserProfile,Follower,AppVersion
from django.db.models import F,Q
from rest_framework_simplejwt.tokens import RefreshToken
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, imencode
import boto3
import time
import random
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime,timedelta,date
import json
from .utils import get_weight,add_bolo_score,shorcountertopic
from django.db.models import Sum
import itertools
import json
import urllib2

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class NotificationAPI(GenericAPIView):
    permissions_classes = (IsOwnerOrReadOnly,)
    serializer_class   = NotificationSerializer

    limit = 10

    def post(self, request, action, format = None):
        # print "request user", request.user, action

        if action == 'get':
            notifications = self.get_notifications(request.user.id)
            notification_data = self.serialize_notification(notifications)
            return JsonResponse(notification_data, safe=False)

        elif action == 'click':
            self.mark_notification_as_read()
            return JsonResponse({
                    'status': "SUCCESS"
                })

    def get_notifications(self, user_id):
        user_id = self.request.user.id
        # last_read = get_redis(redis_keymap%(user_id))
        # notifications = Notification.get_notification(self.request.user, count = 100)

        offset = self.request.data.get('offset') or 0
        limit = self.request.data.get('limit') or self.limit

        # print "offset",offset,"page_size",page_size

        notifications = Notification.objects.filter(for_user = self.request.user, is_active = True).order_by('-last_modified')[offset:offset+limit]

        
        Notification.objects.filter(status = 0).update(status = 1)

        result = []
        for notification in notifications:
            result.append(notification)
        return result


    def serialize_notification(self, notifications):
        serialized_data =[]
        for each_noti in notifications:
            serialized_data.append(each_noti.get_notification_json())
        return serialized_data

    
    def mark_notification_as_read(self):
        notification = Notification.objects.get(id = self.request.data.get("id"))
        notification.status = 2
        notification.save()


class TopicList(generics.ListCreateAPIView):
    serializer_class    = TopicSerializer
    filter_backends     = (DjangoFilterBackend,)
    filter_class        = TopicFilter
    permission_classes  = (IsAuthenticatedOrReadOnly,)
    

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
                print filter_dic

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
                    all_follower = Follower.objects.filter(user_follower = self.request.user).values_list('user_following_id',flat=True)
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
            all_follower = Follower.objects.filter(user_follower = self.request.user).values_list('user_following_id',flat=True)
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

class VBList(generics.ListCreateAPIView):
    serializer_class   = TopicSerializerwithComment
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class   = LimitOffsetPagination


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


    def get_queryset(self):
        topics              = []
        is_user_timeline    = False
        search_term         =self.request.GET.keys()
        filter_dic      ={}
        sort_recent= False
        category__slug = False
        m2mcategory__slug = False
        if search_term:
            for term_key in search_term:
                if term_key not in ['limit','offset','order_by']:
                    # if term_key =='category':
                    #     filter_dic['category__slug'] = self.request.GET.get(term_key)
                    if term_key:
                        value = self.request.GET.get(term_key)
                        filter_dic[term_key]=value
                        if term_key =='user_id':
                            is_user_timeline = True
                        if term_key =='category':
                            m2mcategory__slug = self.request.GET.get(term_key)
            filter_dic['is_vb'] = True
            if 'order_by' in search_term:
                sort_recent = True

            if filter_dic:
                print filter_dic

                if is_user_timeline:
                    filter_dic['is_removed'] = False
                    topics = Topic.objects.filter(**filter_dic)
                    post = topics
                    topics=sorted(itertools.chain(post),key=lambda x: x.date, reverse=True)
                else:
                    topics = []
                    all_seen_vb = VBseen.objects.filter(user = self.request.user).values_list('topic_id',flat=True)
                    # if 'language_id' in search_term:

                        # post1 = Topic.objects.filter(Q(user_id__in=all_follower)|Q(category_id__in = category_follow),language_id = self.request.GET.get('language_id'),is_removed = False,date__gte=enddate)
                    if m2mcategory__slug:
                        post1 = Topic.objects.filter(is_removed = False,is_vb = True,m2mcategory__slug=m2mcategory__slug,language_id = self.request.GET.get('language_id')).exclude(id__in=all_seen_vb).order_by('-date')
                        post2 = Topic.objects.filter(id__in=all_seen_vb,is_removed = False,is_vb = True,m2mcategory__slug=m2mcategory__slug,language_id = self.request.GET.get('language_id')).order_by('-date')
                    else:
                        post1 = Topic.objects.filter(is_removed = False,is_vb = True,language_id = self.request.GET.get('language_id')).exclude(id__in=all_seen_vb).order_by('-id')
                        post2 = Topic.objects.filter(id__in=all_seen_vb,is_removed = False,is_vb = True,language_id = self.request.GET.get('language_id')).order_by('-id')
                    if post1:
                        topics+=list(post1)
                    if post2:
                        topics+=list(post2)
                    # else:
                    #     topics = Topic.objects.filter(is_removed = False,is_vb = True).order_by('-id')
        else:
            topics = Topic.objects.filter(is_removed = False,is_vb = True).order_by('-id')
        return topics

from random import shuffle

from rest_framework.response import Response
from collections import OrderedDict

class ShufflePagination(LimitOffsetPagination):

    def get_paginated_response(self, data):
        shuffle(data)
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))



class GetChallenge(generics.ListCreateAPIView):
    serializer_class = TopicSerializerwithComment
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = ShufflePagination

    def get_queryset(self):
        all_topic = Topic.objects.filter(title__icontains = '#GameOfTongues',is_removed=False)
        return all_topic

        

@api_view(['POST'])
def GetChallengeDetails(request):
    """
    post:
    user_id = request.POST.get('user_id', '')
    """ 
    try:
        all_vb = Topic.objects.filter(title__icontains = '#GameOfTongues',is_removed=False)
        vb_count = all_vb.count()
        all_seen = all_vb.aggregate(Sum('view_count'))
        tongue = TongueTwister.objects.get(hash_tag__icontains='#GameOfTongues')
        return JsonResponse({'message': 'success','vb_count':vb_count,'en_tongue_descp':tongue.en_descpription,'hi_tongue_descp':tongue.hi_descpription,'ta_tongue_descp':tongue.ta_descpription,'te_tongue_descp':tongue.te_descpription,'all_seen':shorcountertopic(all_seen['view_count__sum'])}, status=status.HTTP_200_OK)
    except:
        return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)


class GetTopic(generics.ListCreateAPIView):
    serializer_class   = SingleTopicSerializerwithComment
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class    = LimitOffsetPagination
    """
    post:
    topic_id =self.request.POST.get('topic_id','')
    """ 

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

    def get_queryset(self):
        topics      = []
        search_term = self.request.GET.get('term')
        if search_term:
            topics  = Topic.objects.filter(title__icontains = search_term,is_removed = False,is_vb=True)

        return topics


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
            print user
        user_json = UserSerializer(user).data
        return JsonResponse({'message': 'success','result':user_json}, status=status.HTTP_200_OK)
    except:
        return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)

    # def get_queryset(self):
    #     user_id = self.request.POST.get('user_id','')
    #     if user_id:
    #         user = User.objects.get(id=user_id)

    #     return [user]

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
            print name_list
            user_ids = UserProfile.objects.filter(reduce(lambda x, y: x | y, [Q(name__icontains=word) for word in name_list])).values_list('user_id',flat=True)
            print user_ids
            users = User.objects.filter(Q(username__icontains = search_term)|Q(reduce(lambda x, y: x | y, [Q(username__icontains=word) \
                for word in name_list]))|Q(first_name__icontains = search_term)|Q(last_name__icontains = search_term)|Q(id__in = user_ids)).order_by('-st__question_count')
        return users


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
        print virtual_thumb_file
        url_thumbnail= upload_thumbail(virtual_thumb_file)
        print url_thumbnail
        # obj.thumbnail = url_thumbnail
        # obj.media_duration = media_duration
        # obj.save()
        return url_thumbnail
    else:
        return False

from moviepy.editor import VideoFileClip
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
        client = boto3.client('s3',aws_access_key_id = settings.AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY)
        ts = time.time()
        created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        final_filename = "img-" + str(ts).replace(".", "")  + ".jpg" 
        client.put_object(Bucket=settings.AWS_BUCKET_NAME, Key='thumbnail/' + final_filename, Body=virtual_thumb_file)
        # client.resource('s3').Object(settings.AWS_BUCKET_NAME, 'thumbnail/' + final_filename).put(Body=open(virtual_thumb_file, 'rb'))
        filepath = "https://s3.amazonaws.com/"+settings.AWS_BUCKET_NAME+"/thumbnail/"+final_filename
        # if os.path.exists(file):
        #     os.remove(file)
        return filepath
    except:
        return None

def upload_media(media_file):
    try:
        client = boto3.client('s3',aws_access_key_id = settings.AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY)
        ts = time.time()
        created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        filenameNext= str(media_file.name).split('.')
        final_filename = str(filenameNext[0])+"_"+ str(ts).replace(".", "")+"."+str(filenameNext[1])
        client.put_object(Bucket=settings.AWS_BUCKET_NAME, Key='media/' + final_filename, Body=media_file)
        filepath = "https://s3.amazonaws.com/"+settings.AWS_BUCKET_NAME+"/media/"+final_filename
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
    x = 'BI'+year+month+''.join(random.choice(string.digits) for _ in range(4))
    # x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    try:
        user = User.objects.get(username=x)
        get_random_username()
    except:
        return x


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
    language_id  = request.POST.get('language_id', '')
    comment_html = request.POST.get('comment', '')
    mobile_no    = request.POST.get('mobile_no', '')
    thumbnail = request.POST.get('thumbnail', '')
    media_duration = request.POST.get('media_duration', '')
    comment      = Comment()

    if request.POST.get('is_media'):
        comment.is_media = request.POST.get('is_media')
    if request.POST.get('is_audio'):
        comment.is_audio = request.POST.get('is_audio')

    if user_id and topic_id and comment_html:
        try:

            comment.comment       = comment_html
            comment.comment_html  = comment_html
            comment.language_id   = language_id
            comment.user_id       = user_id
            comment.topic_id      = topic_id
            comment.mobile_no     = mobile_no
            comment.save()
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
            add_bolo_score(request.user.id,'reply_on_topic')
            return JsonResponse({'message': 'Reply Submitted','comment':CommentSerializer(comment).data}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'Topic Id / User Id / Comment provided'}, status=status.HTTP_204_NO_CONTENT)

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

    if comment.user == request.user:
        try:
            comment.delete()
            return JsonResponse({'message': 'Comment Deleted'}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'Invalid Delete Request'}, status=status.HTTP_204_NO_CONTENT)

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

    topic        = Topic()
    user_id      = request.user.id
    title        = request.POST.get('title', '')
    language_id  = request.POST.get('language_id', '')
    category_id  = request.POST.get('category_id', '')
    media_duration  = request.POST.get('media_duration', '')
    question_image  = request.POST.get('question_image', '')
    is_vb = request.POST.get('is_vb',False)
    # media_file = request.FILES.get['media']
    # print media_file

    if title:
        topic.title          = title[0].upper()+title[1:]
    if request.POST.get('question_audio'):
        topic.question_audio = request.POST.get('question_audio')
    if request.POST.get('question_video'):
        topic.question_video = request.POST.get('question_video')
    if request.POST.get('question_image'):
        topic.question_image = request.POST.get('question_image')



    try:

        topic.language_id   = language_id
        topic.category_id   = category_id
        topic.user_id       = user_id
        if is_vb:
            topic.is_vb = True
            topic.media_duration = media_duration
            topic.question_image = question_image
            topic.view_count = random.randint(1,49)
            topic.update_vb()
        else:
            topic.view_count = random.randint(10,30)
        topic.save()
        topic.m2mcategory.add(Category.objects.get(pk=category_id))
        if not is_vb:
            userprofile = UserProfile.objects.get(user = request.user)
            userprofile.question_count = F('question_count')+1
            userprofile.save()
            add_bolo_score(request.user.id,'create_topic')
            topic_json = TopicSerializerwithComment(topic).data
            message = 'Topic Created'
        else:
            userprofile = UserProfile.objects.get(user = request.user)
            userprofile.question_count = F('vb_count')+1
            userprofile.save()
            add_bolo_score(request.user.id,'create_vb')
            topic_json = TopicSerializerwithComment(topic).data
            message = 'Video Byte Created'
        return JsonResponse({'message': message,'topic':topic_json}, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)

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
        title        = request.POST.get('title', '')
        category_id  = request.POST.get('category_id', '')
        language_id  = request.POST.get('language_id', '')
        topic        = Topic.objects.get(pk = topic_id)

        if topic.user == request.user:

            if title:
                topic.title = title[0].upper()+title[1:]
            if category_id:
                topic.category_id = category_id
            if language_id:
                topic.language_id = language_id
            topic.save()

            topic_json = TopicSerializerwithComment(topic).data
            return JsonResponse({'message': 'Topic Edited','topic':topic_json}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({'message': 'Invalid Edit Request'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return JsonResponse({'message': 'Invalid Edit Request'}, status=status.HTTP_400_BAD_REQUEST)

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
    print topic.user, request.user

    if topic.user == request.user:
        try:
            topic.delete()
            return JsonResponse({'message': 'Topic Deleted'}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'Invalid Delete Request'}, status=status.HTTP_204_NO_CONTENT)

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
        topic_json = TopicSerializerwithComment(topic).data
        print topic_json
        return JsonResponse({'result':[topic_json]}, status=status.HTTP_201_CREATED)   
    except:
        return JsonResponse({'message': 'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)

                
class TopicDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class    = TopicSerializer
    queryset            = Topic.objects.all()
    permission_classes  = (IsOwnerOrReadOnly,)
    lookup_field        = 'slug'

class TopicCommentList(generics.ListAPIView):
    serializer_class    = CommentSerializer
    queryset            = Comment.objects.all()
    permission_classes  = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        topic_slug = self.kwargs['slug']
        topic_id = self.kwargs['topic_id']
        return self.queryset.filter(topic_id=topic_id,is_removed = False)

class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_engagement = False).exclude(parent__isnull = False)
    pagination_class=None
    # permission_classes = (IsAuthenticated,)
    permission_classes  = (AllowAny,)

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
        instance        = serializer.save()
        instance.otp    = generateOTP(6)
        response, response_status   = send_sms(instance.mobile_no, instance.otp)
        instance.api_response_dump  = response
        if self.request.POST.get('is_reset_password') and self.request.POST.get('is_reset_password') == '1':
            instance.is_reset_password = True
        if self.request.POST.get('is_for_change_phone') and self.request.POST.get('is_for_change_phone') == '1':
            instance.is_for_change_phone = True
        if not response_status:
            instance.is_active = False
        instance.save()
        if not response_status:
            return JsonResponse({'message': 'OTP could not be sent'}, status=status.HTTP_417_EXPECTATION_FAILED)
        return JsonResponse({'message': 'OTP sent'}, status=status.HTTP_200_OK)

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
    mobile_no = request.POST.get('mobile_no', None)
    language = request.POST.get('language',None)
    otp = request.POST.get('otp', None)
    is_geo_location = request.POST.get('is_geo_location',None)
    lat = request.POST.get('lat',None)
    lang = request.POST.get('lang',None)
    click_id = request.POST.get('click_id',None)
    is_reset_password = False
    is_for_change_phone = False
    all_category_follow = []
    if request.POST.get('is_reset_password') and request.POST.get('is_reset_password') == '1':
        is_reset_password = True # inverted because of exclude
    if request.POST.get('is_for_change_phone') and request.POST.get('is_for_change_phone') == '1':
        is_for_change_phone = True

    if mobile_no and otp:
        try:
            exclude_dict = {'is_active' : True, 'is_reset_password' : is_reset_password,"mobile_no":mobile_no, "otp":otp}
            if is_for_change_phone:
                exclude_dict = {'is_active' : True, 'is_for_change_phone' : is_for_change_phone,"mobile_no":mobile_no, "otp":otp}

            otp_obj = SingUpOTP.objects.filter(**exclude_dict).order_by('-id')
            if otp_obj:
                otp_obj=otp_obj[0]
            otp_obj.is_active = False
            otp_obj.used_at = timezone.now()
            if not is_reset_password and not is_for_change_phone:
                userprofile = UserProfile.objects.filter(mobile_no = mobile_no)
                if userprofile:
                    userprofile = userprofile[0]
                    user = userprofile.user
                    message = 'User Logged In'
                else:
                    user = User.objects.create(username = get_random_username())
                    message = 'User created'
                    userprofile = UserProfile.objects.get(user = user)
                    userprofile.mobile_no = mobile_no
                    if str(is_geo_location) =="1":
                        userprofile.lat = lat
                        userprofile.lang = lang
                    if click_id:
                        userprofile.click_id = click_id
                        click_url = 'http://res.taskbucks.com/postback/res_careeranna/dAppCheck?Ad_network_transaction_id='+str(click_id)+'&eventname=register'
                        response = urllib2.urlopen(click_url).read()
                        userprofile.click_id_response = str(response)
                    userprofile.save()
                    # if str(language):
                    #     default_follow = deafult_boloindya_follow(user,str(language))
                    add_bolo_score(user.id, 'initial_signup')
                user_tokens = get_tokens_for_user(user)
                otp_obj.for_user = user
                otp_obj.save()
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
    name            = request.POST.get('name',None)
    bio             = request.POST.get('bio',None)
    about           = request.POST.get('about',None)
    username        = request.POST.get('username',None)
    refrence        = request.POST.get('refrence',None)
    extra_data      = request.POST.get('extra_data',None)
    activity        = request.POST.get('activity',None)
    language        = request.POST.get('language',None)
    is_geo_location = request.POST.get('is_geo_location',None)
    d_o_b = request.POST.get('d_o_b',None)
    gender = request.POST.get('gender',None)
    click_id = request.POST.get('click_id',None)
    lat = request.POST.get('lat',None)
    lang = request.POST.get('lang',None)
    sub_category_prefrences = request.POST.get('categories',None)
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
            except Exception as e:
                print e
                user_exists,num_user = check_user(extra_data['first_name'],extra_data['last_name'])
                username = generate_username(extra_data['first_name'],extra_data['last_name'],num_user) if user_exists else str(str(extra_data['first_name'])+str(extra_data['last_name']))
                user = User.objects.create(username = username.lower())
                userprofile = UserProfile.objects.get(user = user)
                is_created = True

            if is_created:
                add_bolo_score(user.id,'initial_signup')
                user.first_name = extra_data['first_name']
                user.last_name = extra_data['last_name']
                userprofile.name = extra_data['name']
                userprofile.social_identifier = extra_data['id']
                userprofile.bio = bio
                userprofile.d_o_b = d_o_b
                userprofile.gender = gender
                userprofile.about = about
                userprofile.refrence = refrence
                userprofile.extra_data = extra_data
                userprofile.user = user
                userprofile.bolo_score += 95
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
                # if str(language):
                #     default_follow = deafult_boloindya_follow(user,str(language))
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
                userprofile.d_o_b = d_o_b
                userprofile.gender = gender
                userprofile.profile_pic =profile_pic
                userprofile.save()
                if username:
                    check_username = User.objects.filter(username = username).exclude(pk =request.user.id)
                    if not check_username:
                        user = userprofile.user
                        user.username = username
                        user.save()
                    else:
                        return JsonResponse({'message': 'Username already exist'}, status=status.HTTP_200_OK)
                return JsonResponse({'message': 'Profile Saved'}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)
        elif activity == 'settings_changed':
            try:
                userprofile = UserProfile.objects.get(user = request.user)
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
                    # default_follow = deafult_boloindya_follow(request.user,str(language))
                    userprofile.language = str(language)
                    userprofile.save()
                return JsonResponse({'message': 'Settings Chnaged'}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

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
            add_bolo_score(request.user.id,'follow')
            add_bolo_score(user_following_id,'followed')
            userprofile.follow_count = F('follow_count')+1
            userprofile.save()
            followed_user.follower_count = F('follower_count')+1
            followed_user.save()
            return JsonResponse({'message': 'Followed'}, status=status.HTTP_200_OK)
        else:
            if follow.is_active:
                follow.is_active = False
                follow.save()
                userprofile.follow_count = F('follow_count')-1
                followed_user.follower_count = F('follower_count')-1
                userprofile.save()
                followed_user.save()
                return JsonResponse({'message': 'Unfollowed'}, status=status.HTTP_200_OK)
            else:
                follow.is_active = True
                userprofile.follow_count = F('follow_count')+1
                followed_user.follower_count = F('follower_count')+1
                follow.save()
                followed_user.save()
                userprofile.save()
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
            acted_obj.save()
            add_bolo_score(request.user.id,'liked')
            userprofile.like_count = F('like_count')+1
            userprofile.save()
            return JsonResponse({'message': 'liked'}, status=status.HTTP_200_OK)
        else:
            if liked.like:
                liked.like = False
                liked.save()
                acted_obj.likes_count = F('likes_count')-1
                acted_obj.save()
                userprofile.like_count = F('like_count')-1
                userprofile.save()
                return JsonResponse({'message': 'unliked'}, status=status.HTTP_200_OK)
            else:
                liked.like = True
                liked.save()
                acted_obj.likes_count = F('likes_count')+1
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
        comment_id = request.POST.get('comment_id',None)
        share_on = request.POST.get('share_on',None)
    """
    topic_id = request.POST.get('topic_id',None)
    comment_id = request.POST.get('comment_id',None)
    share_on = request.POST.get('share_on',None)
    userprofile = UserProfile.objects.get(user = request.user)
    if share_on == 'share_timeline':
        try:
            liked = ShareTopic.objects.create(topic_id = topic_id,comment_id = comment_id,user = request.user)
            add_bolo_score(request.user.id,'share_timeline')
            if comment_id:
                comment = Comment.objects.get(pk = comment_id)
                comment.share_count = F('share_count')+1
                comment.save()
                topic = comment.topic
            else:
                topic = Topic.objects.get(pk = topic_id)
                topic.share_count = F('share_count')+1
            topic.total_share_count = F('total_share_count')+1
            topic.save()
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)
    elif share_on == 'facebook_share':
        try:
            liked = SocialShare.objects.create(topic_id = topic_id,comment_id = comment_id,user = request.user,share_type = '0')
            if comment_id:
                comment = Comment.objects.get(pk = comment_id)
                comment.share_count = F('share_count')+1
                comment.save()
                topic= comment.topic
            else:
                topic = Topic.objects.get(pk = topic_id)
                topic.share_count = F('share_count')+1    
            topic.total_share_count = F('total_share_count')+1
            topic.save()
            add_bolo_score(request.user.id,'facebook_share')
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'fb shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)
    elif share_on == 'whatsapp_share':
        try:
            liked = SocialShare.objects.create(topic_id = topic_id,comment_id = comment_id,user = request.user,share_type = '1')
            if comment_id:
                comment = Comment.objects.get(pk = comment_id)
                comment.share_count = F('share_count')+1
                comment.save()
                topic = comment.topic
            else:
                topic = Topic.objects.get(pk = topic_id)
                topic.share_count = F('share_count')+1
            topic.total_share_count = F('total_share_count')+1
            topic.save()
            add_bolo_score(request.user.id,'whatsapp_share')
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'whatsapp shared'}, status=status.HTTP_200_OK)
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
        topic.save()
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
        topic.save()
        vbseen,is_created = VBseen.objects.get_or_create(user = request.user,topic_id = topic_id)
        return JsonResponse({'message': 'vb seen'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def follow_like_list(request):
    try:
        comment_like = Like.objects.filter(user = request.user,like = True,topic_id__isnull = True).values_list('comment_id', flat=True)
        topic_like = Like.objects.filter(user = request.user,like = True,comment_id__isnull = True).values_list('topic_id', flat=True)
        all_follow = Follower.objects.filter(user_follower = request.user,is_active = True).values_list('user_following_id', flat=True)
        userprofile = UserProfile.objects.get(user = request.user)
        all_category_follow = userprofile.sub_category.all().values_list('id', flat=True)
        detialed_category = userprofile.sub_category.all()
        app_version = AppVersion.objects.get(app_name = 'android')
        app_version = AppVersionSerializer(app_version).data
        notification_count = Notification.objects.filter(for_user= request.user,status=0).count()
        return JsonResponse({'comment_like':list(comment_like),'topic_like':list(topic_like),'all_follow':list(all_follow),\
            'all_category_follow':list(all_category_follow),'app_version':app_version,\
            'notification_count':notification_count, 'is_test_user':userprofile.is_test_user,'user':UserSerializer(request.user).data,\
            'detialed_category':CategorySerializer(detialed_category,many = True).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_follow_user(request):
    try:
        all_follow_id = Follower.objects.filter(user_follower = request.user,is_active = True).values_list('user_following_id', flat=True)
        all_vb_of_follower = Topic.objects.filter(is_vb=True,is_removed=False,user_id__in=all_follow_id).values_list('user_id',flat=True)
        if all_vb_of_follower:
            all_user = User.objects.filter(pk__in = all_vb_of_follower)
            return JsonResponse({'all_follow':UserSerializer(all_user,many= True).data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'all_follow':[]}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_following_list(request):
    try:
        all_following_id = Follower.objects.filter(user_following = request.POST.get('user_id', ''),is_active = True).values_list('user_follower_id', flat=True)
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
        all_follower_id = Follower.objects.filter(user_follower = request.POST.get('user_id', ''),is_active = True).values_list('user_following_id', flat=True)
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
            bolo_indya_user = User.objects.get(username = 'boloindya_hi')
        elif language == '3':
            bolo_indya_user = User.objects.get(username = 'boloindya_ta')
        elif language == '4':
            bolo_indya_user = User.objects.get(username = 'boloindya_te')
        else:
            bolo_indya_user = User.objects.get(username = 'boloindya_en')
        follow,is_created = Follower.objects.get_or_create(user_follower = user,user_following=bolo_indya_user)
        if is_created:
            add_bolo_score(user.id,'follow')
            userprofile = UserProfile.objects.get(user = user)
            bolo_indya_profile = UserProfile.objects.get(user = bolo_indya_user)
            userprofile.follow_count = F('follow_count') + 1
            userprofile.save()
            bolo_indya_profile.follower_count = F('follower_count') + 1
            bolo_indya_profile.save()
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
from django.db.models.signals import post_save
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def transcoder_notification(request):
    # if request.POST:
    jobId = json.loads(json.loads(request.body)['Message'])['jobId']
    status = json.loads(json.loads(request.body)['Message'])['state']
    # f =open('maz.txt','a')
    # f.write(jobId)
    # f.write(status)
    # f.close()
    if status == 'COMPLETED':
        topic = Topic.objects.get(is_vb = True, is_transcoded = False, transcode_job_id = jobId)
        topic.is_transcoded = True
    else:
        topic.is_transcoded_error = True
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
        print e,file_path
        return "403"
def get_cloudfront_url(instance):
    if instance.question_video:
        regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
        find_urls_in_string = re.compile(regex, re.IGNORECASE)
        url = find_urls_in_string.search(instance.question_video)
        return str(instance.question_video.replace(str(url.group()), "https://d1fa4tg1fvr6nj.cloudfront.net"))






