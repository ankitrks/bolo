from django.forms import ModelForm, HiddenInput, FileInput,CharField
from django import forms
from .models import PaymentInfo

class PaymentForm(ModelForm):
	class Meta():
		model = PaymentInfo
		exclude = ['user','created_at','last_modified','is_active']
		widgets = {
			'enchashable_detail' : HiddenInput()
		}
	def __init__(self,*args,**kwargs):
		super(PaymentForm,self).__init__(*args,**kwargs)
		self.fields['enchashable_detail'].required  = True
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'