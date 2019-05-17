from django.contrib import admin
from .models import SingUpOTP
from forum.user.models import Weight,UserProfile,AppVersion
from import_export.admin import ImportExportModelAdmin,ExportMixin
from import_export import resources
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter


class UserProfileResource(resources.ModelResource):

	class Meta:
		model = UserProfile
		skip_unchanged = True
		report_skipped = True
		fields = ( 'user__username', 'name','language','bolo_score','user__date_joined','follow_count','follower_count','question_count','answer_count','share_count','like_count')

class SingUpOTPAdmin(admin.ModelAdmin):
    list_display = ('mobile_no', 'otp', 'is_active', 'created_at', 'used_at', 'is_reset_password', 'is_for_change_phone', 'for_user', )
    list_editable = ('is_active', )
admin.site.register(SingUpOTP, SingUpOTPAdmin)

class WeightAdmin(admin.ModelAdmin):
    list_display = ('features', 'weight', )
admin.site.register(Weight, WeightAdmin)

class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ('user', 'bolo_score', )
    list_filter = ('user__date_joined', ('user__date_joined', DateRangeFilter), )
    resource_class = UserProfileResource
admin.site.register(UserProfile,UserProfileAdmin)

admin.site.register(AppVersion)