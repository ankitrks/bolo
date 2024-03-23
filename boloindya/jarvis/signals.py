from __future__ import unicode_literals
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Report
from tasks import send_report_mail

@receiver(post_save, sender=Report)
def reprot_created(sender, instance, created, **kwargs):
    if created:
        send_report_mail.delay(instance.id)