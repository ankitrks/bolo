from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .fields import UserReadOnlyField
from forum.topic.models import Topic
from django.contrib.auth.models import User
from forum.category.models import Category
from forum.comment.models import Comment
from forum.user.models import UserProfile
from .relations import PresentableSlugRelatedField
from .models import SingUpOTP
from .utils import shortnaturaltime

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryLiteSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id','title', 'slug', 'color')

class TopicSerializer(ModelSerializer):
    user = UserReadOnlyField()
    category = PresentableSlugRelatedField(queryset=Category.objects.all(),
                                           presentation_serializer=CategoryLiteSerializer,
                                           slug_field='slug')

    class Meta:
        model = Topic
        fields = '__all__'
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)



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
        if instance.topic_comment.filter(is_media = True, is_audio = False):
            return CommentSerializer([instance.topic_comment.filter(is_media = True, is_audio = False)[0]],many=True).data
        else:
            return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = False),many=True).data
    def get_audio_comments(self,instance):
        if instance.topic_comment.filter(is_media = True, is_audio = True):
            return CommentSerializer([instance.topic_comment.filter(is_media = True, is_audio = True)[0]] ,many=True).data
        else:
            return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = True) ,many=True).data
    def get_text_comments(self,instance):
        if instance.topic_comment.filter(is_media = False):
            return CommentSerializer([instance.topic_comment.filter(is_media = False)[0]] ,many=True).data
        else:
            return CommentSerializer(instance.topic_comment.filter(is_media = False) ,many=True).data
    def get_user(self,instance):
        return UserSerializer(instance.user).data

    def get_date(self,instance):
        return shortnaturaltime(instance.date)

class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        # fields = '__all__' 
        exclude = ('extra_data', )

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

      
