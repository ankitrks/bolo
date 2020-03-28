
from django.contrib import admin
from .models import SingUpOTP, UserJarvisDump, UserFeedback
from forum.user.models import Weight,UserProfile,AppVersion, UserProfile,AndroidLogs, AppPageContent, ReferralCode, ReferralCodeUsed, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend
from forum.category.models import Category,CategoryViewCounter
from import_export.admin import ImportExportModelAdmin,ExportMixin
from import_export import resources
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .models import UserFollowUnfollowDetails, UserVideoTypeDetails, VideoDetails, UserEntryPoint, UserViewedFollowersFollowing, UserInterest, VideoSharedDetails, UserSearch, UserLogStatistics
from django.contrib.auth.models import User

class UserProfileResource(resources.ModelResource):
	class Meta:
		model = UserProfile
		skip_unchanged = True
		report_skipped = True
		list_filter = ('language','is_popular','is_superstar','is_business')
		fields = ( 'user__username', 'name', 'language', 'bolo_score', 'user__date_joined', 'follow_count', 'follower_count', \
			'vb_count', 'answer_count', 'share_count', 'like_count')

class SingUpOTPAdmin(admin.ModelAdmin):
	list_display = ('mobile_no', 'otp', 'is_active', 'created_at', 'used_at', 'is_reset_password', 'is_for_change_phone', 'for_user', )
	list_editable = ('is_active', )
admin.site.register(SingUpOTP, SingUpOTPAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'hindi_title','tamil_title','telgu_title','bengali_title','kannada_title', 'order_no')
    list_editable = ('order_no', )
admin.site.register(Category, CategoryAdmin)

class WeightAdmin(admin.ModelAdmin):
	list_display = ('features', 'weight', 'is_monetize', 'bolo_score', 'equivalent_INR' )
admin.site.register(Weight, WeightAdmin)

class UserProfileAdmin(ImportExportModelAdmin):
	search_fields = ('user__username', 'name',)
	list_display = ('user', 'name', 'language', 'bolo_score', 'follow_count', 'follower_count', 'vb_count', 'answer_count', \
		'share_count', 'like_count', 'is_popular','is_superstar', 'is_business')
	list_editable = ('is_popular','is_superstar', 'is_business', 'language')
	list_filter = ('user__date_joined', ('user__date_joined', DateRangeFilter), 'language','is_popular','is_superstar', 'is_business')
	resource_class = UserProfileResource
admin.site.register(UserProfile,UserProfileAdmin)

class ReferralCodeAdmin(admin.ModelAdmin):
	change_list_template = "admin/forum_user/referralcode/change_list.html"
	list_display = ('for_user','code', 'purpose', 'is_active', 'downloads', 'signup', 'playstore_url', 'no_playstore_url', 'created_at')
	list_filter = ('code', 'is_active','is_refer_earn_code')
	search_fields = ('code', )
admin.site.register(ReferralCode, ReferralCodeAdmin)

class ReferralCodeUsedAdmin(admin.ModelAdmin):
	list_display = ('code', 'by_user', 'is_download', 'created_at', 'last_modified', 'click_id', 'pid', 'android_id')
	search_fields = ('code__code', )
        list_filter = ('created_at', ('created_at', DateRangeFilter), 'code')
admin.site.register(ReferralCodeUsed, ReferralCodeUsedAdmin)

class AndroidLogsAdmin(admin.ModelAdmin):
	list_display = ('user', 'created_at', 'last_modified', 'log_type',)
	search_fields = ('user', )

class UserFeedbackAdmin(admin.ModelAdmin):
	list_display = ('by_user', 'created_at', 'contact_email', 'feedback_image', 'user_contact')
	search_fields = ('by_user', 'contact_email')

	# def render_change_form(self, request, context, *args, **kwargs):
	# 	context['adminform'].form.fields['by_user'].queryset = User.objects.filter(st__is_test_user = False)
	# 	return super(UserFeedbackAdmin, self).render_change_form(request, context, *args, **kwargs)

admin.site.register(AppVersion)
admin.site.register(CategoryViewCounter)
admin.site.register(AndroidLogs, AndroidLogsAdmin)
admin.site.register(AppPageContent)

#user information models
admin.site.register(UserJarvisDump)
admin.site.register(UserFeedback, UserFeedbackAdmin)
admin.site.register(UserFollowUnfollowDetails)
admin.site.register(UserVideoTypeDetails)
admin.site.register(VideoDetails)
admin.site.register(UserEntryPoint)
admin.site.register(UserViewedFollowersFollowing)
admin.site.register(UserInterest)
admin.site.register(VideoSharedDetails)
admin.site.register(UserSearch)
admin.site.register(UserLogStatistics)
admin.site.register(VideoPlaytime)
admin.site.register(VideoCompleteRate)
admin.site.register(UserAppTimeSpend)

