from .models import *
from django.forms import ModelForm, HiddenInput, FileInput,CharField
from django import forms
from forum.topic.models import Topic

class VideoUploadTranscodeForm(ModelForm):
    class Meta():
        model = VideoUploadTranscode
        fields = ['category','is_free_video','video_title','video_descp','meta_title','meta_descp','meta_keywords']

    def __init__(self,*args,**kwargs):
        super(VideoUploadTranscodeForm,self).__init__(*args,**kwargs)
        for field in self: 
            if not field.name=='is_free_video':
                field.field.widget.attrs['class'] = 'form-control'

class TopicUploadTranscodeForm(ModelForm):
    class Meta():
        model = Topic
        fields = ['title','m2mcategory','language_id','is_pubsub_popular_push']

    def __init__(self,*args,**kwargs):
        super(TopicUploadTranscodeForm,self).__init__(*args,**kwargs)
        for field in self: 
            if not field.name=='is_pubsub_popular_push':
                field.field.widget.attrs['class'] = 'form-control'