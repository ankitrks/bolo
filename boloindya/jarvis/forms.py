from .models import *
from django.forms import ModelForm, HiddenInput, FileInput,CharField
from django import forms

class VideoUploadTranscodeForm(ModelForm):
    class Meta():
        model = VideoUploadTranscode
        fields = ['category','is_free_video','video_title','video_descp']

    def __init__(self,*args,**kwargs):
        super(VideoUploadTranscodeForm,self).__init__(*args,**kwargs)
        for field in self: 
            if not field.name=='is_free_video':
                field.field.widget.attrs['class'] = 'form-control'