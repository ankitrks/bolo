from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .fields import UserReadOnlyField
from forum.topic.models import Topic,CricketMatch,Poll,Choice,Voting,Leaderboard, Notification, TongueTwister,BoloActionHistory,VBseen
from django.contrib.auth.models import User
from forum.category.models import Category,CategoryViewCounter
from forum.comment.models import Comment
from forum.user.models import UserProfile,AppVersion, ReferralCodeUsed, VideoCompleteRate,Contact
from .relations import PresentableSlugRelatedField
from .models import SingUpOTP
from .utils import shortnaturaltime,shortcounterprofile,shorcountertopic,get_ranked_topics
from django.conf import settings
import re
from forum.userkyc.models import UserKYC, KYCBasicInfo, KYCDocumentType, KYCDocument, AdditionalInfo, BankDetail
from forum.payment.models import PaymentCycle,EncashableDetail,PaymentInfo
from datetime import datetime,timedelta,date
from forum.topic.utils import get_redis_vb_seen,update_redis_vb_seen
from jarvis.models import PushNotificationUser, FCMDevice
from forum.topic.utils import get_redis_category_paginated_data,get_redis_hashtag_paginated_data

cloufront_url = "https://d1fa4tg1fvr6nj.cloudfront.net"
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        # fields = '__all__'
        exclude = ('reindex_at', 'is_global', 'is_closed', 'is_removed', 'is_private', 'is_engagement' )

class AppVersionSerializer(ModelSerializer):
    class Meta:
        model = AppVersion
        fields = '__all__'

class CategoryLiteSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id','title', 'slug', 'color','hindi_title','tamil_title','telgu_title')


class TongueTwisterSerializer(ModelSerializer):
    total_videos_count = SerializerMethodField()
    total_views = SerializerMethodField()
    class Meta:
        model = TongueTwister
        fields = '__all__'

    def get_total_videos_count(self,instance):
        return shorcountertopic(Topic.objects.filter(hash_tags=instance,is_vb=True,is_removed=False).count())

    def get_total_views(self,instance):
        return shorcountertopic(instance.total_views)

class TongueTwisterWithVideoByteSerializer(ModelSerializer):
    total_videos_count = SerializerMethodField()
    total_views = SerializerMethodField()
    topics = SerializerMethodField()
    class Meta:
        model = TongueTwister
        fields = '__all__'

    def get_total_videos_count(self,instance):
        return shorcountertopic(Topic.objects.filter(hash_tags=instance,is_vb=True,is_removed=False).count())

    def get_total_views(self,instance):
        return shorcountertopic(instance.total_views)

    def get_topics(self,instance):
        language_id = None
        user_id  = None
        page = 1
        if self.context.get("language_id"):
            language_id =  self.context.get("language_id")
        if self.context.get("user_id"):
            user_id =  self.context.get("user_id")
        if self.context.get("page"):
            page =  int(self.context.get("page"))
        topics = []
        all_seen_vb = []
        topics = get_redis_hashtag_paginated_data(language_id,instance.id,page)
        paginator = Paginator(topics, settings.REST_FRAMEWORK['PAGE_SIZE'])
        page = 1
        topic_page = paginator.page(page)
        return CategoryVideoByteSerializer(topics[:settings.REST_FRAMEWORK['PAGE_SIZE']], many=True,context={'last_updated':self.context.get("last_updated",None),'is_expand':self.context.get("is_expand",True)}).data



class BaseTongueTwisterSerializer(ModelSerializer):
    class Meta:
        model = TongueTwister
        fields = ('id','hash_tag')


class TopicSerializer(ModelSerializer):
    user = SerializerMethodField()
    category = PresentableSlugRelatedField(queryset=Category.objects.all(),
                                           presentation_serializer=CategoryLiteSerializer,
                                           slug_field='slug')
    view_count = SerializerMethodField()
    comment_count = SerializerMethodField()
    date = SerializerMethodField()
    video_cdn = SerializerMethodField()
    m2mcategory = SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TopicSerializer, self).__init__(*args, **kwargs)
        if not self.context['is_expand']:
            remove_list = ['m3u8_content','audio_m3u8_content','video_m3u8_content']
        else:
            remove_list = []
        if remove_list:
            for field in remove_list:
                self.fields.pop(field)

    class Meta:
        model = Topic
        #fields = '__all__'
        exclude = ('boosted_till','boosted_start_time','boosted_end_time','is_logo_checked','time_deleted','plag_text','vb_playtime','is_moderated','is_monetized','is_vb','is_popular','is_pubsub_popular_push','created_at','last_modified','m2mcategory','is_globally_pinned','is_closed','is_pinned','last_commented','reindex_at','is_transcoded','is_transcoded_error','vb_playtime','transcode_dump','transcode_status_dump' )
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)

    def get_user(self,instance):
        return ShortUserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)

    def get_m2mcategory(self,instance):
        return CategoryLiteSerializer(instance.m2mcategory.all(),many=True).data

    def get_video_cdn(self,instance):
        if instance.question_video:
            regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
            find_urls_in_string = re.compile(regex, re.IGNORECASE)
            url = find_urls_in_string.search(instance.question_video)
            return str(instance.question_video.replace(str(url.group()), "https://d1fa4tg1fvr6nj.cloudfront.net"))
        else:
            return ''

class CommentSerializer(ModelSerializer):
    # user = UserReadOnlyField()
    user = SerializerMethodField()
    date = SerializerMethodField()
    class Meta:
        model = Comment
        # fields = '__all__'
        exclude = ('action', 'is_removed', 'is_modified', 'ip_address', 'is_media', 'is_audio', 'media_duration', 'thumbnail', )

    def get_user(self,instance):
        return UserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

class PubSubPopularSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'language_id')
        
class TopicSerializerwithComment(ModelSerializer):
    user = SerializerMethodField()
    category = PresentableSlugRelatedField(queryset=Category.objects.all(),
                                           presentation_serializer=CategoryLiteSerializer,
                                           slug_field='slug')
    view_count = SerializerMethodField()
    comment_count = SerializerMethodField()
    video_comments = SerializerMethodField()
    audio_comments = SerializerMethodField()
    text_comments = SerializerMethodField()
    date = SerializerMethodField()
    video_cdn = SerializerMethodField()
    m3u8_content = SerializerMethodField()
    audio_m3u8_content = SerializerMethodField()
    video_m3u8_content = SerializerMethodField()
    # m2mcategory = SerializerMethodField()
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')

    def __init__(self, *args, **kwargs):
        super(TopicSerializerwithComment, self).__init__(*args, **kwargs)
        if not self.context['is_expand']:
            remove_list = ['m3u8_content','audio_m3u8_content','video_m3u8_content']
        else:
            remove_list = []
        # print self.context['last_updated'] , instance.date > self.context['last_updated']
        remove_list = []
        if remove_list:
            for field in remove_list:
                self.fields.pop(field)

    class Meta:
        model = Topic
        # fields = '__all__'
        exclude = ('transcode_dump', 'transcode_status_dump','boosted_till','boosted_start_time','boosted_end_time','is_logo_checked','time_deleted','plag_text','vb_playtime','is_moderated','is_monetized','is_vb','is_popular','is_pubsub_popular_push','created_at','last_modified','m2mcategory','is_globally_pinned','is_closed','is_pinned','last_commented','reindex_at','is_transcoded','is_transcoded_error')
        # TODO:: refactor after deciding about globally pinned.

    def get_video_comments(self,instance):
        return []
        # if instance.topic_comment.filter(is_media = True, is_audio = False,is_removed = False):
        #     return CommentSerializer([instance.topic_comment.filter(is_media = True, is_audio = False, is_removed = False)[0]],many=True).data
        # else:
        ## return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = False, is_removed = False),many=True).data
    def get_audio_comments(self,instance):
        return []
        # if instance.topic_comment.filter(is_media = True, is_audio = True,is_removed = False):
        #     return CommentSerializer([instance.topic_comment.filter(is_media = True, is_audio = True, is_removed = False)[0]] ,many=True).data
        # else:
        ## return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = True, is_removed = False) ,many=True).data
    def get_text_comments(self,instance):
        if instance.topic_comment.filter(is_media = False,is_removed = False).count():
            return CommentSerializer([instance.topic_comment.filter(is_media = False, is_removed = False)[0]] ,many=True).data
        return []
        # else:
        # return CommentSerializer(instance.topic_comment.filter(is_media = False, is_removed = False) ,many=True).data
    def get_user(self,instance):
        return ShortUserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)

    # def get_m2mcategory(self,instance):
    #     return CategoryLiteSerializer(instance.m2mcategory.all(),many=True).data

    def get_video_cdn(self,instance):
        if instance.question_video:
            regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
            find_urls_in_string = re.compile(regex, re.IGNORECASE)
            url = find_urls_in_string.search(instance.question_video)
            return str(instance.question_video.replace(str(url.group()), "https://d1fa4tg1fvr6nj.cloudfront.net"))
        else:
            return ''

    def get_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.m3u8_content
        else:
            return ''

    def get_audio_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.audio_m3u8_content
        else:
            return ''

    def get_video_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.video_m3u8_content
        else:
            return ''

class SingleTopicSerializerwithComment(ModelSerializer):
    user = SerializerMethodField()
    category = PresentableSlugRelatedField(queryset=Category.objects.all(),
                                           presentation_serializer=CategoryLiteSerializer,
                                           slug_field='slug')
    view_count = SerializerMethodField()
    comment_count = SerializerMethodField()
    video_comments = SerializerMethodField()
    audio_comments = SerializerMethodField()
    text_comments = SerializerMethodField()
    date = SerializerMethodField()
    m3u8_content = SerializerMethodField()
    audio_m3u8_content = SerializerMethodField()
    video_m3u8_content = SerializerMethodField()
    # m2mcategory = SerializerMethodField()
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')

    def __init__(self, *args, **kwargs):
        super(SingleTopicSerializerwithComment, self).__init__(*args, **kwargs)
        if not self.context['is_expand']:
            remove_list = ['m3u8_content','audio_m3u8_content','video_m3u8_content']
        else:
            remove_list = []
        # print self.context['last_updated'] , instance.date > self.context['last_updated']
        remove_list = []
        if remove_list:
            for field in remove_list:
                self.fields.pop(field)

    class Meta:
        model = Topic
        # fields = '__all__'
        exclude = ('transcode_dump', 'transcode_status_dump','boosted_till','boosted_start_time','boosted_end_time','is_logo_checked','time_deleted','plag_text','vb_playtime','is_moderated','is_monetized','is_vb','is_popular','is_pubsub_popular_push','created_at','last_modified','m2mcategory','is_globally_pinned','is_closed','is_pinned','last_commented','reindex_at','is_transcoded','is_transcoded_error' )
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)

    def get_video_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = False, is_removed = False),many=True).data
    def get_audio_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = True, is_removed = False) ,many=True).data
    def get_text_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = False, is_removed = False) ,many=True).data
    def get_user(self,instance):
        return ShortUserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)
        
    # def get_m2mcategory(self,instance):
    #     return CategoryLiteSerializer(instance.m2mcategory.all(),many=True).data

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)

    def get_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.m3u8_content
        else:
            return ''

    def get_audio_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.audio_m3u8_content
        else:
            return ''

    def get_video_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.video_m3u8_content
        else:
            return ''

class UserAnswerSerializerwithComment(ModelSerializer):
    user = SerializerMethodField()
    category = PresentableSlugRelatedField(queryset=Category.objects.all(),
                                           presentation_serializer=CategoryLiteSerializer,
                                           slug_field='slug')
    view_count = SerializerMethodField()
    comment_count = SerializerMethodField()
    video_comments = SerializerMethodField()
    audio_comments = SerializerMethodField()
    text_comments = SerializerMethodField()
    date = SerializerMethodField()
    m3u8_content = SerializerMethodField()
    audio_m3u8_content = SerializerMethodField()
    video_m3u8_content = SerializerMethodField()
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')

    def __init__(self, *args, **kwargs):
        super(UserAnswerSerializerwithComment, self).__init__(*args, **kwargs)
        if not self.context['is_expand']:
            remove_list = ['m3u8_content','audio_m3u8_content','video_m3u8_content']
        else:
            remove_list = []
        # print self.context['last_updated'] , instance.date > self.context['last_updated']
        remove_list = []
        if remove_list:
            for field in remove_list:
                self.fields.pop(field)

    class Meta:
        model = Topic
        # fields = '__all__'
        exclude = ('transcode_dump', 'transcode_status_dump','boosted_till','boosted_start_time','boosted_end_time','is_logo_checked','time_deleted','plag_text','vb_playtime','is_moderated','is_monetized','is_vb','is_popular','is_pubsub_popular_push','created_at','last_modified','m2mcategory','is_globally_pinned','is_closed','is_pinned','last_commented','reindex_at','is_transcoded','is_transcoded_error' )
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)

    def get_video_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = False, is_removed = False,user_id = self.context['user_id']),many=True).data
    def get_audio_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = True, is_removed = False,user_id = self.context['user_id']) ,many=True).data
    def get_text_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = False, is_removed = False,user_id = self.context['user_id']) ,many=True).data
    def get_user(self,instance):
        return ShortUserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)

    def get_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.m3u8_content
        else:
            return ''

    def get_audio_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.audio_m3u8_content
        else:
            return ''

    def get_video_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.video_m3u8_content
        else:
            return ''

class UserProfileSerializer(ModelSerializer):
    follow_count= SerializerMethodField()
    follower_count= SerializerMethodField()
    bolo_score= SerializerMethodField()
    slug = SerializerMethodField()
    view_count = SerializerMethodField()
    own_vb_view_count = SerializerMethodField()
    class Meta:
        model = UserProfile
        # fields = '__all__' 
        exclude = ('extra_data', 'location', 'last_seen', 'last_ip', 'timezone', 'is_administrator', 'is_moderator', 'is_verified', 'last_post_on', 'last_post_hash', 'is_geo_location', 'lat', 'lang', 'click_id', 'click_id_response')

    def get_follow_count(self,instance):
        return shortcounterprofile(instance.follow_count)

    def get_follower_count(self,instance):
        return shortcounterprofile(instance.follower_count)

    def get_bolo_score(self,instance):
        return shortcounterprofile(instance.bolo_score)

    def get_slug(self,instance):
        return instance.user.username

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_own_vb_view_count(self,instance):
        return shorcountertopic(instance.own_vb_view_count)

class ShortUserProfileSerializer(ModelSerializer):
    follow_count= SerializerMethodField()
    follower_count= SerializerMethodField()
    bolo_score= SerializerMethodField()
    slug = SerializerMethodField()
    view_count = SerializerMethodField()
    own_vb_view_count = SerializerMethodField()
    class Meta:
        model = UserProfile
        # fields = '__all__' 
        exclude = ('social_identifier','question_count','linkedin_url','instagarm_id','twitter_id','topic_count','comment_count','refrence','mobile_no','encashable_bolo_score','total_time_spent','total_vb_playtime','is_dark_mode_enabled','paytm_number','state_name','city_name','extra_data', 'location', 'last_seen', 'last_ip', 'timezone', 'is_administrator', 'is_moderator', 'is_verified', 'last_post_on', 'last_post_hash', 'is_geo_location', 'lat', 'lang', 'click_id', 'click_id_response','gender','about','language','answer_count','share_count','like_count','is_test_user')

    def get_follow_count(self,instance):
        return shortcounterprofile(instance.follow_count)

    def get_follower_count(self,instance):
        return shortcounterprofile(instance.follower_count)

    def get_bolo_score(self,instance):
        return shortcounterprofile(instance.bolo_score)

    def get_slug(self,instance):
        return instance.user.username

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_own_vb_view_count(self,instance):
        return shorcountertopic(instance.own_vb_view_count)

class ShortUserSerializer(ModelSerializer):
    userprofile = SerializerMethodField()
    class Meta:
        model = User
        #fields = '__all__'
        exclude = ('first_name','last_name','email','password', 'user_permissions', 'groups', 'date_joined', 'is_staff', 'is_superuser', 'last_login')
    def get_userprofile(self,instance):
        return ShortUserProfileSerializer(UserProfile.objects.get(user=instance)).data

class UserSerializer(ModelSerializer):
    userprofile = SerializerMethodField()
    class Meta:
        model = User
        #fields = '__all__'
        exclude = ('password', 'user_permissions', 'groups', 'date_joined', 'is_staff', 'is_superuser', 'last_login')
    def get_userprofile(self,instance):
        return UserProfileSerializer(UserProfile.objects.get(user=instance)).data

class BasicUserSerializer(ModelSerializer):
    name = SerializerMethodField()
    profile_pic = SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name','username','name','profile_pic')
        # exclude = ('password', 'user_permissions', 'groups', 'date_joined', 'is_staff', 'is_superuser', 'last_login')
    def get_name(self,instance):
        return instance.st.name

    def get_profile_pic(self,instance):
        return instance.st.profile_pic

class SingUpOTPSerializer(ModelSerializer):
    class Meta:
        model = SingUpOTP
        fields = ('mobile_no', )

class CricketMatchSerializer(ModelSerializer):
    prediction_start_hour= SerializerMethodField()

    def get_prediction_start_hour(self,instance):
        return settings.PREDICTION_START_HOUR
    
    class Meta:
        model = CricketMatch
        fields = '__all__'

class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class PollSerializer(ModelSerializer):
    cricketmatch = SerializerMethodField()
    class Meta:
        model = Poll
        fields = '__all__'

    def get_cricketmatch(self,instance):
        return CricketMatchSerializer(instance.cricketmatch).data

class PollSerializerwithChoice(ModelSerializer):
    cricketmatch = SerializerMethodField()
    choices = SerializerMethodField()
    class Meta:
        model = Poll
        fields = '__all__'

    def get_cricketmatch(self,instance):
        return CricketMatchSerializer(instance.cricketmatch).data

    def get_choices(self,instance):
        choices = Choice.objects.filter(poll = instance,is_active = True)
        return OnlyChoiceSerializer(choices, many = True).data

class OnlyChoiceSerializer(ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'

class ChoiceSerializer(ModelSerializer):
    poll = SerializerMethodField()
    class Meta:
        model = Choice
        fields = '__all__'

    def get_poll(self,instance):
        return PollSerializer(instance.poll).data

class VotingSerializer(ModelSerializer):
    cricketmatch = SerializerMethodField()
    poll = SerializerMethodField()
    choice = SerializerMethodField()
    user = SerializerMethodField()
    class Meta:
        model = Voting
        fields = '__all__'


    def get_poll(self,instance):
        return PollSerializer(instance.poll).data

    def get_cricketmatch(self,instance):
        return CricketMatchSerializer(instance.cricketmatch).data

    def get_choice(self,instance):
        return ChoiceSerializer(instance.choice).data

    def get_user(self,instance):
        return UserSerializer(instance.user).data


class LeaderboardSerializer(ModelSerializer):
    user = SerializerMethodField()
    class Meta:
        model = Leaderboard
        fields = '__all__'


    def get_user(self,instance):
        return UserSerializer(instance.user).data 

class KYCDocumnetsTypeSerializer(ModelSerializer):
    class Meta:
        model = KYCDocumentType
        fields = '__all__'

class UserKYCSerializer(ModelSerializer):
    class Meta:
        model = UserKYC
        fields = '__all__'

class BoloActionHistorySerializer(ModelSerializer):
    class Meta:
        model = BoloActionHistory
        fields = '__all__'

class PaymentCycleSerializer(ModelSerializer):
    class Meta:
        model = PaymentCycle
        fields = '__all__'

class EncashableDetailSerializer(ModelSerializer):
    class Meta:
        model = EncashableDetail
        fields = '__all__'

class PaymentInfoSerializer(ModelSerializer):
    class Meta:
        model = PaymentInfo
        fields = '__all__'

class UserWithUserSerializer(ModelSerializer):
    user = SerializerMethodField()
    sub_category = SerializerMethodField()
    view_count = SerializerMethodField()
    own_vb_view_count = SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_user(self,instance):
        return UserWithoutUserProfileSerializer(instance.user).data
    
    def get_sub_category(self,instance):
        return CategorySerializer(instance.sub_category, many=True).data

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_own_vb_view_count(self,instance):
        return shorcountertopic(instance.own_vb_view_count)

class UserWithoutUserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        #fields = '__all__'
        exclude = ('password', )

class UserBaseSerializerDatatable(ModelSerializer):
    class Meta:
        model = User
        fields = ('username','id')
        # exclude = ('password', )

class UserPayDatatableSerializer(ModelSerializer):
    user = UserBaseSerializerDatatable()
    class Meta:
        model = UserProfile
        fields = ('user','name','bolo_score','id')
   
class CategoryVideoByteSerializer(ModelSerializer):
    user = SerializerMethodField()
    view_count = SerializerMethodField()
    likes_count = SerializerMethodField()
    comment_count = SerializerMethodField()
    date = SerializerMethodField()
    video_cdn = SerializerMethodField()
    m3u8_content = SerializerMethodField()
    audio_m3u8_content = SerializerMethodField()
    video_m3u8_content = SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CategoryVideoByteSerializer, self).__init__(*args, **kwargs)
        if not self.context['is_expand']:
            remove_list = ['m3u8_content','audio_m3u8_content','video_m3u8_content']
        else:
            remove_list = []
        remove_list= []
        if remove_list:
            for field in remove_list:
                self.fields.pop(field)

    class Meta:
        model = Topic
        #fields = '__all__'
        exclude = ('transcode_dump','transcode_status_dump', 'is_transcoded_error', 'transcode_job_id', 'is_transcoded', 'is_removed', 'is_closed', 'is_globally_pinned', 'is_pinned', 'last_commented', 'reindex_at', 'last_active' )
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)

    def get_user(self,instance):
        return ShortUserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_likes_count(self,instance):
        return shorcountertopic(instance.likes_count)

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)

    def get_video_cdn(self,instance):
        if instance.question_video:
            regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
            find_urls_in_string = re.compile(regex, re.IGNORECASE)
            url = find_urls_in_string.search(instance.question_video)
            return str(instance.question_video.replace(str(url.group()), "https://d1fa4tg1fvr6nj.cloudfront.net"))
        else:
            return ''

    def get_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.m3u8_content
        else:
            return ''

    def get_audio_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.audio_m3u8_content
        else:
            return ''

    def get_video_m3u8_content(self,instance):
        if self.context['last_updated'] and instance.date > self.context['last_updated']:
            return instance.video_m3u8_content
        else:
            return ''


from django.core.paginator import Paginator
from django.db.models import Sum

class CategoryWithVideoSerializer(ModelSerializer):
    topics = SerializerMethodField()
    total_view = SerializerMethodField()
    current_language_view = SerializerMethodField()

    class Meta:
        model = Category
        # fields = '__all__'
        exclude = ('reindex_at', 'is_global', 'is_closed', 'is_removed', 'is_private', )

    def get_total_view(self, instance):
        return shorcountertopic(instance.view_count)

    def get_current_language_view(self,instance):
        if self.context.get("language_id"):
            language =  self.context.get("language_id")
            current_language_category = CategoryViewCounter.objects.get(category=instance,language=language)
            return shorcountertopic(current_language_category.view_count)


    def get_topics(self,instance):
        # return []
        language_id = 1
        user_id  = None
        page = 1
        if self.context.get("language_id"):
            language_id =  self.context.get("language_id")
        if self.context.get("user_id"):
            user_id =  self.context.get("user_id")
        if self.context.get("page"):
            page =  int(self.context.get("page"))
        topics = []
        all_seen_vb = []
        topics = get_redis_category_paginated_data(language_id,instance.id,page)
        return CategoryVideoByteSerializer(topics[:settings.REST_FRAMEWORK['PAGE_SIZE']], many=True,context={'last_updated':self.context.get("last_updated",None),'is_expand':self.context.get("is_expand",True)}).data

class VideoCompleteRateSerializer(ModelSerializer):
    class Meta:
        model = VideoCompleteRate
        fields = ('videoid','user', 'playtime', 'percentage_viewed')

# searializer for serach _notification
class CategoryWithTitleSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('title', 'id',)

class UserWithNameSerializer(ModelSerializer):
    user_name = SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('name', 'user', 'user_name',)

    def get_user_name(self,instance):
        return instance.user.username

class TongueTwisterWithHashSerializer(ModelSerializer):
    class Meta:
        model = TongueTwister
        fields = ('hash_tag', 'id')

class TongueWithTitleSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = ('title', 'id')

class UserOnlySerializer(ModelSerializer):
    class Meta:
        model = User
        #fields = '__all__'
        exclude = ('password', 'user_permissions', 'groups', 'date_joined', 'is_staff', 'is_superuser', 'last_login')

class FCMDeviceSerializer(ModelSerializer):

    class Meta:
        model = FCMDevice
        fields = '__all__'

class PushNotificationUserSerializer(ModelSerializer):
    user = SerializerMethodField()
    device = FCMDeviceSerializer()

    class Meta:
        model = PushNotificationUser
        fields = '__all__'

    def get_user(self,instance):
        return UserOnlySerializer(instance.user).data

class ContactSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Contact
        fields = '__all__'

    def get_user(self,instance):
        return UserSerializer(instance.user).data

class ReferralCodeUsedStatSerializer(ModelSerializer):
    user = SerializerMethodField()
    date_joined = SerializerMethodField()

    class Meta:
        model = ReferralCodeUsed
        fields = ('user', 'date_joined')

    def get_user(self,instance):
        return UserSerializer(instance.by_user).data

    def get_date_joined(self,instance):
        return instance.by_user.date_joined.strftime("%d-%m-%Y %H:%M:%S")

