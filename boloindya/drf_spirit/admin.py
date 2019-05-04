from django.contrib import admin
from .models import SingUpOTP
class SingUpOTPAdmin(admin.ModelAdmin):
    list_display = ('mobile_no', 'otp', 'is_active', 'created_at', 'used_at', 'is_reset_password', 'is_for_change_phone', 'for_user', )
    list_editable = ('is_active', )
admin.site.register(SingUpOTP, SingUpOTPAdmin)


from forum.user.models import Weight,UserProfile,AppVersion
class WeightAdmin(admin.ModelAdmin):
    list_display = ('features', 'weight', )
admin.site.register(Weight, WeightAdmin)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bolo_score', )
admin.site.register(UserProfile,UserProfileAdmin)

admin.site.register(AppVersion)