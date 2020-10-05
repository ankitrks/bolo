from rest_framework.serializers import ModelSerializer, SerializerMethodField, RelatedField, CharField

from .fields import UserReadOnlyField
from forum.topic.models import Topic,CricketMatch,Poll,Choice,Voting,Leaderboard, Notification, TongueTwister,BoloActionHistory,VBseen, TongueTwisterCounter, HashtagViewCounter
from django.contrib.auth.models import User
from forum.category.models import Category,CategoryViewCounter
from forum.comment.models import Comment
from forum.user.models import UserProfile,AppVersion, ReferralCodeUsed, VideoCompleteRate,Contact
from .relations import PresentableSlugRelatedField
from .models import SingUpOTP, Campaign, Winner, MusicAlbum
from .utils import shortnaturaltime,shortcounterprofile,shorcountertopic,get_ranked_topics
from django.conf import settings
import re
from forum.userkyc.models import UserKYC, KYCBasicInfo, KYCDocumentType, KYCDocument, AdditionalInfo, BankDetail
from forum.payment.models import PaymentCycle,EncashableDetail,PaymentInfo
from datetime import datetime,timedelta,date
from forum.topic.utils import get_redis_vb_seen,update_redis_vb_seen
from jarvis.models import PushNotificationUser, FCMDevice, Report
from forum.topic.utils import get_redis_category_paginated_data,get_redis_hashtag_paginated_data, get_redis_hashtag_paginated_data_with_json, get_campaign_paginated_data
from forum.user.utils.bolo_redis import get_userprofile_counter
import json

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
        try:
            if self.context.get("language_id"):
                language_id =  self.context.get("language_id")
                language_ids = [language_id]
                if int(language_id) in [1,2]:
                    language_ids = [1,2]
                    hash_tag_counter=HashtagViewCounter.objects.filter(hashtag = instance, language__in = language_ids)
                    hash_tag_counter_values = list(hash_tag_counter.values('video_count'))
                    video_count_values = [item['video_count'] for item in hash_tag_counter_values]
                    video_count = sum(video_count_values)
                    if any(value<999 for value in video_count_values):
                        video_count = Topic.objects.filter(first_hash_tag=instance,is_removed=False,is_vb=True, language_id__in = language_ids).count()
                    return shorcountertopic(video_count)
                else:
                    return shorcountertopic(Topic.objects.filter(hash_tags=instance,is_vb=True,is_removed=False, language_id__in = language_ids).count())
            else:
                return shorcountertopic(Topic.objects.filter(hash_tags=instance,is_vb=True,is_removed=False).count())
        except Exception as e:
            return shorcountertopic(Topic.objects.filter(hash_tags=instance,is_vb=True,is_removed=False).count())
            # raise e

    def get_total_views(self,instance):
        try:
            if self.context.get("language_id"):
                language_id =  self.context.get("language_id")
                language_ids = [language_id]
                if int(language_id) in [1,2]:
                    language_ids = [1,2]
                    hash_tag_counter=HashtagViewCounter.objects.filter(hashtag = instance, language__in = language_ids)
                    hash_tag_counter_values = list(hash_tag_counter.values('view_count', 'video_count'))
                    view_count = sum(item['view_count'] for item in hash_tag_counter_values)
                    video_count_values = [item['video_count'] for item in hash_tag_counter_values]
                    video_count = sum(video_count_values)
                    if any(value<999 for value in video_count_values):
                        all_view_count = Topic.objects.filter(first_hash_tag=instance,is_removed=False,is_vb=True, language_id__in = language_ids).aggregate(Sum('view_count'))
                        if all_view_count.has_key('view_count__sum') and all_view_count['view_count__sum']:
                            view_count = all_view_count['view_count__sum']
                    return shorcountertopic(view_count)
                else:
                    return shorcountertopic(instance.total_views)
            else:
                return shorcountertopic(instance.total_views)    
        except Exception as e:
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

        if Campaign.objects.filter(hashtag_id = instance.id):
            topics = get_campaign_paginated_data(language_id, instance.id, page)
            if int(language_id) in [1,2] and not topics:
                if int(language_id)==1:
                    topics = get_campaign_paginated_data(2, instance.id, page)
                elif int(language_id)==2:
                    topics = get_campaign_paginated_data(1, instance.id, page)
            return CategoryVideoByteSerializer(topics, many=True,context={'last_updated': self.context.get("last_updated",None),'is_expand':self.context.get("is_expand",True)}).data

        else:
            topics = get_redis_hashtag_paginated_data_with_json(language_id,instance.id,page, self.context.get("last_updated",None), self.context.get("is_expand",True))
            if int(language_id) in [1,2] and not topics:
                if int(language_id)==1:
                    topics = get_redis_hashtag_paginated_data_with_json(2,instance.id,page, self.context.get("last_updated",None), self.context.get("is_expand",True))
                elif int(language_id)==2:
                    topics = get_redis_hashtag_paginated_data_with_json(1,instance.id,page, self.context.get("last_updated",None), self.context.get("is_expand",True))
            return topics

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
    # m2mcategory = SerializerMethodField()
    backup_url = SerializerMethodField()
    likes_count = SerializerMethodField()
    whatsapp_share_count = SerializerMethodField()
    other_share_count = SerializerMethodField()
    total_share_count = SerializerMethodField()

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
        exclude = ('boosted_till','boosted_start_time','boosted_end_time','is_logo_checked','time_deleted','plag_text','vb_playtime','is_moderated','is_monetized','is_vb','is_popular','is_pubsub_popular_push','created_at','last_modified','m2mcategory','is_globally_pinned','is_closed','is_pinned','last_commented','reindex_at','is_transcoded','is_transcoded_error','transcode_dump','transcode_status_dump' )
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

    # def get_m2mcategory(self,instance):
    #     return CategoryLiteSerializer(instance.m2mcategory.all(),many=True).data

    def get_video_cdn(self,instance):
        try:
            if instance.question_video:
                cloufront_url = settings.US_CDN_URL
                if 'in-boloindya' in instance.question_video:
                    cloufront_url = settings.IN_CDN_URL
                regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
                find_urls_in_string = re.compile(regex, re.IGNORECASE)
                url = find_urls_in_string.search(instance.question_video)
                return str(instance.question_video.replace(str(url.group()), cloufront_url))
            else:
                return ''
        except:
            return instance.question_video

    def get_backup_url(self,instance):
        try:
            if instance.question_video:
                cloufront_url = settings.US_CDN_URL
                if 'in-boloindya' in instance.question_video:
                    cloufront_url = settings.IN_CDN_URL
                regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
                find_urls_in_string = re.compile(regex, re.IGNORECASE)
                url = find_urls_in_string.search(instance.question_video)
                return str(instance.question_video.replace(str(url.group()), cloufront_url))
            else:
                return instance.question_video
        except:
            return instance.question_video

    def get_likes_count(self, instance):
        return shorcountertopic(instance.likes_count)

    def get_whatsapp_share_count(self,instance):
        return shorcountertopic(instance.whatsapp_share_count)

    def get_other_share_count(self,instance):
        return shorcountertopic(instance.other_share_count + instance.linkedin_share_count + instance.facebook_share_count + instance.twitter_share_count)

    def get_total_share_count(self,instance):
        return shorcountertopic(instance.total_share_count)

class CommentSerializer(ModelSerializer):
    # user = UserReadOnlyField()
    user = SerializerMethodField()
    date = SerializerMethodField()
    gify_details = SerializerMethodField()
    class Meta:
        model = Comment
        # fields = '__all__'
        exclude = ('action', 'is_removed', 'is_modified', 'ip_address', 'is_media', 'is_audio', 'media_duration', 'thumbnail', )

    def get_user(self,instance):
        return UserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_gify_details(self,instance):
        return json.loads(instance.gify_details) if instance.gify_details else None

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
    backup_url = SerializerMethodField()
    likes_count = SerializerMethodField()
    # m2mcategory = SerializerMethodField()
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')
    whatsapp_share_count = SerializerMethodField()
    other_share_count = SerializerMethodField()
    total_share_count = SerializerMethodField()

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

    def get_likes_count(self, instance):
        return shorcountertopic(instance.likes_count)
    # def get_m2mcategory(self,instance):
    #     return CategoryLiteSerializer(instance.m2mcategory.all(),many=True).data

    def get_video_cdn(self,instance):
        try:
            if instance.question_video:
                cloufront_url = settings.US_CDN_URL
                if 'in-boloindya' in instance.question_video:
                    cloufront_url = settings.IN_CDN_URL
                regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
                find_urls_in_string = re.compile(regex, re.IGNORECASE)
                url = find_urls_in_string.search(instance.question_video)
                return str(instance.question_video.replace(str(url.group()), cloufront_url))
            else:
                return ''
        except:
            return instance.question_video

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

    def get_backup_url(self,instance):
        try:
            if instance.question_video:
                cloufront_url = settings.US_CDN_URL
                if 'in-boloindya' in instance.question_video:
                    cloufront_url = settings.IN_CDN_URL
                regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
                find_urls_in_string = re.compile(regex, re.IGNORECASE)
                url = find_urls_in_string.search(instance.question_video)
                return str(instance.question_video.replace(str(url.group()), cloufront_url))
            else:
                return instance.question_video
        except:
            return instance.question_video

    def get_whatsapp_share_count(self,instance):
        return shorcountertopic(instance.whatsapp_share_count)

    def get_other_share_count(self,instance):
        return shorcountertopic(instance.other_share_count + instance.linkedin_share_count + instance.facebook_share_count + instance.twitter_share_count)

    def get_total_share_count(self,instance):
        return shorcountertopic(instance.total_share_count)

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
    backup_url = SerializerMethodField()
    # m2mcategory = SerializerMethodField()
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')
    likes_count = SerializerMethodField()
    whatsapp_share_count = SerializerMethodField()
    other_share_count = SerializerMethodField()
    total_share_count = SerializerMethodField()

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

    def get_backup_url(self,instance):
        if instance.question_video:
            return instance.question_video
        return ''

    def get_likes_count(self, instance):
        return shorcountertopic(instance.likes_count)

    def get_whatsapp_share_count(self,instance):
        return shorcountertopic(instance.whatsapp_share_count)

    def get_other_share_count(self,instance):
        return shorcountertopic(instance.other_share_count + instance.linkedin_share_count + instance.facebook_share_count + instance.twitter_share_count)

    def get_total_share_count(self,instance):
        return shorcountertopic(instance.total_share_count)

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
    backup_url = SerializerMethodField()
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')
    likes_count = SerializerMethodField()
    whatsapp_share_count = SerializerMethodField()
    other_share_count = SerializerMethodField()
    total_share_count = SerializerMethodField()

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

    def get_backup_url(self,instance):
        if instance.question_video:
            return instance.question_video
        return ''

    def get_likes_count(self, instance):
        return shorcountertopic(instance.likes_count)

    def get_whatsapp_share_count(self,instance):
        return shorcountertopic(instance.whatsapp_share_count)

    def get_other_share_count(self,instance):
        return shorcountertopic(instance.other_share_count + instance.linkedin_share_count + instance.facebook_share_count + instance.twitter_share_count)

    def get_total_share_count(self,instance):
        return shorcountertopic(instance.total_share_count)

class UserProfileSerializer(ModelSerializer):
    follow_count= SerializerMethodField()
    follower_count= SerializerMethodField()
    bolo_score= SerializerMethodField()
    slug = SerializerMethodField()
    view_count = SerializerMethodField()
    own_vb_view_count = SerializerMethodField()
    vb_count = SerializerMethodField()

    class Meta:
        model = UserProfile
        # fields = '__all__' 
        exclude = ('social_identifier', 'question_count', 'linkedin_url', 'instagarm_id', 'twitter_id', 'topic_count', 'comment_count',\
            'refrence', 'mobile_no', 'encashable_bolo_score', 'total_time_spent', 'total_vb_playtime',\
            'is_dark_mode_enabled', 'paytm_number', 'state_name', 'city_name', 'extra_data', 'location', \
            'last_seen', 'last_ip', 'timezone', 'is_administrator', 'is_moderator', 'is_verified', 'last_post_on', \
            'last_post_hash', 'is_geo_location', 'lat', 'lang', 'click_id', 'click_id_response', 'gender', 'about', 'language', 'answer_count',\
            'share_count', 'like_count', 'is_test_user', 'is_bot_account', 'salary_range', 'boost_views_count', 'boost_like_count', \
            'boost_follow_count', 'boosted_time', 'boost_span', 'd_o_b', 'is_insight_fix')

    def get_follow_count(self,instance):
        return shortcounterprofile(get_userprofile_counter(instance.user_id)['follow_count'])

    def get_follower_count(self,instance):
        return shortcounterprofile(get_userprofile_counter(instance.user_id)['follower_count'])

    def get_bolo_score(self,instance):
        return shortcounterprofile(instance.bolo_score)

    def get_slug(self,instance):
        return instance.user.username

    def get_view_count(self,instance):
        return shorcountertopic(get_userprofile_counter(instance.user_id)['view_count'])

    def get_own_vb_view_count(self,instance):
        return shorcountertopic(get_userprofile_counter(instance.user_id)['view_count'])

    def get_vb_count(self,instance):
        return shortcounterprofile(get_userprofile_counter(instance.user_id)['video_count'])

class ShortUserProfileSerializer(ModelSerializer):
    follow_count= SerializerMethodField()
    follower_count= SerializerMethodField()
    bolo_score= SerializerMethodField()
    slug = SerializerMethodField()
    view_count = SerializerMethodField()
    own_vb_view_count = SerializerMethodField()
    vb_count = SerializerMethodField()

    class Meta:
        model = UserProfile
        # fields = '__all__' 
        exclude = ('social_identifier', 'question_count', 'linkedin_url', 'instagarm_id', 'twitter_id', 'topic_count', 'comment_count',\
            'refrence', 'mobile_no', 'encashable_bolo_score', 'total_time_spent', 'total_vb_playtime',\
            'is_dark_mode_enabled', 'paytm_number', 'state_name', 'city_name', 'extra_data', 'location', \
            'last_seen', 'last_ip', 'timezone', 'is_administrator', 'is_moderator', 'is_verified', 'last_post_on', \
            'last_post_hash', 'is_geo_location', 'lat', 'lang', 'click_id', 'click_id_response', 'gender', 'about', 'language', 'answer_count',\
            'share_count', 'like_count', 'is_test_user', 'is_bot_account', 'salary_range', 'boost_views_count', 'boost_like_count', \
            'boost_follow_count', 'boosted_time', 'boost_span', 'd_o_b', 'is_insight_fix')

    def get_follow_count(self,instance):
        return shortcounterprofile(instance.userprofile_counter['follow_count'])

    def get_follower_count(self,instance):
        return shortcounterprofile(instance.userprofile_counter['follower_count'])

    def get_bolo_score(self,instance):
        return shortcounterprofile(instance.bolo_score)

    def get_slug(self,instance):
        return instance.user.username

    def get_view_count(self,instance):
        return shorcountertopic(instance.userprofile_counter['view_count'])

    def get_own_vb_view_count(self,instance):
        return shorcountertopic(instance.userprofile_counter['view_count'])

    def get_vb_count(self,instance):
        return shortcounterprofile(instance.userprofile_counter['video_count'])

class ShortUserSerializer(ModelSerializer):
    userprofile = SerializerMethodField()
    class Meta:
        model = User
        #fields = '__all__'
        exclude = ('password', 'user_permissions', 'groups', 'date_joined', 'is_staff', 'is_superuser', 'last_login', 'email')
    def get_userprofile(self,instance):
        return ShortUserProfileSerializer(UserProfile.objects.get(user=instance)).data

class UserSerializer(ModelSerializer):
    userprofile = SerializerMethodField()
    class Meta:
        model = User
        #fields = '__all__'
        exclude = ('password', 'user_permissions', 'groups', 'date_joined', 'is_staff', 'is_superuser', 'last_login', 'email')
    def get_userprofile(self,instance):
        if instance.is_authenticated():
            return UserProfileSerializer(UserProfile.objects.get(user=instance)).data

class BasicUserSerializer(ModelSerializer):
    name = SerializerMethodField()
    profile_pic = SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'name', 'profile_pic')
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
        # fields = '__all__'
        exclude = ('social_identifier', 'question_count', 'linkedin_url', 'instagarm_id', 'twitter_id', 'topic_count', 'comment_count',\
            'refrence', 'mobile_no', 'encashable_bolo_score', 'total_time_spent', 'total_vb_playtime',\
            'is_dark_mode_enabled', 'paytm_number', 'state_name', 'city_name', 'extra_data', 'location', \
            'last_seen', 'last_ip', 'timezone', 'is_administrator', 'is_moderator', 'is_verified', 'last_post_on', \
            'last_post_hash', 'is_geo_location', 'lat', 'lang', 'click_id', 'click_id_response', 'gender', 'about', 'language', 'answer_count',\
            'share_count', 'like_count', 'is_test_user', 'is_bot_account', 'salary_range', 'boost_views_count', 'boost_like_count', \
            'boost_follow_count', 'boosted_time', 'boost_span', 'd_o_b', 'is_insight_fix')

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
        exclude = ('password', 'user_permissions', 'groups', 'date_joined', 'is_staff', 'is_superuser', 'last_login', 'email')

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

class ReportDatatableSerializer(ModelSerializer):
    reported_by = UserBaseSerializerDatatable()
    target_type = SerializerMethodField()
    video_link = SerializerMethodField()
    class Meta:
        model = Report
        fields = ('id','reported_by','report_type','target_type','video_link','target_id')

    def get_target_type(self, instance):
        return str(instance.target_type.model)

    def get_video_link(self,instance):
        if isinstance(instance.target,Topic):
            print instance.target.backup_url
            return instance.target.backup_url
        else:
            return ''

class BotUserDatatableSerializer(ModelSerializer):
    user = UserBaseSerializerDatatable()
    follower_count= SerializerMethodField()
    vb_count = SerializerMethodField()
    gender = SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'name', 'follower_count', 'follow_count', 'vb_count', 'gender')

    def get_follower_count(self,instance):
        return shortcounterprofile(get_userprofile_counter(instance.user_id)['follower_count'])

    def get_vb_count(self,instance):
        return shortcounterprofile(get_userprofile_counter(instance.user_id)['video_count'])

    def get_gender(self,instance):
        return instance.get_gender_display()

class TopicDatatableSerializer(ModelSerializer):
    user = UserBaseSerializerDatatable()
    view_count = SerializerMethodField()
    likes_count = SerializerMethodField()
    comment_count = SerializerMethodField()
    date = SerializerMethodField()

    class Meta:
        model = Topic
        fields = ('id', 'title' , 'question_video', 'question_image', 'view_count', 'likes_count', 'comment_count', 'user', 'date')

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_likes_count(self,instance):
        return shorcountertopic(instance.likes_count)

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)
   
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
    backup_url = SerializerMethodField()
    whatsapp_share_count = SerializerMethodField()
    other_share_count = SerializerMethodField()
    total_share_count = SerializerMethodField()

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
        try:
            if instance.question_video:
                cloufront_url = settings.US_CDN_URL
                if 'in-boloindya' in instance.question_video:
                    cloufront_url = settings.IN_CDN_URL
                regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
                find_urls_in_string = re.compile(regex, re.IGNORECASE)
                url = find_urls_in_string.search(instance.question_video)
                return str(instance.question_video.replace(str(url.group()), cloufront_url))
            else:
                return ''
        except:
            return instance.question_video

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

    def get_backup_url(self,instance):
        try:
            if instance.question_video:
                cloufront_url = settings.US_CDN_URL
                if 'in-boloindya' in instance.question_video:
                    cloufront_url = settings.IN_CDN_URL
                regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
                find_urls_in_string = re.compile(regex, re.IGNORECASE)
                url = find_urls_in_string.search(instance.question_video)
                return str(instance.question_video.replace(str(url.group()), cloufront_url))
            else:
                return instance.question_video
        except:
            return instance.question_video

    def get_whatsapp_share_count(self,instance):
        return shorcountertopic(instance.whatsapp_share_count)

    def get_other_share_count(self,instance):
        return shorcountertopic(instance.other_share_count + instance.linkedin_share_count + instance.facebook_share_count + instance.twitter_share_count)

    def get_total_share_count(self,instance):
        return shorcountertopic(instance.total_share_count)


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
        exclude = ('password', 'user_permissions', 'groups', 'date_joined', 'is_staff', 'is_superuser', 'last_login', 'email')

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

class TongueTwisterWithOnlyVideoByteSerializer(ModelSerializer):
    topics = SerializerMethodField()
    class Meta:
        model = TongueTwister
        fields = ('topics', 'id')

    def get_topics(self,instance):
        language_id = None
        user_id  = None
        page = 0
        if self.context.get("language_id"):
            language_id =  self.context.get("language_id")
        if self.context.get("user_id"):
            user_id =  self.context.get("user_id")
        if self.context.get("page"):
            page =  int(self.context.get("page"))
        topics = []
        all_seen_vb = []
        # filter_dict = {'hash_tags':instance}
        # if language_id:
        #     filter_dict['language_id'] = language_id
        # print filter_dict
        # topics = get_ranked_topics(user_id,page,filter_dict,{})
        # print {'hash_tags':instance,'language_id':language_id}
        if user_id:
            all_seen_vb = get_redis_vb_seen(user_id)
            # all_seen_vb = VBseen.objects.filter(user = self.request.user, topic__title__icontains=challengehash).distinct('topic_id').values_list('topic_id',flat=True)
        excluded_list =[]
        boosted_post = Topic.objects.filter(is_removed = False,is_vb = True, language_id = language_id, hash_tags=instance,is_boosted=True,boosted_end_time__gte=datetime.now()).exclude(pk__in=all_seen_vb).distinct('user_id')
        if boosted_post:
            boosted_post = sorted(boosted_post, key=lambda x: x.date, reverse=True)
        for each in boosted_post:
            excluded_list.append(each.id)
        superstar_post = Topic.objects.filter(is_removed = False,is_vb = True, language_id = language_id, hash_tags=instance,user__st__is_superstar = True).exclude(pk__in=all_seen_vb).distinct('user_id')
        if superstar_post:
            superstar_post = sorted(superstar_post, key=lambda x: x.date, reverse=True)
        for each in superstar_post:
            excluded_list.append(each.id)
        popular_user_post = Topic.objects.filter(is_removed = False,is_vb = True, language_id = language_id, hash_tags=instance,user__st__is_superstar = False,user__st__is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id')
        if popular_user_post:
            popular_user_post = sorted(popular_user_post, key=lambda x: x.date, reverse=True)
        for each in popular_user_post:
            excluded_list.append(each.id)
        popular_post = Topic.objects.filter(is_removed = False,is_vb = True, language_id = language_id, hash_tags=instance,user__st__is_superstar = False,user__st__is_popular=False,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id')
        if popular_post:
            popular_post = sorted(popular_post, key=lambda x: x.date, reverse=True)
        for each in popular_post:
            excluded_list.append(each.id)
        normal_user_post = Topic.objects.filter(is_removed = False,is_vb = True, language_id = language_id, hash_tags=instance,user__st__is_superstar = False,user__st__is_popular=False,is_popular=False).exclude(pk__in=all_seen_vb).distinct('user_id')
        if normal_user_post:
            normal_user_post = sorted(normal_user_post, key=lambda x: x.date, reverse=True)
        for each in normal_user_post:
            excluded_list.append(each.id)
        other_post = Topic.objects.filter(is_removed = False,is_vb = True, language_id = language_id, hash_tags=instance).exclude(pk__in=list(all_seen_vb)+list(excluded_list)).order_by('-date')
        orderd_all_seen_post=[]
        all_seen_post = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=all_seen_vb, hash_tags=instance)
        if all_seen_post:
            for each_id in all_seen_vb:
                for each_vb in all_seen_post:
                    if each_vb.id == each_id:
                        orderd_all_seen_post.append(each_vb)
        topics=list(boosted_post)+list(superstar_post)+list(popular_user_post)+list(popular_post)+list(normal_user_post)+list(other_post)+list(orderd_all_seen_post)
        page_size = 15
        paginator = Paginator(topics, page_size)
        page = 1
        topic_page = paginator.page(page)
        return CategoryVideoByteSerializer(topics[:settings.REST_FRAMEWORK['PAGE_SIZE']], many=True,context={'is_expand':self.context.get("is_expand",True)}).data

class TongueTwisterWithoutViewsSerializer(ModelSerializer):

    class Meta:
        model = TongueTwister
        fields = '__all__'

class TongueTwisterCounterSerializer(ModelSerializer):
    total_videos_count = SerializerMethodField()
    total_views = SerializerMethodField()
    tongue_twister = SerializerMethodField()

    class Meta:
        model = HashtagViewCounter
        fields = '__all__'

    def get_total_videos_count(self,instance):
        video_count = instance.video_count
        language_ids = [1,2]
        if int(instance.language) in language_ids:
            hash_tag_counter = HashtagViewCounter.objects.filter(hashtag=instance.hashtag, language__in=language_ids)
            hash_tag_counter_values = list(hash_tag_counter.values('video_count'))
            video_count_values = [item['video_count'] for item in hash_tag_counter_values]
            video_count = sum(video_count_values)
            if any(value<999 for value in video_count_values):
                video_count = Topic.objects.filter(first_hash_tag=instance.hashtag,is_removed=False,is_vb=True, language_id__in = language_ids).count()
        return shorcountertopic(video_count)

    def get_total_views(self,instance):
        view_count = instance.view_count
        language_ids = [1,2]
        if int(instance.language) in language_ids:
            hash_tag_counter = HashtagViewCounter.objects.filter(hashtag=instance.hashtag, language__in=language_ids)
            hash_tag_counter_values = list(hash_tag_counter.values('view_count','video_count'))
            view_count = sum(item['view_count'] for item in hash_tag_counter_values)
            video_count_values = [item['video_count'] for item in hash_tag_counter_values]
            video_count = sum(video_count_values)
            if any(value<999 for value in video_count_values):
                all_view_count = Topic.objects.filter(first_hash_tag=instance.hashtag,is_removed=False,is_vb=True, language_id__in = language_ids).aggregate(Sum('view_count'))
                if all_view_count.has_key('view_count__sum') and all_view_count['view_count__sum']:
                    view_count = all_view_count['view_count__sum']
        return shorcountertopic(view_count)

    def get_tongue_twister(self,instance):
        return TongueTwisterWithoutViewsSerializer(instance.hashtag).data 
'''
    total_videos_count = SerializerMethodField()
    total_views = SerializerMethodField()
    tongue_twister = TongueTwisterWithoutViewsSerializer()
    class Meta:
        model = TongueTwisterCounter
        fields = '__all__'

    def get_total_videos_count(self,instance):
        return shorcountertopic(instance.hash_counter)

    def get_total_views(self,instance):
        return shorcountertopic(instance.total_views)
'''

class TopicsWithOnlyContent(ModelSerializer):

    class Meta:
        model = Topic
        fields = ('m3u8_content', 'id', 'audio_m3u8_content', 'video_m3u8_content', 'question_video')

class WinnerSerializer(ModelSerializer):

    user = SerializerMethodField()

    class Meta:
        model = Winner
        fields = ('user', 'rank', 'extra_text', 'video')
    
    def get_user(self,instance):
        return UserSerializer(instance.user).data

class CampaignSerializer(ModelSerializer):

    hashtag_name = CharField(source='hashtag.hash_tag', read_only=True)
    next_campaign_name = CharField(source='next_campaign_hashtag.hash_tag', read_only=True)
    winners = WinnerSerializer(read_only=True, many=True)

    class Meta:
        model = Campaign
        fields = ('banner_img_url', 'hashtag_name', 'is_active', 'active_from', 'active_till', 'is_winner_declared', 'winners', 'next_campaign_name', 'show_popup_on_app', 'banner_img_url', 'popup_img_url', 'details')

class MusicAlbumSerializer(ModelSerializer):
  class Meta:
    model = MusicAlbum
    fields = '__all__'
