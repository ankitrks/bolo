from django.db import models
from django.db.models.signals import post_save, post_delete
from datetime import datetime

class LastModifiedQueryset(models.query.QuerySet):
    def update(self, *args, **kwargs):
        if not kwargs.has_key('vb_score'):
            kwargs['last_modified'] = datetime.now()
        try:
            for each_instance in self:
                try:
                    if each_instance.is_removed:
                        post_delete.send(sender=type(each_instance), instance=each_instance, created=False)
                    else:
                        post_save.send(sender=type(each_instance), instance=each_instance, created=False)
                except Exception as e:
                    print e
        except Exception as e:
            print e
        return super(LastModifiedQueryset,self).update(*args, **kwargs)
