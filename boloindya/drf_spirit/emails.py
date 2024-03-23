from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _


def send_mass_mail(messages):
    connection = mail.get_connection()
    connection.send_messages(messages)


def send_email_to_topic_people(instance, created):
    emails = list(instance.topic.comments.exclude(user=instance.user)
                          .values_list("user__email", flat=True).distinct().iterator())
    # append the topic creator email
    emails.append(instance.topic.user.email)
    # remove duplicates if the topic creator also comments
    emails = set(emails)
    subject = _("A new comment has been made")
    html_template = "drf_spirit/new_comment.html"
    html_message = render_to_string(html_template)
    messages = []
    for email in emails:
        msg = EmailMultiAlternatives(subject=subject, to=[email])
        msg.attach_alternative(html_message, "text/html")
        messages.append(msg)

    send_mass_mail(messages)
