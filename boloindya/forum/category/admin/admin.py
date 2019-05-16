# from utils import admin_all
from forum.comment.models import *
from django.contrib import admin
# admin_all(models)
from datetime import datetime,timedelta

class CommentAdmin(admin.ModelAdmin):
	search_fields = ('topic', )
	list_filter = ('is_media', 'is_audio', 'language_id', 'topic__category')
	list_display = ('id', 'topic', 'user', 'is_media', 'is_audio', 'language_id')
	def changelist_view(self, request, extra_context=None):
		search_fields = ('topic', )
		list_filter = ('is_media', 'is_audio', 'language_id', 'topic__category')
		list_display = ('id', 'topic', 'user', 'is_media', 'is_audio', 'language_id')
		ChangeList = self.get_changelist(request)
		cl = ChangeList(request, self.model, list_display,self.list_display_links, list_filter, self.date_hierarchy,search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all, self.list_editable, self)
		qs=cl.get_queryset(request)
		extra_context = extra_context or {}
		audio_duration = get_audio_duration(qs)
		video_duration = get_video_duration(qs)
		extra_context['audio_duration'] = audio_duration
		extra_context['video_duration'] = video_duration
		return super(CommentAdmin, self).changelist_view(request, extra_context=extra_context)
admin.site.register(Comment, CommentAdmin)


def get_audio_duration(qs):
	all_audio_answer = qs.filter(is_media=True,is_audio = True)
	duration =datetime.strptime('00:00', '%M:%S')
	for each_audio in all_audio_answer:
		# print each_audio.media_duration,"maaz"
		if each_audio.media_duration and not each_audio.media_duration =='00:00':
			# print each_audio.media_duration,'a'
			datetime_object = datetime.strptime(each_audio.media_duration, '%M:%S')
			a = timedelta(minutes=datetime_object.minute, seconds=datetime_object.second)
			# b = timedelta(minutes=duration.minute, seconds=duration.second)
			# print a,duration
			duration=a+duration
			# print duration, type(duration)
			# duration = timedelta(hours = b.hour,minutes=b.minute, seconds=b.second)
		else:
			pass
	return duration


def get_video_duration(qs):
	all_video_answer = qs.filter(is_media=True,is_audio = False)
	duration =datetime.strptime('00:00', '%M:%S')
	for each_video in all_video_answer:
		# print each_video.media_duration
		if each_video.media_duration and not each_video.media_duration =='00:00':
			# print each_video.media_duration,'b'
			datetime_object = datetime.strptime(each_video.media_duration, '%M:%S')
			a = timedelta(minutes=datetime_object.minute, seconds=datetime_object.second)
			# b = timedelta(minutes=duration.minute, seconds=duration.second)
			# print a,duration
			duration= a + duration
			# print duration,type(duration)
			# duration = timedelta(hours = b.hour,minutes=b.minute, seconds=b.second)
		else:
			pass
	return duration

