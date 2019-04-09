# from utils import admin_all
from forum.topic.models import *
from django.contrib import admin
# admin_all(models)

class TopicAdmin(admin.ModelAdmin):
	search_fields = ('title', )
	list_filter = ('language_id', 'category', 'is_media')
	list_display = ('id', 'title', 'user', 'category', 'is_media', )
	list_editable = ('title', )
admin.site.register(Topic, TopicAdmin)