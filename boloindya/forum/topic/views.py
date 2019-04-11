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
from django.template.loader import render_to_string
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
# from utils import convert_speech_to_text

import io
import os
#import wget
import copy
import subprocess
from datetime import datetime
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
def convert_speech_to_text(blob_url):
    fname = datetime.now().strftime('%s')
    wget_command = "python -m wget -o /tmp/" + fname + " " + blob_url
    subprocess.call(wget_command, shell=True)

    command = "ffmpeg -i /tmp/" + fname + " -ab 160k -ac 1 -ar 44100 -vn /tmp/" + fname + ".wav"
    subprocess.call(command, shell=True)
    client = speech.SpeechClient()

    with io.open('/tmp/' + fname + '.wav', 'rb') as audio_file:
      content = audio_file.read()
      audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig( encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16, \
                    sample_rate_hertz=44100, language_code='en-US')
    response = client.recognize(config, audio)

    return_str = ''
    for result in response.results:
        print ('{}'.format(result.alternatives[0].transcript))
        return_str += ('{}'.format(result.alternatives[0].transcript))
        # print('Transcript: {}'.format(result.alternatives[0].transcript))
    f1_rm = "rm -rf /tmp/" + fname
    f2_rm = "rm -rf /tmp/" + fname + ".wav"
    subprocess.call(f1_rm, shell=True)
    subprocess.call(f2_rm, shell=True)

    return return_str

@login_required
@ratelimit(rate='1/10s')
def publish(request, category_id=None):
    if category_id:
        get_object_or_404(
            Category.objects.visible(),
            pk=category_id)
            
    user = request.user

    if request.method == 'POST':
        title = ''
        if request.POST.get('question_audio'):
            title = convert_speech_to_text( request.POST.get('question_audio') )
        if request.POST.get('question_video'):
            title = convert_speech_to_text( request.POST.get('question_video') )
        post_data = copy.deepcopy(request.POST)
        if title:
            post_data['title'] = title
        form = TopicForm(user=user, data=post_data)
        cform = CommentForm(user=user, data=request.POST)
        if (all([form.is_valid(), cform.is_valid()]) and
                not request.is_limited()):
            if not user.st.update_post_hash(form.get_topic_hash()):
                return redirect(
                    request.POST.get('next', None) or
                    form.get_category().get_absolute_url())

            # wrap in transaction.atomic?
            topic = form.save()
            if title:
                topic.title = title
            if request.POST.get('question_audio'):
                topic.question_audio = request.POST.get('question_audio')
            if request.POST.get('question_video'):
                topic.question_audio = request.POST.get('question_video')
            topic.save()
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
def search(request):
    category_id = None
    lid = request.GET.get('lid', 2)
    categories = Category.objects \
        .visible() \
        .parents()   

    # topic = {}
    # if is_single_topic not in [0, '0']:
    #     print 'Yoo'
    #     topic = get_object_or_404(Topic.objects.visible(),pk=is_single_topic)

    if(category_id != None):
        category = get_object_or_404(Category.objects.visible(),pk=category_id)                  

    topics = []
    search_term = request.GET.get('q')
    if search_term:
        topics = Topic.objects.filter(title__icontains = search_term)

    context = {
        'categories': categories,
        'topics': topics,
        'category_id' : category_id,
        'lid': lid
        # 'is_single_topic': is_single_topic,
        # 'single_topic': topic
    }
    return render(request, 'spirit/topic/_ques_and_ans_index.html', context)

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

    topics = Topic.objects.filter(id = pk)#.all()[:10]

    # topic = get_object_or_404(Topic.objects.visible(),pk=pk)


    context = {
        'categories': categories,
        'topics': topics,
        'is_single_topic': pk,
        # 'single_topic': topic
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

    return render(request, 'spirit/topic/_home.html', context)


def index_videos(request):

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

def get_topics_feed(request):
    pageno = request.GET.get('pageno', None)
    topic_list = Topic.objects.filter(language_id = request.GET.get('lid', 1))
    paginator = Paginator(topic_list, 10) # Show 25 contacts per page

    topics = paginator.page(pageno)  

    if(request.GET.get('category_id', None) != 'None'):
        category = get_object_or_404(Category.objects.visible(),pk=int((request.GET.get('category_id', 14))))
        topics = category.category_topics.all()[0:10]                         
        paginator = Paginator(topic_list, 10) # Show 25 contacts per page

        page = 1
        topics = paginator.page(page) 

    data = render_to_string('spirit/topic/_single_topic.html', {'topics': topics})
    return JsonResponse(data, safe=False)


def ques_ans_index(request,category_id=None):#, is_single_topic=0):
    lid = request.GET.get('lid', 2)
    categories = Category.objects \
        .visible() \
        .parents()    

    topic_list = Topic.objects.filter(language_id = lid)
    paginator = Paginator(topic_list, 10) # Show 25 contacts per page

    page = 1
    topics = paginator.page(page)

    # topic = {}
    # if is_single_topic not in [0, '0']:
    #     print 'Yoo'
    #     topic = get_object_or_404(Topic.objects.visible(),pk=is_single_topic)

    if(category_id != None):
        category = get_object_or_404(Category.objects.visible(),pk=category_id)
        topic_list = category.category_topics.all()    
        paginator = Paginator(topic_list, 10) # Show 25 contacts per page

        page = 1
        topics = paginator.page(page)                    

    context = {
        'categories': categories,
        'topics': topics,
        'category_id' : category_id,
        'lid': lid
        # 'is_single_topic': is_single_topic,
        # 'single_topic': topic
    }

    return render(request, 'spirit/topic/_ques_and_ans_index.html', context)


def index(request):
    return render(request, 'spirit/topic/_home.html')


def new_home(request):
    return render(request, 'spirit/topic/_new_home.html')

def robotstext(request):
    return render(request, 'spirit/topic/robots.txt') 

def robotstext(request):
    return render(request, 'spirit/topic/sitemap.xml')       

