# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponsePermanentRedirect

from djconfig import config
from django.conf import settings

from ..core.utils.paginator import paginate, yt_paginate
from ..core.utils.ratelimit.decorators import ratelimit
from ..category.models import Category
from ..comment.models import MOVED
from ..comment.forms import CommentForm
from ..comment.utils import comment_posted
from ..comment.models import Comment
from .models import Topic
from .forms import TopicForm
from . import utils


@login_required
@ratelimit(rate='1/10s')
def publish(request, category_id=None):
    if category_id:
        get_object_or_404(
            Category.objects.visible(),
            pk=category_id)

    user = request.user

    if request.method == 'POST':
        form = TopicForm(user=user, data=request.POST)
        cform = CommentForm(user=user, data=request.POST)

        if (all([form.is_valid(), cform.is_valid()]) and
                not request.is_limited()):
            if not user.st.update_post_hash(form.get_topic_hash()):
                return redirect(
                    request.POST.get('next', None) or
                    form.get_category().get_absolute_url())

            # wrap in transaction.atomic?
            topic = form.save()
            cform.topic = topic
            comment = cform.save()
            comment_posted(comment=comment, mentions=cform.mentions)
            return redirect(topic.get_absolute_url())
    else:
        if not category_id:
            category_id = 1
        form = TopicForm(user=user, initial={'category': category_id})
        cform = CommentForm()

    context = {
        'form': form,
        'cform': cform,
    }

    return render(request, 'spirit/topic/publish.html', context)


@login_required
def update(request, pk):
    topic = Topic.objects.for_update_or_404(pk, request.user)

    if request.method == 'POST':
        form = TopicForm(user=request.user, data=request.POST, instance=topic)
        category_id = topic.category_id

        if form.is_valid():
            topic = form.save()

            if topic.category_id != category_id:
                Comment.create_moderation_action(user=request.user, topic=topic, action=MOVED)

            return redirect(request.POST.get('next', topic.get_absolute_url()))
    else:
        form = TopicForm(user=request.user, instance=topic)

    context = {
        'form': form,
    }

    return render(request, 'spirit/topic/update.html', context)


def detail(request, pk, slug):
    categories = Category.objects \
        .visible() \
        .parents()    

    topics = Topic.objects.all()[:10]

    topic = get_object_or_404(Topic.objects.visible(),pk=pk)


    context = {
        'categories': categories,
        'topics': topics,
        'is_single_topic': pk,
        'single_topic': topic
    }

    return render(request, 'spirit/topic/_ques_and_ans_index.html', context)


def index_active(request):

    categories = Category.objects \
        .visible() \
        .parents()

    category = get_object_or_404(Category.objects.visible(),
                                 pk=5)

    subcategories = Category.objects \
        .visible() \
        .children(parent=category)

    sub_category = []
    topics = []

    if len(subcategories) > 0:
        sub_category = get_object_or_404(Category.objects.visible(), pk=subcategories[0].pk)
        topics = sub_category.category_topics.all()[0:8]


    current_index = 0

    for index, category_each in enumerate(categories):
        if category_each.id == category.id:
            current_index = index

    context = {
        'categories': categories,
        'category': category,
        'subcategories': subcategories,
        'sub_category': sub_category,
        'topics': topics,
        'current_index': current_index
    }

    return render(request, 'spirit/topic/_index.html', context)

def ques_ans_index(request,category_id=None, is_single_topic=0):
    
    categories = Category.objects \
        .visible() \
        .parents()    

    topics = Topic.objects.all()[:10]

    topic = {}
    if(is_single_topic != 0):
        topic = get_object_or_404(Topic.objects.visible(),pk=is_single_topic)

    if(category_id != None):
        category = get_object_or_404(Category.objects.visible(),pk=category_id)
        topics = category.category_topics.all()[0:10]                         

    context = {
        'categories': categories,
        'topics': topics,
        'is_single_topic': is_single_topic,
        'single_topic': topic
    }

    return render(request, 'spirit/topic/_ques_and_ans_index.html', context)
