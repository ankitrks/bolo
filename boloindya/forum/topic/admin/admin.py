# from utils import admin_all
from forum.topic.models import *
from django.contrib import admin
from drf_spirit.views import check_hashtag
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from forum.topic.models import Topic, Notification, ShareTopic, CricketMatch, Poll, Choice, Voting, Leaderboard,\
 TongueTwister, BoloActionHistory, HashtagViewCounter
from forum.category.models import Category
from forum.topic.models import Topic, Notification, ShareTopic, CricketMatch, Poll, Choice, Voting, Leaderboard, \
        TongueTwister, BoloActionHistory, language_options,JobOpening,JobRequest,RankingWeight
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from datetime import datetime,timedelta
from forum.user.utils.bolo_redis import update_profile_counter
from tasks import update_profile_counter_task
from django.db import connections
from haystack.query import SearchQuerySet, SQ
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.urlresolvers import reverse
import copy

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
    is_boosted = forms.BooleanField(required = False)
    boosted_till = forms.IntegerField(required = False)
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
import newrelic.agent

# newrelic.agent.initialize()
application = newrelic.agent.register_application()


class TopicChangeList(ChangeList):
    def __init__(self, request, model, list_display, list_display_links,
            list_filter, date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, model_admin):

        # super(TopicChangeList, self).__init__(request, model, list_display, list_display_links,
        #     list_filter, date_hierarchy, search_fields, list_select_related,
        #     list_per_page, list_max_show_all, list_editable, model_admin)
        # action_checkbox

        newrelic.agent.set_transaction_name("/Admin/Topic/GET", "Admin Panel")

        self.list_display = ('vb_list', 'id', 'title', 'name', 'duration', 'show_thumbnail', 'language_id', 'playtime', 'imp_count',\
            'date', 'is_moderated', 'is_removed', 'is_pubsub_popular_push', 'is_boosted', 'boosted_till', 'm2mcategory') #is_popular
        self.list_display_links = ['id']
        self.list_editable = ('title', 'language_id', 'm2mcategory', 'is_pubsub_popular_push', 'is_removed', \
                'is_moderated','is_boosted','boosted_till')
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
        self.show_full_result_count = False

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


    def get_results(self, request):
        paginator = self.model_admin.get_paginator(request, self.queryset, self.list_per_page)
        # Get the number of objects, with admin filters applied.
        count = None
        try:
            with connections['default'].cursor() as cr:
                sql = self.queryset.query.sql_with_params()
                cr.execute("analyze forum_topic_topic; SELECT count_estimate(%s)", [cr.mogrify(sql[0], sql[1])])

                count = cr.fetchall()[0][0]
        except Exception as e:
            print "While geeting approx count", str(e)

        if count and count > 5000:
            print "from apporx"
            paginator.count = count

        result_count = paginator.count

        print "result_count", result_count
        
        # Get the total number of objects, with no admin filters applied.
        if self.model_admin.show_full_result_count:
            full_result_count = self.root_queryset.count()
        else:
            full_result_count = None
        can_show_all = result_count <= self.list_max_show_all
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.queryset._clone()
        else:
            try:
                result_list = paginator.page(self.page_num + 1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.show_full_result_count = self.model_admin.show_full_result_count
        # Admin actions are shown if there is at least one entry
        # or if entries are not counted because show_full_result_count is disabled
        self.show_admin_actions = not self.show_full_result_count or bool(full_result_count)
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator

from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter
class ModeratedFilter(SimpleListFilter):
    title = 'Moderated by'
    parameter_name = 'last_moderated_by__id'
    def lookups(self, request, model_admin):
        return list(User.objects.filter(Q(is_staff = True) | Q(is_superuser = True)).values_list('id', 'username'))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(last_moderated_by__id=self.value())
        return queryset

class UserTypeFilter(SimpleListFilter):
    title = 'User type'
    parameter_name = 'user__st'
    def lookups(self, request, model_admin):
        return (
            ('1', 'Superstar'),
            ('1', 'Popular'),
            ('1', 'Business'),
        )

    def queryset(self, request, queryset):
        if self.value() and self.value().lower() == 'superstar':
            self.parameter_name = 'user__st__is_superstar'
            return queryset.filter(user__st__is_superstar = True)
        elif self.value() and self.value().lower() == 'popular':
            self.parameter_name = 'user__st__is_popular'
            return queryset.filter(user__st__is_popular = True)
        elif self.value() and self.value().lower() == 'business':
            self.parameter_name = 'user__st__is_business'
            return queryset.filter(user__st__is_business = True)  
        return queryset

class MultiSelectFilter(admin.SimpleListFilter):

    def choices(self, changelist):
        if self.value():
            values_list = self.value().split(',')
        else:
            values_list = []
        for lookup, title in self.lookup_choices:
            yield {
                'selected': force_text(lookup) in values_list,
                'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

class CategoryMultiSelectFilter(MultiSelectFilter):
    title = 'Categories'
    template = 'spirit/topic/admin/category_multiselect_filter.html'

    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return tuple([(category.id, category.title) for category in Category.objects.all()])

    def queryset(self, request, queryset):
        if self.value():
            categories = Category.objects.filter(id__in=self.value().split(','))
            return queryset.filter(m2mcategory__in=categories)

        return queryset


class LanguageMultiSelectFilter(MultiSelectFilter):
    title = 'Languages'
    template = 'spirit/topic/admin/language_multiselect_filter.html'

    parameter_name = 'language'

    def lookups(self, request, model_admin):
        return tuple([(language[0], language[1]) for language in settings.LANGUAGE_OPTIONS])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(language_id__in=self.value().split(','))

        return queryset


class TopicAdmin(admin.ModelAdmin): # to enable import/export, use "ImportExportModelAdmin" NOT "admin.ModelAdmin"
    # ordering = ['is_vb', '-id']
    ordering = ('-id',)
    list_per_page = 20
    search_fields = ('title', 'user__username', 'user__st__name', )
    list_filter = (('date', DateRangeFilter), 'is_moderated', 'is_monetized', 'is_removed', \
            'is_popular', 'is_boosted', 'is_reported', ModeratedFilter, UserTypeFilter, CategoryMultiSelectFilter,\
            LanguageMultiSelectFilter, 'user__st__is_superstar', 'user__st__is_popular', 'user__st__is_business')
    
    show_full_result_count = False
    # filter_horizontal = ('m2mcategory', )

    fieldsets = (
        # (None, {
        #     'fields': ('title', 'm2mcategory')
        # }),
        ('VB Details', {
            'fields': ('language_id', 'media_duration','is_pubsub_popular_push','is_boosted','boosted_till'),
        }),
        ('Counts', {
            'fields': (('view_count', 'comment_count'), ('total_share_count', 'share_count'), ('likes_count', 'vb_score')),
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

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "last_moderated_by":
    #         kwargs["queryset"] = User.objects.filter(Q(is_staff = True) | Q(is_superuser = True))
    #     return super(TopicAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changelist(self, request, **kwargs):
        return TopicChangeList

    def get_changelist_form(self, request, **kwargs):
        return TopicChangeListForm

    def playtime(self, obj):
        return obj.playtime()
    playtime.short_description = "playtime"
    playtime.admin_order_field = 'vb_playtime'

    def duration(self, obj):
        return obj.duration()
    duration.short_description = "duration"
    duration.admin_order_field = 'media_duration'

    def vb_list(self, obj):
        video_url = reverse('spirit:share_vb_page', kwargs={'user_id': str(obj.user_id),
                        'poll_id': str(obj.id), 'slug': obj.slug or 'a'})
        return '<a href="?user_id=' + str(obj.user.id) +'" data-video_url="'+video_url+'" target="_blank" style="background-position: \
                0 -834px;background-image: url(/static/grappelli/images/icons-small-sf6f04fa616.png);\
                background-repeat: no-repeat;height: 20px;display: block;"></a>'
    vb_list.allow_tags = True
    vb_list.short_description = "VB"
    
    def show_thumbnail(self, obj):
        if obj.question_image:
            return """<div style="background: url('""" + obj.question_image + """');width: 100%;
                    height: 56px;background-size: 100%;"></div>"""
        return '<div style="width: 30px;height: 30px;"></div>'
    show_thumbnail.allow_tags = True
    show_thumbnail.short_description = "IMG"

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

    # def get_search_results(self, request, queryset, search_term):
    #     final_search_term = search_term.replace('h:', '').replace('n:', '')
    #     queryset, use_distinct = super(TopicAdmin, self).get_search_results(request, queryset, final_search_term)
    #     if search_term:
    #         if search_term.startswith('h:'):
    #             queryset = queryset.filter(hash_tags__hash_tag__iexact = search_term.replace('h:', ''))
    #         if search_term.startswith('n:'):
    #             queryset = queryset.filter(title__icontains = search_term.replace('n:', '')).exclude(hash_tags__hash_tag__icontains = search_term.replace('n:', ''))
    #     return queryset, use_distinct

    def get_search_results(self, request, queryset, search_term):
        final_search_term = search_term.replace('h:', '').replace('n:', '')

        if search_term.startswith('h:'):
            queryset = queryset.filter(hash_tags__hash_tag__iexact = search_term.replace('h:', ''))
        elif search_term.startswith('n:'):
            queryset = queryset.filter(title__icontains = search_term.replace('n:', '')).exclude(hash_tags__hash_tag__icontains = search_term.replace('n:', ''))
        elif search_term:
            user_sqs = SearchQuerySet().models(UserProfile).raw_search(search_term) \
                                .order_by('-is_superstar').order_by('-is_popular').values('id', 'is_superstar',
                                    'is_popular', 'name')[:100]
            topic_sqs = SearchQuerySet().models(Topic).raw_search(search_term).values('id')[:1000]

            self.sqs_result = []
            self.sqs_result_dict = {}
            id_list = []
            user_id_list = []
            for item in topic_sqs:
                if not type(item.get('id')) in (str, unicode):
                    continue

                id_list.append(item.get('id').split('.')[-1])

            for item in user_sqs:
                if not type(item.get('id')) in (str, unicode):
                    continue

                user_id_list.append(item.get('id').split('.')[-1])

            if user_id_list:
                with connections['default'].cursor() as cr:
                    cr.execute("""
                        SELECT topic.id
                        FROM forum_topic_topic topic
                        INNER JOIN forum_user_userprofile profile on profile.user_id = topic.user_id
                        WHERE profile.id in %s
                    """, [tuple(user_id_list)])

                    id_list += [row[0] for row in cr.fetchall()]

            queryset = queryset.filter(id__in=id_list)

        queryset.select_related('user', 'user__userprofile')
        return queryset, False

    def save_model(self, request, obj, form, change):
        newrelic.agent.set_transaction_name("/Admin/Topic/POST", "Admin Panel")
        if 'title' in form.changed_data:
            obj.title = form.cleaned_data['title']
        if 'language_id' in form.changed_data:
            obj.language_id = form.cleaned_data['language_id']
        if 'is_pubsub_popular_push' in form.changed_data:
            obj.is_pubsub_popular_push = form.cleaned_data['is_pubsub_popular_push']
            obj.is_popular = form.cleaned_data['is_pubsub_popular_push']
            obj.popular_boosted = form.cleaned_data['is_pubsub_popular_push']
            if obj.popular_boosted:
                obj.popular_boosted_time = datetime.now()

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
                update_profile_counter_task.delay(obj.user_id,'video_count',1, False)
            else:
                obj.restore()
                update_profile_counter_task.delay(obj.user_id,'video_count',1, True)
        
        if 'is_boosted' in form.changed_data or 'boosted_till' in form.changed_data:
            if 'is_boosted' in form.changed_data:
                obj.is_boosted = form.cleaned_data['is_boosted']

            if 'boosted_till' in form.changed_data:
                obj.boosted_till = form.cleaned_data['boosted_till']
                if obj.boosted_till:
                    obj.boosted_start_time = datetime.now()
                    obj.boosted_end_time = datetime.now()+timedelta(hours=obj.boosted_till)

        if 'title' in form.changed_data:
            tag_list = obj.title.split()
            hash_tag = copy.deepcopy(tag_list)
            if tag_list:
                for index, value in enumerate(tag_list):
                    if value.startswith("#"):
                        tag_list[index]='<a href="/get_challenge_details/?ChallengeHash='+value.strip('#')+'">'+value+'</a>'
                title = " ".join(tag_list)
                obj.title = title[0].upper()+title[1:]
                obj.first_hash_tag = None
                hash_tags = obj.hash_tags.all()
                for each_hashtag in hash_tags:
                    each_hashtag.hash_counter = F('hash_counter')-1
                    obj.hash_tags.remove(each_hashtag)
                    each_hashtag.save()
                first_hash_tag = False
                for index, value in enumerate(hash_tag):
                    if value.startswith("#"):
                        # tag,is_created = TongueTwister.objects.get_or_create(hash_tag__iexact=value.strip('#'))
                        tag = TongueTwister.objects.using('default').filter(hash_tag__iexact=value.strip('#'))
                        if tag.count():
                            tag.update(hash_counter = F('hash_counter')+1)
                            tag = tag[0]
                        else:
                            tag = TongueTwister.objects.create(hash_tag=value.strip('#'))
                        obj.hash_tags.add(tag)
                        if not first_hash_tag:
                            obj.first_hash_tag = tag
                            first_hash_tag = True
        obj.save()
        if 'is_boosted' in form.changed_data or 'boosted_till' in form.changed_data or 'is_pubsub_popular_push' in form.changed_data:
            obj.calculate_vb_score()

        if 'language_id' in form.changed_data and obj.is_monetized:
            if form.initial['language_id'] == '1':
                userprofile = UserProfile.objects.filter(user = obj.user)
                reduce_bolo_score(obj.user.id, 'create_topic_en', obj, 'no_monetize')
                obj.add_monetization()
            elif obj.language_id == '1':
                userprofile = UserProfile.objects.filter(user = obj.user)
                reduce_bolo_score(obj.user.id, 'create_topic', obj, 'no_monetize')
                obj.add_monetization()

        if form.changed_data and request.user.is_staff:
            obj.last_moderated_by = request.user

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
# admin.site.register(BoloActionHistory, BoloActionHistoryAdmin)

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

class JonOpeningAdmin(admin.ModelAdmin):
    list_display = ('title', 'expiry_date', 'publish_status')
    def get_actions(self, request):
        #Disable delete
        actions = super(JonOpeningAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
    def has_delete_permission(self, request, obj=None):
        #Disable delete
        return False

class JobRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile')

class TongueTwisterForm(forms.ModelForm):
    languages = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          choices=language_options)
    class Meta:
        fields = ('__all__')
        model = TongueTwister

class TongueTwisterAdmin(admin.ModelAdmin):
    list_display = ('hash_tag', 'is_blocked', 'is_popular', 'order', 'popular_date', 'languages')
    list_editable = ('is_blocked', 'is_popular', 'order', 'popular_date', 'languages')
    list_filter = ('is_blocked', 'is_popular', )
    search_fields = ('hash_tag',)
    form = TongueTwisterForm

class RankingWeightAdmin(admin.ModelAdmin):
    list_display = ('features','weight',)
    search_fields = ('features',)

class HashtagViewCounterAdmin(admin.ModelAdmin):
    list_display = ('hashtag','language', 'view_count', 'video_count')
    search_fields = ('hashtag',)

admin.site.register(RankingWeight,RankingWeightAdmin)
admin.site.register(Poll, PollAdmin)

admin.site.register(Topic, TopicAdmin)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(ShareTopic,ShareTopicAdmin)
admin.site.register(Voting)
admin.site.register(Leaderboard)
# admin.site.register(VBseen)
admin.site.register(TongueTwister,TongueTwisterAdmin)
admin.site.register(JobOpening,JonOpeningAdmin)
admin.site.register(JobRequest,JobRequestAdmin)
admin.site.register(HashtagViewCounter, HashtagViewCounterAdmin)


