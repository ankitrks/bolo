from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .emails import send_email_to_topic_people
from forum.comment.models import Comment


@receiver(post_save, sender=Comment)
def post_comment_save(sender, instance, created, **kwargs):
    # if created:
    #     # Need to send emails to topic people
    #     send_email_to_topic_people(instance, created)
    #     # need to update *comment_count of topic if the comment is created
    #     instance.topic.increase_comment_count()
    pass


@receiver(post_delete, sender=Comment)
def post_comment_delete(sender, instance, using, **kwargs):
    # # Need to update *comment_count of the comment's topic
    # instance.topic.decrease_comment_count()
    pass
