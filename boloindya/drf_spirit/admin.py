
from django.contrib import admin
from .models import SingUpOTP, UserJarvisDump, UserFeedback
from forum.user.models import Weight,UserProfile,AppVersion, UserProfile,AndroidLogs, AppPageContent, ReferralCode, ReferralCodeUsed, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend,UserPhoneBook,Contact
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

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_name', 'is_active', 'get_language', 'get_bolo_score', 'get_follow_count', \
        'get_vb_count', 'get_is_popular', 'get_is_superstar', 'get_is_business')
    list_editable = ('is_active', )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'st__name', 'st__mobile_no', 'st__paytm_number')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_name(self, obj):
        return obj.st.name
    get_name.short_description = 'Name'

    def get_language(self, obj):
        return obj.st.language
    get_language.short_description = 'Language'

    def get_bolo_score(self, obj):
        return obj.st.bolo_score
    get_bolo_score.short_description = 'Bolo Score'

    def get_follow_count(self, obj):
        return obj.st.follow_count
    get_follow_count.short_description = 'Follow Count'

    def get_vb_count(self, obj):
        return obj.st.vb_count
    get_vb_count.short_description = 'VB Count'

    def get_is_popular(self, obj):
        if obj.st.is_popular:
            return '<img src="/static/admin/img/icon-yes.svg" alt="False">'
        return '<img src="/static/admin/img/icon-no.svg" alt="False">'
    get_is_popular.short_description = 'Popular?'
    get_is_popular.allow_tags = True

    def get_is_superstar(self, obj):
        if obj.st.is_superstar:
            return '<img src="/static/admin/img/icon-yes.svg" alt="False">'
        return '<img src="/static/admin/img/icon-no.svg" alt="False">'
    get_is_superstar.short_description = 'Superstar?'
    get_is_superstar.allow_tags = True

    def get_is_business(self, obj):
        if obj.st.is_business:
            return '<img src="/static/admin/img/icon-yes.svg" alt="False">'
        return '<img src="/static/admin/img/icon-no.svg" alt="False">'
    get_is_business.short_description = 'Business?'
    get_is_business.allow_tags = True

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class UserProfileAdmin(ImportExportModelAdmin):
    search_fields = ('user__username', 'user__email', 'name', 'mobile_no', 'paytm_number')
    list_display = ('user', 'name', 'language', 'bolo_score', 'follow_count', 'follower_count', 'vb_count', 'answer_count', \
        'share_count', 'like_count', 'is_popular','is_superstar', 'is_business')
    list_editable = ('is_popular','is_superstar', 'is_business', 'language')
    list_filter = ('user__date_joined', ('user__date_joined', DateRangeFilter), 'language','is_popular','is_superstar', 'is_business')
    resource_class = UserProfileResource
admin.site.register(UserProfile,UserProfileAdmin)

from django.db.models import Count, Q
class ReferralCodeAdmin(admin.ModelAdmin):
    change_list_template = "admin/forum_user/referralcode/change_list.html"
    list_display = ('for_user', 'get_paytm_number', 'code', 'purpose', 'is_active', 'get_downloads', 'get_signup', 'playstore_url', \
            'no_playstore_url', 'created_at')
    list_filter = ('code', 'is_active','is_refer_earn_code')
    search_fields = ('code', 'for_user__username', 'for_user__email', 'for_user__st__name', 'for_user__st__mobile_no', 'for_user__st__paytm_number')

    def get_queryset(self, request):
        queryset = super(ReferralCodeAdmin, self).get_queryset(request)
        queryset = queryset.annotate(
            _get_downloads = Count("referralcodeused", filter = Q(is_download = True, by_user__isnull = True), distinct=True),
            _get_signup = Count("referralcodeused", filter = Q(is_download = True, by_user__isnull = False), distinct=True),
        )
        return queryset

    def get_paytm_number(self, obj):
        return obj.for_user.st.paytm_number
    get_paytm_number.short_description = 'Paytm Number'

    def get_downloads(self, obj):
        # return str(obj.downloads())
        return '<a href="/superman/forum_user/referralcodeused/?code__id__exact=' + str(obj.id) + '&by_user__isnull=1" target="_blank">\
        ' + str(obj.downloads()) + '</a>'
    get_downloads.short_description = 'Downloads'
    get_downloads.allow_tags = True
    get_downloads.admin_order_field = '_get_downloads'

    def get_signup(self, obj):
        return '<a href="/superman/forum_user/referralcodeused/?code__id__exact=' + str(obj.id) + '&by_user__isnull=0" target="_blank">\
        ' + str(obj.signup()) + '</a>'
    get_signup.short_description = 'Signup'
    get_signup.allow_tags = True
    get_signup.admin_order_field = '_get_signup'

admin.site.register(ReferralCode, ReferralCodeAdmin)

class ReferralCodeUsedAdmin(admin.ModelAdmin):
    list_display = ('code', 'get_user', 'get_install_time', 'get_signup_time', 'get_last_active_time', 'android_id')
    search_fields = ('code__code', )
    list_filter = ('created_at', ('created_at', DateRangeFilter), ) # 'code'

    def get_queryset(self, request):
        qs = super(ReferralCodeUsedAdmin, self).get_queryset(request)
        if request.GET.get('by_user__isnull') and request.GET.get('by_user__isnull') == '0':
            qs = qs.order_by('by_user').distinct('by_user')
        if request.GET.get('by_user__isnull') and request.GET.get('by_user__isnull') == '1':
            qs = qs.order_by('android_id').distinct('android_id')
        return qs

    def get_user(self, obj):
        if obj.by_user:
            return obj.by_user.username
        return '-'
    get_user.short_description = 'User'
    
    def get_install_time(self, obj):
        try:
            first_install = ReferralCodeUsed.objects.filter(code = obj.code, is_download = True, by_user__isnull = True, android_id = obj.android_id)\
                .order_by('last_modified').first().last_modified
            return first_install
        except:
            return '~ ' + obj.created_at.strftime('%b %d, %Y, %I:%M %p')

    get_install_time.short_description = 'install'

    def get_signup_time(self, obj):
        if obj.by_user:
            return obj.by_user.date_joined
        return '-'
    get_signup_time.short_description = 'signup'

    def get_last_active_time(self, obj):
        try:
            last_active = AndroidLogs.objects.filter(user = obj.by_user).order_by('-last_modified').first().last_modified
            return last_active
        except:
            return '-'
    get_last_active_time.short_description = 'last active'

admin.site.register(ReferralCodeUsed, ReferralCodeUsedAdmin)

class AndroidLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'last_modified', 'log_type',)
    search_fields = ('user', )

class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('by_user', 'created_at', 'contact_email', 'feedback_image', 'user_contact')
    search_fields = ('by_user', 'contact_email')

    # def render_change_form(self, request, context, *args, **kwargs):
    #     context['adminform'].form.fields['by_user'].queryset = User.objects.filter(st__is_test_user = False)
    #     return super(UserFeedbackAdmin, self).render_change_form(request, context, *args, **kwargs)

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
admin.site.register(UserPhoneBook)
admin.site.register(Contact)

