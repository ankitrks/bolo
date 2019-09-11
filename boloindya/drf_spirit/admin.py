from django.contrib import admin
from .models import SingUpOTP, UserJarvisDump
from forum.user.models import Weight,UserProfile,AppVersion, UserProfile,AndroidLogs, AppPageContent, ReferralCode, ReferralCodeUsed
from forum.category.models import Category
from import_export.admin import ImportExportModelAdmin,ExportMixin
from import_export import resources
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .models import user_follow_unfollow_details, user_videotype_details, video_details, user_entry_point, user_viewed_followers_following, user_interest, video_shared_details


class UserProfileResource(resources.ModelResource):
	class Meta:
		model = UserProfile
		skip_unchanged = True
		report_skipped = True
		list_filter = ('language', )
		fields = ( 'user__username', 'name','language','bolo_score','user__date_joined','follow_count','follower_count','question_count','answer_count','share_count','like_count')

class SingUpOTPAdmin(admin.ModelAdmin):
	list_display = ('mobile_no', 'otp', 'is_active', 'created_at', 'used_at', 'is_reset_password', 'is_for_change_phone', 'for_user', )
	list_editable = ('is_active', )
admin.site.register(SingUpOTP, SingUpOTPAdmin)

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('title', 'hindi_title','tamil_title','telgu_title', )
admin.site.register(Category, CategoryAdmin)

class WeightAdmin(admin.ModelAdmin):
	list_display = ('features', 'weight', )
admin.site.register(Weight, WeightAdmin)

class UserProfileAdmin(ImportExportModelAdmin):
	search_fields = ('user__username','name',)
	list_display = ('user', 'name','language','bolo_score','follow_count','follower_count','question_count','answer_count','share_count','like_count')
	list_filter = ('user__date_joined', ('user__date_joined', DateRangeFilter), 'language')
	resource_class = UserProfileResource
admin.site.register(UserProfile,UserProfileAdmin)

class ReferralCodeAdmin(admin.ModelAdmin):
	change_list_template = "admin/forum_user/referralcode/change_list.html"
	list_display = ('code', 'purpose', 'is_active', 'downloads', 'signup', 'playstore_url', 'no_playstore_url', 'created_at')
	list_filter = ('code', 'is_active')
	search_fields = ('code', )
admin.site.register(ReferralCode, ReferralCodeAdmin)

class ReferralCodeUsedAdmin(admin.ModelAdmin):
	list_display = ('code', 'by_user', 'is_download', 'created_at', 'last_modified')
	search_fields = ('code__code', )
admin.site.register(ReferralCodeUsed, ReferralCodeUsedAdmin)

admin.site.register(AppVersion)
admin.site.register(AndroidLogs)
admin.site.register(AppPageContent)

# user information models
admin.site.register(UserJarvisDump)
admin.site.register(user_follow_unfollow_details)
admin.site.register(user_videotype_details)
admin.site.register(video_details)
admin.site.register(user_entry_point)
admin.site.register(user_viewed_followers_following)
admin.site.register(user_interest)
admin.site.register(video_shared_details)



