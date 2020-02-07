from .models import *
from django.forms import ModelForm, HiddenInput, FileInput,CharField
from django import forms
from forum.topic.models import Topic
from forum.user.models import UserPay

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
    gender_options = (
        ('0','Please Select User Gender'),
        ('1', 'Male'),
        ('2', 'Female'),
    )
    gender = forms.ChoiceField(choices=gender_options, required=True, label='Gender')
    class Meta():
        model = Topic
        fields = ['title','m2mcategory','language_id','gender']

    def __init__(self,*args,**kwargs):
        super(TopicUploadTranscodeForm,self).__init__(*args,**kwargs)
        for field in self: 
            field.field.widget.attrs['class'] = 'form-control'

class UserPayForm(ModelForm):
    class Meta():
        model = UserPay
        fields = '__all__'
        fields = ['for_year','for_month','amount_pay','transaction_id']
        
    def __init__(self,*args,**kwargs):
        super(UserPayForm,self).__init__(*args,**kwargs)
        for field in self: 
            field.field.widget.attrs['class'] = 'form-control'