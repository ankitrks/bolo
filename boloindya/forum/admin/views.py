# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from django.http import JsonResponse

import spirit
from ..category.models import Category
from ..comment.flag.models import CommentFlag
from ..comment.like.models import CommentLike
from ..comment.models import Comment
from ..topic.models import Topic
from ..user.models import UserProfile
from ..core.utils.decorators import administrator_required
from .forms import BasicConfigForm

User = get_user_model()


@administrator_required
def config_basic(request):

    if request.method == 'POST':
        form = BasicConfigForm(data=request.POST)

        if form.is_valid():
            form.save()
            messages.info(request, _("Settings updated!"))
            return redirect(request.GET.get("next", request.get_full_path()))
    else:
        form = BasicConfigForm()

    context = {'form': form, }

    return render(request, 'spirit/admin/config_basic.html', context)


@administrator_required
def dashboard(request):
    # Strongly inaccurate counters below...
    context = {
        'version': spirit.__version__,
        'category_count': Category.objects.all().count() - 1,  # - private
        'topics_count': Topic.objects.all().count(),
        'comments_count': Comment.objects.all().count(),
        'users_count': User.objects.all().count(),
        'flags_count': CommentFlag.objects.filter(is_closed=False).count(),
        'likes_count': CommentLike.objects.all().count()
    }

    return render(request, 'spirit/admin/dashboard.html', context)

@administrator_required
def block_user(request, user_id, action):
    print("request action ", action)
    if not request.method == 'POST':
        return JsonResponse({}, status=401)

    userprofile = UserProfile.objects.get(id=user_id)
    user = userprofile.user

    delete_count = 0

    if action == 'block':
        user.is_active = False
        user.save()

    elif action == 'unblock':
        user.is_active = True
        user.save()

    elif action == 'delete_comments':
        for comment in user.st_comments.filter(is_removed=False):
            comment.delete()
            delete_count += 1

    elif action == 'delete_videos':
        for topic in user.st_topics.filter(is_removed=False):
            topic.delete(user.is_active)
            delete_count += 1


    return JsonResponse({'delete_count': delete_count}, status=200)

