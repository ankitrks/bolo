from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .fields import UserReadOnlyField
from forum.topic.models import Topic,CricketMatch,Poll,Choice,Voting,Leaderboard, Notification
from django.contrib.auth.models import User
from forum.category.models import Category
from forum.comment.models import Comment
from forum.user.models import UserProfile,AppVersion
from .relations import PresentableSlugRelatedField
from .models import SingUpOTP
from .utils import shortnaturaltime,shortcounterprofile,shorcountertopic
from django.conf import settings
import re

cloufront_url = "https://d1fa4tg1fvr6nj.cloudfront.net"
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AppVersionSerializer(ModelSerializer):
    class Meta:
        model = AppVersion
        fields = '__all__'

class CategoryLiteSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id','title', 'slug', 'color','hindi_title','tamil_title','telgu_title')

class TopicSerializer(ModelSerializer):
    user = SerializerMethodField()
    category = PresentableSlugRelatedField(queryset=Category.objects.all(),
                                           presentation_serializer=CategoryLiteSerializer,
                                           slug_field='slug')
    view_count = SerializerMethodField()
    comment_count = SerializerMethodField()
    date = SerializerMethodField()
    video_cdn = SerializerMethodField()

    class Meta:
        model = Topic
        fields = '__all__'
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)

    def get_user(self,instance):
        return UserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)

    def get_video_cdn(self,instance):
        if self.question_video:
            regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
            find_urls_in_string = re.compile(regex, re.IGNORECASE)
            url = find_urls_in_string.search(self.question_video)
            return str(self.question_video.replace(str(url.group()), "https://d1fa4tg1fvr6nj.cloudfront.net/"))
        else:
            return ''






class CommentSerializer(ModelSerializer):
    # user = UserReadOnlyField()
    user = SerializerMethodField()
    date = SerializerMethodField()
    class Meta:
        model = Comment
        fields = '__all__'

    def get_user(self,instance):
        return UserSerializer(instance.user).data
        
    def get_date(self,instance):
        return shortnaturaltime(instance.date)

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
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')

    class Meta:
        model = Topic
        fields = '__all__'
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)

    def get_video_comments(self,instance):
        if instance.topic_comment.filter(is_media = True, is_audio = False,is_removed = False):
            return CommentSerializer([instance.topic_comment.filter(is_media = True, is_audio = False, is_removed = False)[0]],many=True).data
        else:
            return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = False, is_removed = False),many=True).data
    def get_audio_comments(self,instance):
        if instance.topic_comment.filter(is_media = True, is_audio = True,is_removed = False):
            return CommentSerializer([instance.topic_comment.filter(is_media = True, is_audio = True, is_removed = False)[0]] ,many=True).data
        else:
            return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = True, is_removed = False) ,many=True).data
    def get_text_comments(self,instance):
        if instance.topic_comment.filter(is_media = False,is_removed = False):
            return CommentSerializer([instance.topic_comment.filter(is_media = False, is_removed = False)[0]] ,many=True).data
        else:
            return CommentSerializer(instance.topic_comment.filter(is_media = False, is_removed = False) ,many=True).data
    def get_user(self,instance):
        return UserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)
        
    def get_video_cdn(self,instance):
        if self.question_video:
            regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
            find_urls_in_string = re.compile(regex, re.IGNORECASE)
            url = find_urls_in_string.search(self.question_video)
            return str(self.question_video.replace(str(url.group()), "https://d1fa4tg1fvr6nj.cloudfront.net/"))
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
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')

    class Meta:
        model = Topic
        fields = '__all__'
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)

    def get_video_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = False, is_removed = False),many=True).data
    def get_audio_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = True, is_removed = False) ,many=True).data
    def get_text_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = False, is_removed = False) ,many=True).data
    def get_user(self,instance):
        return UserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)

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
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')

    class Meta:
        model = Topic
        fields = '__all__'
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)

    def get_video_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = False, is_removed = False,user_id = self.context['user_id']),many=True).data
    def get_audio_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = True, is_removed = False,user_id = self.context['user_id']) ,many=True).data
    def get_text_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = False, is_removed = False,user_id = self.context['user_id']) ,many=True).data
    def get_user(self,instance):
        return UserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

    def get_view_count(self,instance):
        return shorcountertopic(instance.view_count)

    def get_comment_count(self,instance):
        return shorcountertopic(instance.comment_count)

class UserProfileSerializer(ModelSerializer):
    follow_count= SerializerMethodField()
    follower_count= SerializerMethodField()
    bolo_score= SerializerMethodField()
    class Meta:
        model = UserProfile
        # fields = '__all__' 
        exclude = ('extra_data', )

    def get_follow_count(self,instance):
        return shortcounterprofile(instance.follow_count)

    def get_follower_count(self,instance):
        return shortcounterprofile(instance.follower_count)

    def get_bolo_score(self,instance):
        return shortcounterprofile(instance.bolo_score)

class UserSerializer(ModelSerializer):
    userprofile = SerializerMethodField()
    class Meta:
        model = User
        #fields = '__all__'
        exclude = ('password', )
    def get_userprofile(self,instance):
        return UserProfileSerializer(UserProfile.objects.get(user=instance)).data

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

      
