from django.db import models
from django.db.models.signals import post_save
from datetime import datetime


class UserProfileQueryset(models.query.QuerySet):
    def update(self, *args, **kwargs):
        try:
            if len(self) == 1:
            	for each_instance in self:
                	post_save.send(sender=type(each_instance), instance=each_instance, created=False)
        except Exception as e:
            print e
        return super(UserProfileQueryset,self).update(*args, **kwargs)
