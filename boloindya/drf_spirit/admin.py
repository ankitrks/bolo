from django.contrib import admin
from .models import SingUpOTP
class SingUpOTPAdmin(admin.ModelAdmin):
    list_display = ('mobile_no', 'otp', 'is_active', 'created_at', 'used_at', 'is_reset_password', 'for_user', )
admin.site.register(SingUpOTP, SingUpOTPAdmin)