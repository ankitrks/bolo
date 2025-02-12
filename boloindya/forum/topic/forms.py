# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_bytes
from django.utils import timezone

from ..core import utils
from ..core.utils.forms import NestedModelChoiceField
from ..category.models import Category
from .models import Topic,JobRequest
from django.core.validators import validate_email
from django.forms import ValidationError
class TopicForm(forms.ModelForm):

    topic_hash = forms.CharField(
        max_length=32,
        widget=forms.HiddenInput,
        required=False)

    class Meta:
        model = Topic
        fields = ('title', 'category')

    def __init__(self, user, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['category'] = NestedModelChoiceField(
            queryset=Category.objects.visible().opened(),
            related_name='parent_category',
            parent_field='parent_id',
            label_field='title',
            label=_("Category"),
            empty_label=_("Chose a category"))

        if self.instance.pk and not user.st.is_moderator:
            del self.fields['category']

    def get_category(self):
        return self.cleaned_data['category']

    def get_topic_hash(self):
        topic_hash = self.cleaned_data.get('topic_hash', None)

        if topic_hash:
            return topic_hash

        return utils.get_hash((
            smart_bytes(self.cleaned_data['title']),
            smart_bytes('category-{}'.format(self.cleaned_data['category'].pk))))

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user

        self.instance.reindex_at = timezone.now()
        return super(TopicForm, self).save(commit)

class JobRequestForm(forms.ModelForm):
    initialVal=""
    class Meta:
        model = JobRequest
        fields = ('name', 'email', 'mobile', 'document','cover_letter','help_text')

    def __init__(self, *args, **kwargs):
        super(JobRequestForm, self).__init__(*args, **kwargs)
        initialVal=self.instance.jobOpening_id
    jobOpening_id = forms.CharField(
        max_length=32,
        widget=forms.HiddenInput,
        required=False,initial=initialVal)

    def clean(self): 

        # data from the form is fetched using super function  
        cleaned_data = super(JobRequestForm,self).clean() 
        # extract the username and text field from the data 
        name = self.cleaned_data.get('name') 
        email = self.cleaned_data.get('email') 
  
        # conditions to be met for the username length 
        if not (name): 
            raise forms.ValidationError(_("Name is required"))
        try:
            validate_email(email)
            valid_email = True
        except validate_email:
            valid_email = False

        if valid_email==False: 
            raise forms.ValidationError(_("Email is required"))
  
        # return any errors if found 
        return self.cleaned_data 
        
