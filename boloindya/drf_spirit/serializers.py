from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .fields import UserReadOnlyField
from forum.topic.models import Topic
from forum.category.models import Category
from forum.comment.models import Comment
from .relations import PresentableSlugRelatedField
from .models import SingUpOTP

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryLiteSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('title', 'slug', 'color')

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
    user = UserReadOnlyField()
    class Meta:
        model = Comment
        fields = '__all__'

class TopicSerializerwithComment(ModelSerializer):
    user = UserReadOnlyField()
    category = PresentableSlugRelatedField(queryset=Category.objects.all(),
                                           presentation_serializer=CategoryLiteSerializer,
                                           slug_field='slug')
    video_comments = SerializerMethodField()
    audio_comments = SerializerMethodField()
    text_comments = SerializerMethodField()
    # comments = PresentableSlugRelatedField(queryset=Comment.objects.all(),presentation_serializer=CommentSerializer,slug_field='comment')

    class Meta:
        model = Topic
        fields = '__all__'
        # TODO:: refactor after deciding about globally pinned.
        read_only_fields = ('is_pinned',)

    def get_video_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = False),many=True).data
    def get_audio_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = True, is_audio = True) ,many=True).data
    def get_text_comments(self,instance):
        return CommentSerializer(instance.topic_comment.filter(is_media = False) ,many=True).data
 

class SingUpOTPSerializer(ModelSerializer):
    class Meta:
        model = SingUpOTP
        fields = ('mobile_no', )
