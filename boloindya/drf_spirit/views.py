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

from .filters import TopicFilter, CommentFilter
from .models import SingUpOTP
from .permissions import IsOwnerOrReadOnly
from .serializers import TopicSerializer, CategorySerializer, CommentSerializer, SingUpOTPSerializer,TopicSerializerwithComment,UserSerializer
from forum.topic.models import Topic,ShareTopic,Like,SocialShare
from forum.category.models import Category
from forum.comment.models import Comment
from forum.user.models import UserProfile,Follower
from django.db.models import F,Q
from rest_framework_simplejwt.tokens import RefreshToken
import json
from .utils import get_weight,add_bolo_score

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

    def get_queryset(self):
        topics              = []
        is_user_timeline    = False
        search_term         =self.request.GET.keys()
        if search_term:
            filter_dic      ={}
            post            = []
            for term_key in search_term:
                if term_key:
                    value               =self.request.GET.get(term_key)
                    filter_dic[term_key]=value
                    if term_key =='user_id':
                        is_user_timeline = True
            if filter_dic:
                topics = Topic.objects.filter(**filter_dic)
                if is_user_timeline:
                    all_shared_post = ShareTopic.objects.filter(user_id = filter_dic['user_id'])
                    if all_shared_post:
                        for each_post in all_shared_post:
                            post.append(each_post)
                    if topics:
                        for each_post in topics:
                            post.append(each_post)
                    topics = post
        else:
                topics = Topic.objects.all()
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

    Required Parameters:
    user_id and topic_id and comment_html

    """

    user_id      = request.user.id
    topic_id     = request.POST.get('topic_id', '')
    language_id  = request.POST.get('language_id', '')
    comment_html = request.POST.get('comment', '')
    mobile_no    = request.POST.get('mobile_no', '')
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
    topic.question_audio = request.POST.get('question_audio')

    Required Parameters:
    title and category_id 

    """

    topic        = Topic()
    user_id      = request.user.id
    title        = request.POST.get('title', '')
    language_id  = request.POST.get('language_id', '')
    category_id  = request.POST.get('category_id', '')

    if title:
        topic.title          = title.upper()
    if request.POST.get('question_audio'):
        topic.question_audio = request.POST.get('question_audio')
    if request.POST.get('question_video'):
        topic.question_audio = request.POST.get('question_video')


    if title and category_id:
        try:

            topic.language_id   = language_id
            topic.category_id   = category_id
            topic.user_id       = user_id
            topic.save()
            add_bolo_score(request.user.id,'create_topic')
            return JsonResponse({'message': 'Topic Created'}, status=status.HTTP_201_CREATED)
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
    queryset            = Comment.objects.filter()
    permission_classes  = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        topic_slug = self.kwargs['slug']
        return self.queryset.filter(topic__slug=topic_slug)

class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_engagement = False)
    # permission_classes = (IsAuthenticated,)
    permission_classes  = (AllowAny,)

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
    get:
        Required Parameters
        request.GET.get('is_reset_password')
        request.GET.get('is_for_change_phone')
    """

    def perform_create(self, serializer):
        instance        = serializer.save()
        instance.otp    = generateOTP(6)
        response, response_status   = send_sms(instance.mobile_no, instance.otp)
        instance.api_response_dump  = response
        if self.request.GET.get('is_reset_password') and self.request.GET.get('is_reset_password') == '1':
            instance.is_reset_password = True
        if self.request.GET.get('is_for_change_phone') and self.request.GET.get('is_for_change_phone') == '1':
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
    get:
        Required Parameters
        mobile_no = request.POST.get('mobile_no', None)
        otp = request.POST.get('otp', None)
        request.GET.get('is_reset_password')
        request.GET.get('is_for_change_phone')
    """
    mobile_no = request.POST.get('mobile_no', None)
    otp = request.POST.get('otp', None)
    exclude_is_reset_password = True # inverted because of exclude
    is_for_change_phone = False
    if request.GET.get('is_reset_password') and request.GET.get('is_reset_password') == '1':
        exclude_is_reset_password = False # inverted because of exclude
    if request.GET.get('is_for_change_phone') and request.GET.get('is_for_change_phone') == '1':
        is_for_change_phone = True

    if mobile_no and otp:
        try:
            exclude_dict = {'is_active' : False, 'is_reset_password' : exclude_is_reset_password}
            if is_for_change_phone:
                exclude_dict = {'is_active' : False, 'is_for_change_phone' : is_for_change_phone}
            otp_obj = SingUpOTP.objects.exclude(**exclude_dict).get(mobile_no=mobile_no, otp=otp)
            otp_obj.is_active = False
            otp_obj.used_at = timezone.now()
            if exclude_is_reset_password:
                user = User.objects.create(username = mobile_no)
                add_bolo_score(user.id,'initial_signup')
                otp_obj.for_user = user
                otp_obj.save()
                user_tokens = get_tokens_for_user(user)
                return JsonResponse({'message': 'User created', 'username' : mobile_no,'access':user_tokens['access'],'refresh':user_tokens['refresh']}, status=status.HTTP_200_OK)
            otp_obj.save()
            return JsonResponse({'message': 'OTP Validated', 'username' : mobile_no}, status=status.HTTP_200_OK)
        except Exception as e:
            print e
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
    
    if username and password:
        try:
            user = request.user
            user.set_password( password )
            return JsonResponse({'message': 'Password updated!', 'username' : username}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid username'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No username / password provided'}, status=status.HTTP_204_NO_CONTENT)


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
    if extra_data:
        extra_data = json.loads(extra_data)
    try:
        if activity == 'facebook_login' and refrence == 'facebook':
            try:
                userprofile,is_created = UserProfile.objects.get_or_create(social_identifier = extra_data['id'])
                user=userprofile.user
            except:
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
                user.save()
                user_tokens = get_tokens_for_user(user)
                return JsonResponse({'message': 'User created', 'username' : user.username,'access':user_tokens['access'],'refresh':user_tokens['refresh']}, status=status.HTTP_200_OK)
            else:
                user_tokens = get_tokens_for_user(user)
                return JsonResponse({'message': 'User Logged In', 'username' :user.username ,'access':user_tokens['access'],'refresh':user_tokens['refresh']}, status=status.HTTP_200_OK)
        elif activity == 'profile_save':
            try:
                userprofile = UserProfile.objects.get(user = request.user)
                userprofile.bio = bio
                userprofile.about = about
                userprofile.profile_pic =profile_pic
                if username:
                    user = userprofile.user
                    user.username = username
                    user.save()
                userprofile.save()
                return JsonResponse({'message': 'Profile Saved'}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'message': 'Error Occured:'+str(e)+''}, status=status.HTTP_400_BAD_REQUEST)
        elif activity == 'settings_changed':
            try:
                userprofile = UserProfile.objects.get(user = request.user)
                if sub_category_prefrences:
                    for each_sub_category in sub_category_prefrences:
                        userprofile.sub_category_id = each_sub_category
                        userprofile.save()
                if language:
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
                return JsonResponse({'message': 'Unfollowed'}, status=status.HTTP_200_OK)
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
            if each_sub_category.id == user_sub_category_id:
                each_sub_category.remove()
                return JsonResponse({'message': 'Unfollowed'}, status=status.HTTP_200_OK)
            else:
                userprofile.sub_category_id = user_sub_category_id
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
    userprofile = UserProfile.objects.get(user = request.user)
    try:
        liked,is_created = Like.objects.get_or_create(topic_id = topic_id,user = request.user)
        if is_created:
            add_bolo_score(request.user.id,'liked')
            userprofile.like_count = F('like_count')+1
            userprofile.save()
            return JsonResponse({'message': 'liked'}, status=status.HTTP_200_OK)
        else:
            liked.like = False
            liked.save()
            userprofile.like_count = F('like_count')-1
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
        share_on = request.POST.get('share_on',None)
    """
    topic_id = request.POST.get('topic_id',None)
    share_on = request.POST.get('share_on',None)
    userprofile = UserProfile.objects.get(user = request.user)
    if share_on == 'share_timeline':
        try:
            liked = ShareTopic.objects.create(topic_id = topic_id,user = request.user)
            add_bolo_score(request.user.id,'share_timeline')
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)
    elif share_on == 'facebook_share':
        try:
            liked = SocialShare.objects.create(topic_id = topic_id,user = request.user,share_type = '0')
            add_bolo_score(request.user.id,'facebook_share')
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'fb shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)
    elif share_on == 'whatsapp_share':
        try:
            liked = SocialShare.objects.create(topic_id = topic_id,user = request.user,share_type = '1')
            add_bolo_score(request.user.id,'whatsapp_share')
            userprofile.share_count = F('share_count')+1
            userprofile.save()
            return JsonResponse({'message': 'whatsapp shared'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# def 












