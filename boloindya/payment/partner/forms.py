from django import forms

class OTPForm(forms.Form):
    otp = forms.CharField(label='OTP', max_length=10)