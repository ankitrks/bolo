
from django.contrib import admin
from .models import SingUpOTP, UserJarvisDump, UserFeedback, Campaign, Winner
from forum.user.models import Weight,UserProfile,AppVersion, UserProfile,AndroidLogs, AppPageContent, ReferralCode, ReferralCodeUsed, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend,UserPhoneBook,Contact
from forum.category.models import Category,CategoryViewCounter
from import_export.admin import ImportExportModelAdmin,ExportMixin
from import_export import resources
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .models import UserFollowUnfollowDetails, UserVideoTypeDetails, VideoDetails, UserEntryPoint, UserViewedFollowersFollowing, UserInterest, VideoSharedDetails, UserSearch, UserLogStatistics
from django.contrib.auth.models import User
# from django.db.models import Count, Q
from forum.topic.models import VBseen

import datetime
import pytz
from django.utils import timezone
from django.contrib.admin.filters import DateFieldListFilter
from django.utils.translation import gettext_lazy as _
class CustomDateTimeFilter(DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super(CustomDateTimeFilter, self).__init__(*args, **kwargs)
        now = timezone.now()
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        today = now.date()
        yesterday = today - datetime.timedelta(days=1)
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        
        self.links = (
            (_('Any date'), {}),
            (_('Today'), {
                self.lookup_kwarg_since: str(datetime.datetime.strptime((today.strftime('%b %d, %Y') + ' 00:00:00'), '%b %d, %Y %H:%M:%S')),
                self.lookup_kwarg_until: str(datetime.datetime.strptime((today.strftime('%b %d, %Y') + ' 23:59:59'), '%b %d, %Y %H:%M:%S')),
            }),
            (_('Yesterday'), {
                self.lookup_kwarg_since: str(datetime.datetime.strptime((yesterday.strftime('%b %d, %Y') + ' 00:00:00'), '%b %d, %Y %H:%M:%S')),
                self.lookup_kwarg_until: str(datetime.datetime.strptime((yesterday.strftime('%b %d, %Y') + ' 23:59:59'), '%b %d, %Y %H:%M:%S')),
            }),
            (_('Past 3 days'), {
                self.lookup_kwarg_since: str(today - datetime.timedelta(days=3)),
                self.lookup_kwarg_until: str(today),
            }),
            (_('Past 7 days'), {
                self.lookup_kwarg_since: str(today - datetime.timedelta(days=7)),
                self.lookup_kwarg_until: str(today),
            }),
            (_('This month'), {
                self.lookup_kwarg_since: str(today.replace(day=1)),
                self.lookup_kwarg_until: str(next_month),
            }),
        )

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
    list_display = ('username', 'date_joined', 'email', 'get_name', 'is_active', 'get_language', 'get_bolo_score', 'get_follow_count', \
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

class ReferralCodeAdmin(admin.ModelAdmin):
    change_list_template = "admin/forum_user/referralcode/change_list.html"
    list_display = ('for_user', 'get_paytm_number', 'code', 'purpose', 'is_active', 'get_downloads', 'get_signup', 'playstore_url', \
            'no_playstore_url', 'created_at')
    list_filter = ('code', 'is_active', 'is_refer_earn_code', ('refcode__created_at', CustomDateTimeFilter), ('refcode__created_at', DateRangeFilter) )
    search_fields = ('code', 'for_user__username', 'for_user__email', 'for_user__st__name', 'for_user__st__mobile_no', 'for_user__st__paytm_number')

    def changelist_view(self, request, *args, **kwargs):
        self.request = request
        return super(ReferralCodeAdmin, self).changelist_view(request, *args, **kwargs)

    # def get_queryset(self, request):
    #     queryset = super(ReferralCodeAdmin, self).get_queryset(request)
    #     queryset = queryset.annotate(
    #         _get_downloads = Count("referralcodeused", filter = (Q(is_download = True, by_user__isnull = True)).values_list('android_id'), distinct=True),
    #         _get_signup = Count("referralcodeused", filter = (Q(is_download = True, by_user__isnull = False)).values_list('by_user'), distinct=True),
    #     )
    #     return queryset

    def get_ordering(self, request):
        return ('-signup_count', )

    def get_paytm_number(self, obj):
        if obj.for_user:
            return obj.for_user.st.paytm_number
        return '-'
    get_paytm_number.short_description = 'Paytm Number'

    def get_downloads(self, obj):
        if self.request.GET.get('refcode__created_at__gte') or self.request.GET.get('refcode__created_at__lte') \
                or self.request.GET.get('refcode__created_at__lt'):
            fdict = {}
            getstr=[]
            if self.request.GET.get('refcode__created_at__gte'):
                fdict['created_at__gte'] = self.request.GET.get('refcode__created_at__gte')
                getstr.append('created_at__gte=' + self.request.GET.get('refcode__created_at__gte'))
            if self.request.GET.get('refcode__created_at__lte'):
                fdict['created_at__lt'] = self.request.GET.get('refcode__created_at__lte')
                getstr.append('created_at__lt=' + self.request.GET.get('refcode__created_at__lte'))
            if self.request.GET.get('refcode__created_at__lt'):
                fdict['created_at__lt'] = self.request.GET.get('refcode__created_at__lt')
                getstr.append('created_at__lt=' + self.request.GET.get('refcode__created_at__lt'))
            return '<a href="/superman/forum_user/referralcodeused/?code__id__exact=' + str(obj.id) + '&by_user__isnull=1&' + '&'.join(getstr) \
                + '" target="_blank">' + str(obj.downloads_list().filter(**fdict).distinct('android_id').count()) + '</a>'
        else:
            return '<a href="/superman/forum_user/referralcodeused/?code__id__exact=' + str(obj.id) + '&by_user__isnull=1" target="_blank">\
                ' + str(obj.download_count) + '</a>'
    get_downloads.short_description = 'Downloads'
    get_downloads.allow_tags = True
    get_downloads.admin_order_field = 'download_count'

    def get_signup(self, obj):
        if self.request.GET.get('refcode__created_at__gte') or self.request.GET.get('refcode__created_at__lte')\
                or self.request.GET.get('refcode__created_at__lte'):
            fdict = {}
            getstr=[]
            if self.request.GET.get('refcode__created_at__gte'):
                fdict['created_at__gte'] = self.request.GET.get('refcode__created_at__gte')
                getstr.append('created_at__gte=' + self.request.GET.get('refcode__created_at__gte'))
            if self.request.GET.get('refcode__created_at__lte'):
                fdict['created_at__lt'] = self.request.GET.get('refcode__created_at__lte')
                getstr.append('created_at__lt=' + self.request.GET.get('refcode__created_at__lte'))
            if self.request.GET.get('refcode__created_at__lt'):
                fdict['created_at__lt'] = self.request.GET.get('refcode__created_at__lt')
                getstr.append('created_at__lt=' + self.request.GET.get('refcode__created_at__lt'))
            return '<a href="/superman/forum_user/referralcodeused/?code__id__exact=' + str(obj.id) + '&by_user__isnull=0&' + '&'.join(getstr) \
                + '" target="_blank">' + str(obj.signup_list().filter(**fdict).distinct('by_user').count()) + '</a>'
        else:
            return '<a href="/superman/forum_user/referralcodeused/?code__id__exact=' + str(obj.id) + '&by_user__isnull=0" target="_blank">\
                ' + str(obj.signup_count) + '</a>'
    get_signup.short_description = 'Signup'
    get_signup.allow_tags = True
    get_signup.admin_order_field = 'signup_count'

admin.site.register(ReferralCode, ReferralCodeAdmin)

class ReferralCodeUsedAdmin(admin.ModelAdmin):
    list_display = ('code', 'get_user', 'get_user_name', 'get_phone', 'get_install_time', 'get_signup_time', 'get_last_active_time',\
        'android_id', 'created_at')
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

    def get_user_name(self, obj):
        if obj.by_user:
            return obj.by_user.st.name
        return '-'
    get_user_name.short_description = 'Name'

    def get_phone(self, obj):
        if obj.by_user:
            return obj.by_user.st.mobile_no
        return '-'
    get_phone.short_description = 'phone no'
    
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
            last_active = AndroidLogs.objects.filter(user = obj.by_user).order_by('-last_modified').first()
            if last_active:
                return last_active.last_modified
            else:
                last_active = VBseen.objects.filter(user = obj.by_user).order_by('-last_modified').first()
                if last_active:
                    return '~ ' + last_active.last_modified.strftime('%b %d, %Y, %I:%M %p')
        except:
            return '-'
    get_last_active_time.short_description = 'last active'

admin.site.register(ReferralCodeUsed, ReferralCodeUsedAdmin)

class AndroidLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'last_modified', 'log_type', 'android_id')
    search_fields = ('user', )

class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('by_user', 'created_at', 'contact_email', 'feedback_image', 'user_contact')
    search_fields = ('by_user', 'contact_email')

    # def render_change_form(self, request, context, *args, **kwargs):
    #     context['adminform'].form.fields['by_user'].queryset = User.objects.filter(st__is_test_user = False)
    #     return super(UserFeedbackAdmin, self).render_change_form(request, context, *args, **kwargs)

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('hashtag', 'is_active', 'active_from', 'active_till', 'is_winner_declared')
    raw_id_fields = ('hashtag', 'next_campaign_hashtag')

class WinnerAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']        

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
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Winner, WinnerAdmin)

