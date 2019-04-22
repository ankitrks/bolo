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
from .serializers import TopicSerializer, CategorySerializer, CommentSerializer, SingUpOTPSerializer
from forum.topic.models import Topic
from forum.category.models import Category
from forum.comment.models import Comment
from forum.user.models import UserProfile,Follower

from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class TopicList(generics.ListCreateAPIView):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = TopicFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TopicDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    lookup_field = 'slug'

class TopicCommentList(generics.ListAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.filter()
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        topic_slug = self.kwargs['slug']
        return self.queryset.filter(topic__slug=topic_slug)

class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

class CommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = CommentFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    lookup_field = 'id'

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
    sms_url = 'https://2factor.in/API/V1/' + settings.TWO_FACTOR_SMS_API_KEY +  '/SMS/' +  phone_number +\
             '/' + otp + '/' + settings.TWO_FACTOR_SMS_TEMPLATE
    response = urllib2.urlopen(sms_url).read()
    json_response = json.loads( response )
    if json_response.has_key('Status') and json_response['Status'] == 'Success':
        return response, True
    return response, False

class SingUpOTPView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SingUpOTPSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.otp = generateOTP(6)
        response, response_status = send_sms(instance.mobile_no, instance.otp)
        instance.api_response_dump = response
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
    password = request.POST.get('password', '')
    username = request.POST.get('username', '')
    if username and password:
        try:
            user = User.objects.get(username = username)
            user.set_password( password )
            return JsonResponse({'message': 'Password updated!', 'username' : username}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid username'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No username / password provided'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def fb_profile_settings(request):
    profile_pic = request.POST.get('profile_pic',None)
    name = request.POST.get('name',None)
    bio = request.POST.get('bio',None)
    about = request.POST.get('about',None)
    username = request.POST.get('username',None)
    refrence = request.POST.get('refrence',None)
    extra_data = request.POST.get('extra_data',None)
    activity = request.POST.get('activity',None)
    language = request.POST.get('language',None)
    sub_category_prefrences = request.POST.get('categories',None)
    try:
        if activity == 'facebook_login' and refrence == 'facebook':
            userprofile,is_created = UserProfile.objects.get_or_create(social_identifier = extra_data['id'])
            if is_created:
                user = User.objects.create(username = extra_data['id'])
                user.first_name = extra_data['first_name']
                user.last_name = extra_data['last_name']
                userprofile.name = extra_data['name']
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
                user = userprofile.user
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
    user_following_id = request.POST.get('user_following_id',None)
    try:
        follow,is_created = Follower.objects.get_or_create(user_follower = request.user,user_following_id=user_following_id)
        if is_created:
            return JsonResponse({'message': 'Followed'}, status=status.HTTP_200_OK)
        else:
            if follow.is_active:
                follow.is_active = False
                follow.save()
                return JsonResponse({'message': 'Unfollowed'}, status=status.HTTP_200_OK)
            else:
                follow.is_active = True
                follow.save()
                return JsonResponse({'message': 'Unfollowed'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error Occured:'+str(e)+'',}, status=status.HTTP_400_BAD_REQUEST)












