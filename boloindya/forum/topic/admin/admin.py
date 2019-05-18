# from utils import admin_all
from forum.topic.models import *
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from forum.topic.models import Topic,Notification
# admin_all(models)

class TopicResource(resources.ModelResource):

	class Meta:
		model = Topic
		skip_unchanged = True
		report_skipped = True
		fields = ( 'title', 'category','language_id')


class TopicAdmin(ImportExportModelAdmin):
	search_fields = ('title', )
	list_filter = ('language_id', 'category', 'is_media')
	list_display = ('id', 'title', 'user', 'category', 'is_media','comments','audio_duration' ,'video_duration',)
	list_editable = ('title', )
	resource_class = TopicResource
	# def comment_count(self, obj):
	# 	url = '/forum_comment/comment/?topic_id='+obj.id
	# 	print url, obj.comment_count
	# 	return '<a href="%s" target="_blank">%s</a>' % (url, obj.comment_count)
	# comment_count.allow_tags = True
	# comment_count.short_description = 'Click to open the detail list of answers'

class NotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'for_user', 'user', 'notification_type')


admin.site.register(Topic, TopicAdmin)
admin.site.register(Notification,NotificationAdmin)




