from .models import *
from django.forms import ModelForm, HiddenInput, FileInput,CharField
from django import forms

class KYCBasicInfoRejectForm(ModelForm):
    class Meta():
        model = KYCBasicInfo
        fields = ['reject_reason','reject_text']

    def __init__(self,*args,**kwargs):
        super(KYCBasicInfoRejectForm,self).__init__(*args,**kwargs)
        for field in self: 
            field.field.widget.attrs['class'] = 'form-control'

class KYCDocumentRejectForm(ModelForm):
    class Meta():
        model = KYCDocument
        fields = ['reject_reason','reject_text']

    def __init__(self,*args,**kwargs):
        super(KYCDocumentRejectForm,self).__init__(*args,**kwargs)
        for field in self: 
            field.field.widget.attrs['class'] = 'form-control'

class AdditionalInfoRejectForm(ModelForm):
    class Meta():
        model = AdditionalInfo
        fields = ['reject_reason','reject_text']

    def __init__(self,*args,**kwargs):
        super(AdditionalInfoRejectForm,self).__init__(*args,**kwargs)
        for field in self: 
            field.field.widget.attrs['class'] = 'form-control'


class BankDetailRejectForm(ModelForm):
    class Meta():
        model = BankDetail
        fields = ['reject_reason','reject_text']

    def __init__(self,*args,**kwargs):
        super(BankDetailRejectForm,self).__init__(*args,**kwargs)
        for field in self: 
            field.field.widget.attrs['class'] = 'form-control'