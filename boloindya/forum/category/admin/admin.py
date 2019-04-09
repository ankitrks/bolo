# from utils import admin_all
from forum.comment.models import *
from django.contrib import admin
# admin_all(models)

class CommentAdmin(admin.ModelAdmin):
	search_fields = ('topic', )
	list_filter = ('is_media', 'is_audio', 'language_id', 'topic')
	list_display = ('id', 'topic', 'user', 'is_media', 'is_audio', 'language_id')
admin.site.register(Comment, CommentAdmin)