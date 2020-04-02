# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from .models import UserProfile,ReferralCode
from forum.userkyc.models import UserKYC
from drf_spirit.utils import generate_refer_earn_code

User = get_user_model()


def update_or_create_user_profile(sender, instance, created, **kwargs):
    user = instance

    if created:
        UserProfile.objects.create(user=user,slug=user.username)
        UserKYC.objects.create(user=user)
        ReferralCode.objects.create(for_user=user,code=generate_refer_earn_code(),purpose='refer_n_earn',is_refer_earn_code=True)

    else:
        user.st.save()

post_save.connect(update_or_create_user_profile, sender=User, dispatch_uid=__name__)