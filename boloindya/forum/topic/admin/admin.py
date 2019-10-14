# from utils import admin_all
from forum.topic.models import *
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from forum.topic.models import Topic, Notification, ShareTopic, CricketMatch, Poll, Choice, Voting, Leaderboard,\
 TongueTwister, BoloActionHistory
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

class TopicResource(resources.ModelResource):
    class Meta:
        model = Topic
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ( 'title', 'category__title','language_id','user_id')
        fields = ( 'id', 'title','user__username','category__title','media_duration','is_media','comments')


class TopicAdmin(ImportExportModelAdmin):
    ordering = ['is_vb', '-id']
    search_fields = ('title', 'user__username', 'user__st__name')
    list_filter = ('language_id','date', ('date', DateRangeFilter), 'is_removed', 'is_monetized', 'm2mcategory')
    list_display = ('id', 'title', 'name', 'duration', 'language_id', 'is_monetized', 'comments', 'is_removed', 'date')
    list_editable = ('title', 'language_id')
    filter_horizontal = ('m2mcategory', )
    resource_class = TopicResource

    fieldsets = (
        (None, {
            'fields': ('title', 'm2mcategory')
        }),
        ('VB Details', {
            'fields': ('language_id', 'media_duration'),
        }),
        ('Counts', {
            'fields': (('view_count', 'comment_count'), ('total_share_count', 'share_count'), 'likes_count'),
        }),
        ('Transcode Options', {
            'classes': ('collapse',),
            'fields': ('backup_url', ('is_transcoded', 'is_transcoded_error'), 'transcode_job_id', \
                        'transcode_dump', 'transcode_status_dump'),
        }),
    )

    actions = ['remove_selected', 'remove_from_monetization', 'restore_selected', 'add_monetization']
    def remove_selected(self, request, queryset):
        for each_obj in queryset:
            if not each_obj.is_removed:
                each_obj.delete()
    remove_selected.short_description = "Delete selected Records!"

    def remove_from_monetization(self, request, queryset):
        for each_obj in queryset:
            if each_obj.is_monetized:
                each_obj.no_monetization()
    remove_from_monetization.short_description = "Remove from Monetization!"

    def restore_selected(self, request, queryset):
        for each_obj in queryset:
            if each_obj.is_removed:
                each_obj.restore()
    restore_selected.short_description = "Restore selected Records (No Monetization)!"

    def add_monetization(self, request, queryset):
        for each_obj in queryset:
            if not each_obj.is_monetized:
                each_obj.add_monetization()
    add_monetization.short_description = "Restore & Add to Monetization!"

    # def remove_from_monetization(self, request, queryset):
    #     for each_obj in queryset:
    #         if each_obj.is_monetized:
    #             each_obj.no_monetization()
    # remove_from_monetization.short_description = "Remove from Monetization!"

    def get_actions(self, request):
        actions = super(TopicAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        if 'language_id' in form.changed_data and obj.is_monetized:
            # print form.initial['language_id'],obj.language_id,"####",change
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

