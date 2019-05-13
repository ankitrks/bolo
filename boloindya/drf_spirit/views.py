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


from .filters import TopicFilter, CommentFilter
from .models import SingUpOTP
from .permissions import IsOwnerOrReadOnly
from .serializers import TopicSerializer, CategorySerializer, CommentSerializer, SingUpOTPSerializer,TopicSerializerwithComment,AppVersionSerializer,UserSerializer
from forum.topic.models import Topic,ShareTopic,Like,SocialShare
from forum.category.models import Category
from forum.comment.models import Comment
from forum.user.models import UserProfile,Follower,AppVersion
from django.db.models import F,Q
from rest_framework_simplejwt.tokens import RefreshToken
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, imencode
import boto3
import time
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime
import json
from .utils import get_weight,add_bolo_score
import itertools

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

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
                topics              = Topic.objects.filter(**filter_dic)
                pagination_class    = LimitOffsetPagination
        else:
                topics              = Topic.objects.all()
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
        if search_term:
            post            = []
            for term_key in search_term:
                if term_key not in ['limit','offset']:
                    if term_key =='category':
                        filter_dic['category__slug'] = self.request.GET.get(term_key)
                    elif term_key:
                        value               =self.request.GET.get(term_key)
                        filter_dic[term_key]=value
                        if term_key =='user_id':
                            is_user_timeline = True
            if filter_dic:
                if is_user_timeline:
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
                else:
                    all_follower = Follower.objects.filter(user_follower = self.request.user).values_list('user_following_id',flat=True)
                    category_follow = UserProfile.objects.get(user= self.request.user).sub_category.all().values_list('id',flat = True)
                    if 'language_id' in search_term and 'category' in search_term:
                        topics = Topic.objects.filter(Q(user_id__in=all_follower)|Q(category_id__in = category_follow),language_id = self.request.GET.get('language_id'),category__slug =self.request.GET.get('category'))
                    elif 'language_id' in search_term:
                        topics = Topic.objects.filter(Q(user_id__in=all_follower)|Q(category_id__in = category_follow),language_id = self.request.GET.get('language_id'))
                    elif 'category' in search_term:
                        topics = Topic.objects.filter(Q(user_id__in=all_follower)|Q(category_id__in = category_follow),category__slug =self.request.GET.get('category'))
                    else:
                        topics = Topic.objects.filter(Q(user_id__in=all_follower)|Q(category_id__in = category_follow))
                    post = topics
            topics=sorted(itertools.chain(post),key=lambda x: x.date, reverse=True)
        else:
            all_follower = Follower.objects.filter(user_follower = self.request.user).values_list('user_following_id',flat=True)
            category_follow = UserProfile.objects.get(user= self.request.user).sub_category.all().values_list('id',flat = True)
            topics = Topic.objects.filter(Q(user_id__in=all_follower)|Q(category_id__in = category_follow))
        return topics;


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
            topics  = Topic.objects.filter(title__icontains = search_term)

        return topics;

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
            users   = User.objects.filter(Q(username__icontains = search_term)|Q(first_name__icontains = search_term))

        return users;


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
    print clip.duration 
    return clip.duration

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
            return JsonResponse({'message': 'Reply Submitted'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'Topic Id / User Id / Comment provided'}, status=status.HTTP_204_NO_CONTENT)

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



    if title and category_id:
        try:

            topic.language_id   = language_id
            topic.category_id   = category_id
            topic.user_id       = user_id
            topic.save()
            userprofile = UserProfile.objects.get(user = request.user)
            userprofile.question_count = F('question_count')+1
            userprofile.save()
            add_bolo_score(request.user.id,'create_topic')
            topic_json = TopicSerializerwithComment(topic).data
            return JsonResponse({'message': 'Topic Created','topic':topic_json}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'Topic Id / User Id / Comment provided'}, status=status.HTTP_204_NO_CONTENT)

                
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
        return self.queryset.filter(topic_id=topic_id)

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
                    user = User.objects.create(username = mobile_no)
                    message = 'User created'
                    userprofile = UserProfile.objects.get(user = user)
                    userprofile.mobile_no = mobile_no
                    userprofile.save()
                    if language:
                        default_follow = deafult_boloindya_follow(user.id,str(language))
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

        return [user];

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

                user = User.objects.create(username = extra_data['id'])
                userprofile = UserProfile.objects.get(user = user)
                is_created = True

            if is_created:
                add_bolo_score(user.id,'initial_signup')
                user.first_name = extra_data['first_name']
                user.last_name = extra_data['last_name']
                userprofile.name = extra_data['name']
                userprofile.social_identifier = extra_data['id']
                userprofile.bio = bio
                userprofile.about = about
                userprofile.refrence = refrence
                userprofile.extra_data = extra_data
                userprofile.user = user
                userprofile.save()
                if language:
                    default_follow = deafult_boloindya_follow(user.id,str(language))
                    userprofile.language = str(language)
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
                userprofile.profile_pic =profile_pic
                userprofile.save()
                if username:
                    check_username = User.objects.filter(username = username).exclude(pk =request.user.id)
                    if not check_username:
                        user = userprofile.user
                        user.username = username
                        user.save()
                    else:
                        return JsonResponse({'message': 'Username already exist'}, status=status.HTTP_400_BAD_REQUEST)
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
                    default_follow = deafult_boloindya_follow(request.user,str(language))
                    userprofile.language = str(language)
                    userprofile.save()
                return JsonResponse({'message': 'Settings Chnaged'}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

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
    comment_id = request.POST.get('comment_id',None)
    userprofile = UserProfile.objects.get(user = request.user)
    try:
        liked,is_created = Like.objects.get_or_create(comment_id = comment_id,user = request.user)
        comment = Comment.objects.get(pk = comment_id)
        if is_created:
            comment.likes_count = F('likes_count')+1
            comment.save()
            add_bolo_score(request.user.id,'liked')
            userprofile.like_count = F('like_count')+1
            userprofile.save()
            return JsonResponse({'message': 'liked'}, status=status.HTTP_200_OK)
        else:
            if liked.like:
                liked.like = False
                liked.save()
                comment.likes_count = F('likes_count')-1
                comment.save()
                userprofile.like_count = F('like_count')-1
                userprofile.save()
            else:
                liked.like = True
                liked.save()
                comment.likes_count = F('likes_count')+1
                comment.save()
                userprofile.like_count = F('like_count')+1
                userprofile.save()
            return JsonResponse({'message': 'unliked'}, status=status.HTTP_200_OK)
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
    comment_ids = request.GET.get('comment_ids',None)
    """
    get:
        Required Parameters
        comment_ids = request.GET.get('comment_ids',None)
    """
    #### add models for seen users
    try:
        comment_list = comment_ids.split(',')
        for each_comment_id in comment_list:
            comment = Comment.objects.get(pk = each_comment_id)
            topic= comment.topic
            topic.view_count = F('view_count') +1
            topic.save()
            return JsonResponse({'message': 'item viewed'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def follow_like_list(request):
    try:
        all_like = Like.objects.filter(user = request.user,like = True).values_list('comment_id', flat=True)
        all_follow = Follower.objects.filter(user_follower = request.user,is_active = True).values_list('user_following_id', flat=True)
        userprofile = UserProfile.objects.get(user = request.user)
        all_category_follow = userprofile.sub_category.all().values_list('id', flat=True)
        app_version = AppVersion.objects.get(app_name = 'android')
        app_version = AppVersionSerializer(app_version).data
        return JsonResponse({'all_like':list(all_like),'all_follow':list(all_follow),'all_category_follow':list(all_category_follow),'app_version':app_version}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)



def deafult_boloindya_follow(user,language):
    # try:
    if language == '1':
        bolo_indya_user = User.objects.get(username = 'boloindya_hi')
    elif language == '2':
        bolo_indya_user = User.objects.get(username = 'boloindya_ta')
    elif language == '3':
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
    #     return True
    # except:
    #     return False









