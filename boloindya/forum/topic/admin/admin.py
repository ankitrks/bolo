# from utils import admin_all
from forum.topic.models import *
from django.contrib import admin
from drf_spirit.views import check_hashtag
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from forum.topic.models import Topic, Notification, ShareTopic, CricketMatch, Poll, Choice, Voting, Leaderboard,\
 TongueTwister, BoloActionHistory
from forum.category.models import Category
from forum.topic.models import Topic, Notification, ShareTopic, CricketMatch, Poll, Choice, Voting, Leaderboard, \
        TongueTwister, BoloActionHistory, language_options,JobOpening,JobRequest
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

class TopicResource(resources.ModelResource):
    class Meta:
        model = Topic
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ( 'title', 'category__title','language_id','user_id')
        fields = ( 'id', 'title','user__username','category__title','media_duration','is_media','comments')

from django import forms
class TopicChangeListForm(forms.ModelForm):
    m2mcategory = forms.ModelMultipleChoiceField(queryset = Category.objects.all(), \
            widget = forms.CheckboxSelectMultiple, required = False)
    title = forms.CharField(required = True)
    language_id = forms.ChoiceField(choices = language_options,required = True)
    is_pubsub_popular_push = forms.BooleanField(required = False)
    is_monetized = forms.BooleanField(required = False)
    is_removed = forms.BooleanField(required = False)
    is_moderated = forms.BooleanField(required = False)
    # is_popular = forms.BooleanField(required = False)

from django.contrib.admin.views.main import ChangeList
PAGE_VAR = 'p'
ALL_VAR = 'all'
ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'
PAGE_VAR = 'p'
SEARCH_VAR = 'q'
ERROR_FLAG = 'e'
from django.contrib.admin.options import (
    IS_POPUP_VAR, TO_FIELD_VAR, IncorrectLookupParameters,
)
from django.utils.translation import ugettext
from django.utils.encoding import force_text
class TopicChangeList(ChangeList):
    def __init__(self, request, model, list_display, list_display_links,
            list_filter, date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, model_admin):

        # super(TopicChangeList, self).__init__(request, model, list_display, list_display_links,
        #     list_filter, date_hierarchy, search_fields, list_select_related,
        #     list_per_page, list_max_show_all, list_editable, model_admin)
        # action_checkbox
        self.list_display = ('id', 'vb_list', 'title', 'name', 'duration', 'language_id', 'imp_count',\
            'is_moderated', 'is_monetized', 'is_removed', 'is_pubsub_popular_push', 'date', 'm2mcategory') #is_popular
        self.list_display_links = ['id']
        self.list_editable = ('title', 'language_id', 'm2mcategory', 'is_pubsub_popular_push', 'is_monetized', 'is_removed', \
                'is_moderated')
        self.model = model
        self.opts = model._meta
        self.lookup_opts = self.opts
        self.root_queryset = model_admin.get_queryset(request)
        self.list_filter = list_filter
        self.date_hierarchy = date_hierarchy
        self.search_fields = search_fields
        self.list_select_related = list_select_related
        self.list_per_page = list_per_page
        self.list_max_show_all = list_max_show_all
        self.model_admin = model_admin
        self.preserved_filters = model_admin.get_preserved_filters(request)

        # Get search parameters from the query string.
        try:
            self.page_num = int(request.GET.get(PAGE_VAR, 0))
        except ValueError:
            self.page_num = 0
        self.show_all = ALL_VAR in request.GET
        self.is_popup = IS_POPUP_VAR in request.GET
        to_field = request.GET.get(TO_FIELD_VAR)
        if to_field and not model_admin.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)
        self.to_field = to_field
        self.params = dict(request.GET.items())
        if PAGE_VAR in self.params:
            del self.params[PAGE_VAR]
        if ERROR_FLAG in self.params:
            del self.params[ERROR_FLAG]

        self.query = request.GET.get(SEARCH_VAR, '')
        self.queryset = self.get_queryset(request)
        self.get_results(request)
        if self.is_popup:
            title = ugettext('Select %s')
        else:
            title = ugettext('Select %s to change')
        self.title = title % force_text(self.opts.verbose_name)
        self.pk_attname = self.lookup_opts.pk.attname

class TopicAdmin(admin.ModelAdmin): # to enable import/export, use "ImportExportModelAdmin" NOT "admin.ModelAdmin"
    ordering = ['is_vb', '-id']
    search_fields = ('title', 'user__username', 'user__st__name', )
    list_filter = (('date', DateRangeFilter), 'language_id', 'm2mcategory', 'is_moderated', 'is_monetized', 'is_removed', 'is_popular')
    filter_horizontal = ('m2mcategory', )

    fieldsets = (
        (None, {
            'fields': ('title', 'm2mcategory')
        }),
        ('VB Details', {
            'fields': ('language_id', 'media_duration','is_pubsub_popular_push'),
        }),
        ('Counts', {
            'fields': (('view_count', 'comment_count'), ('total_share_count', 'share_count'), 'likes_count'),
        }),
        ('Transcode Options', {
            'classes': ('collapse',),
            'fields': ('backup_url', ('is_transcoded', 'is_transcoded_error'), 'transcode_job_id', \
                        'transcode_dump', 'transcode_status_dump', 'm3u8_content', 'audio_m3u8_content', 'video_m3u8_content'),
        }),
        ('Others', {
            'fields': (('plag_text', 'time_deleted')),
        }),
    )

    def get_changelist(self, request, **kwargs):
        return TopicChangeList

    def get_changelist_form(self, request, **kwargs):
        return TopicChangeListForm

    def duration(self, obj):
        return obj.duration()
    duration.short_description = "duration"
    duration.admin_order_field = 'media_duration'

    def vb_list(self, obj):
        return '<a href="?user_id="' + str(obj.user.id) +'" target="_blank">l</a>'
    vb_list.allow_tags = True
    vb_list.short_description = "vb"

    def comments(self, obj):
        return obj.comments()
    comments.short_description = "comments"
    comments.admin_order_field = 'comment_count'

    actions = [] # ['remove_selected', 'remove_from_monetization', 'restore_selected', 'add_monetization']
    # def remove_selected(self, request, queryset):
    #     for each_obj in queryset:
    #         if not each_obj.is_removed:
    #             each_obj.delete()
    # remove_selected.short_description = "Delete selected Records!"

    # def remove_from_monetization(self, request, queryset):
    #     for each_obj in queryset:
    #         if each_obj.is_monetized:
    #             each_obj.no_monetization()
    # remove_from_monetization.short_description = "Remove from Monetization!"

    # def restore_selected(self, request, queryset):
    #     for each_obj in queryset:
    #         if each_obj.is_removed:
    #             each_obj.restore()
    # restore_selected.short_description = "Restore selected Records (No Monetization)!"

    # def add_monetization(self, request, queryset):
    #     for each_obj in queryset:
    #         if each_obj.is_removed:
    #             each_obj.restore()
    #         if not each_obj.is_monetized:
    #             each_obj.add_monetization()
    # add_monetization.short_description = "Restore & Add to Monetization!"

    def get_actions(self, request):
        actions = super(TopicAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        if 'title' in form.changed_data:
            obj.title = form.cleaned_data['title']
        if 'language_id' in form.changed_data:
            obj.language_id = form.cleaned_data['language_id']
        if 'is_pubsub_popular_push' in form.changed_data:
            obj.is_pubsub_popular_push = form.cleaned_data['is_pubsub_popular_push']
        if 'is_moderated' in form.changed_data:
            obj.is_moderated = form.cleaned_data['is_moderated']
        if 'is_monetized' in form.changed_data:
            obj.is_monetized = form.cleaned_data['is_monetized']
            if obj.is_monetized:
                if obj.is_removed:
                    obj.restore()
                obj.add_monetization()
            else:
                obj.no_monetization()

        if 'is_removed' in form.changed_data:
            obj.is_removed = form.cleaned_data['is_removed']
            if obj.is_removed:
                obj.delete()
            else:
                obj.restore()

        if 'title' in form.changed_data:
            tag_list = obj.title.split()
            hash_tag = tag_list
            if tag_list:
                for index, value in enumerate(tag_list):
                    if value.startswith("#"):
                        tag_list[index]='<a href="/get_challenge_details/?ChallengeHash='+value.strip('#')+'">'+value+'</a>'
                title = " ".join(tag_list)
                obj.title = title[0].upper()+title[1:]

        obj.save()
        if 'language_id' in form.changed_data and obj.is_monetized:
            if form.initial['language_id'] == '1':
                userprofile = UserProfile.objects.get(user = obj.user)
                userprofile.save()
                reduce_bolo_score(obj.user.id, 'create_topic_en', obj, 'no_monetize')
                obj.add_monetization()
            elif obj.language_id == '1':
                userprofile = UserProfile.objects.get(user = obj.user)
                userprofile.save()
                reduce_bolo_score(obj.user.id, 'create_topic', obj, 'no_monetize')
                obj.add_monetization()
        super(TopicAdmin,self).save_model(request, obj, form, change)

    # def comment_count(self, obj):
    #     url = '/forum_comment/comment/?topic_id='+obj.id
    #     print url, obj.comment_count
    #     return '<a href="%s" target="_blank">%s</a>' % (url, obj.comment_count)
    # comment_count.allow_tags = True
    # comment_count.short_description = 'Click to open the detail list of answers'

class BoloActionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'score', 'action', 'action_object', 'is_removed')
    # list_filter = ('user__st__name', )
    search_fields = ('user__username', 'user__st__name')
admin.site.register(BoloActionHistory, BoloActionHistoryAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'for_user', 'user', 'notification_type')

class ShareTopicAdmin(admin.ModelAdmin):
    list_display = ('id','user')

class CricketMatchAdmin(admin.ModelAdmin):
    list_display = ('match_name', 'team_1', 'team_2', 'match_datetime', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('match_name', )
        }),
        ('Team 1', {
            'fields': ('team_1', 'team_1_flag'),
        }),
        ('Team 2', {
            'fields': ('team_2', 'team_2_flag'),
        }),
        ('Advance Options', {
            'fields': ('match_datetime', 'is_active'),
        }),
    )
admin.site.register(CricketMatch, CricketMatchAdmin)

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'cricketmatch', 'activate_datetime', 'deactivate_datetime', 'score', 'bolo_score', 'is_evaluated')
    list_editable = ('activate_datetime', 'deactivate_datetime', 'score', 'bolo_score', 'is_evaluated')
    inlines = [ChoiceInline]
    fieldsets = (
        (None, {
            'fields': ('cricketmatch', 'title')
        }),
        ('Score', {
            'fields': (('score', 'bolo_score'), ),
        }),
        ('Date / Time', {
            'fields': (('activate_datetime', 'deactivate_datetime'), ),
        }),
        ('Advance Options', {
            'classes': ('collapse',),
            'fields': ('is_evaluated', 'is_active'),
        }),
    )
admin.site.register(Poll, PollAdmin)

admin.site.register(Topic, TopicAdmin)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(ShareTopic,ShareTopicAdmin)
admin.site.register(Voting)
admin.site.register(Leaderboard)
admin.site.register(VBseen)
admin.site.register(TongueTwister)
admin.site.register(JobOpening)
admin.site.register(JobRequest)

