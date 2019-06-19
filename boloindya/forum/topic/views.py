# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponsePermanentRedirect

from djconfig import config
from django.conf import settings

from django.contrib.auth.models import User

from ..core.utils.paginator import paginate, yt_paginate
from ..core.utils.ratelimit.decorators import ratelimit
from ..category.models import Category
from ..comment.models import MOVED
from ..comment.forms import CommentForm
from ..comment.utils import comment_posted
from ..comment.models import Comment
from .models import Topic,CricketMatch,Poll,Voting,Choice
from .forms import TopicForm
from . import utils
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponse
import json
from django.core.paginator import Paginator
from forum.topic.models import Like
from django.db.models import F,Q

# Required for speech to text...
import io
import os
import urllib2
import copy
import subprocess
from datetime import datetime
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


from forum.user.models import UserProfile

def get_current_language(request):
    return request.COOKIES.get('language', request.GET.get('lid', 2))

def get_language_code(request):
    language_code_map = {'1' : 'en-US', '2' : 'hi', '3' : 'ta', '4' : 'te', 1 : 'en-US', 2 : 'hi', 3 : 'ta', 4 : 'te'}
    return language_code_map[get_current_language(request)]

def convert_speech_to_text(request, blob_url):
    try:
        fname = datetime.now().strftime('%s')
        file_response = urllib2.urlopen(blob_url)
        file_obj = open("/tmp/" + fname, 'w')
        file_obj.write(file_response.read())
        file_obj.close()

        command = "ffmpeg -i /tmp/" + fname + " -ab 160k -ac 1 -ar 44100 -vn /tmp/" + fname + ".wav"
        subprocess.call(command, shell=True)
        client = speech.SpeechClient()

        with io.open('/tmp/' + fname + '.wav', 'rb') as audio_file:
          content = audio_file.read()
          audio = types.RecognitionAudio(content=content)

        config = types.RecognitionConfig( encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16, \
                        sample_rate_hertz=44100, language_code=get_language_code(request))
        response = client.recognize(config, audio)

        return_str = ''
        for result in response.results:
            return_str += ('{}'.format(result.alternatives[0].transcript))
        f1_rm = "rm -rf /tmp/" + fname
        f2_rm = "rm -rf /tmp/" + fname + ".wav"
        subprocess.call(f1_rm, shell=True)
        subprocess.call(f2_rm, shell=True)
    except Exception as e:
        return_str = ' - - '
    return return_str

@login_required
@ratelimit(rate='1/10s')
def publish(request, category_id=None):
    if category_id:
        get_object_or_404(Category.objects.visible(), pk=category_id)
    
    user = request.user
    if request.method == 'POST':
        title = ''
        if request.POST.get('question_audio'):
            title = convert_speech_to_text( request, request.POST.get('question_audio') )
        if request.POST.get('question_video'):
            title = convert_speech_to_text( request, request.POST.get('question_video') )
        post_data = copy.deepcopy(request.POST)
        if title:
            post_data['title'] = title[0].upper() + title[1:]
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
            topic.language_id = get_current_language(request)
            topic.save()
            if request.POST.get('comment'):
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

def search(request):
    category_id = None
    lid = get_current_language(request)
    categories = Category.objects.visible().parents()

    if(category_id != None):
        category = get_object_or_404(Category.objects.visible(),pk=category_id)                  

    topics = []
    search_term = request.GET.get('q')
    if search_term:
        topics = Topic.objects.filter(title__icontains = search_term)[:35]

    context = {
        'categories': categories,
        'topics': topics,
        'category_id' : category_id,
        'lid': lid,
        'search_term': search_term
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
    topics = Topic.objects.get(id = pk)
    try:
        user_profile = UserProfile.objects.get(user = request.user)
    except:
        user_profile = None
    context = {
        'topic': topics,
        'is_single_topic': pk,
        'user_profile': user_profile
    }
    return render(request, 'spirit/topic/particular_topic.html', context)

def share_vb_page(request, user_id, poll_id, slug):
    topics = Topic.objects.get(id = poll_id)
    try:
        user_profile = UserProfile.objects.get(user_id = user_id)
    except:
        user_profile = None
    context = {
        'topic': topics,
        'is_single_topic': poll_id,
        'user_profile': user_profile
    }
    return render(request, 'spirit/topic/particular_topic.html', context)

def index_active(request):
    categories = Category.objects.visible().parents()
    category = get_object_or_404(Category.objects.visible(), pk=5)
    subcategories = Category.objects.visible().children(parent=category)
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

def recent_topics(request):
    topics = Topic.objects.filter(language_id = get_current_language(request)).order_by('-date')[:30]
    context = {
        'topics': topics,
    }
    return render(request, 'spirit/topic/recent.html', context)

def index_videos(request):
    categories = Category.objects.visible().parents()
    category = get_object_or_404(Category.objects.visible(), pk=5)
    subcategories = Category.objects.visible().children(parent=category)
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
    pageno = request.GET.get('pageno', 1)
    topic_list = Topic.objects.filter(language_id = get_current_language(request))
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


def ques_ans_index(request, category_id = None, cat_slug = ''):
    page = 1
    topics = []
    lid = get_current_language(request)
    categories = Category.objects.visible().parents()
    
    if(category_id != None):
        category = get_object_or_404(Category.objects.visible(),pk=category_id)
        topic_list = category.category_topics.filter(language_id = lid)
        paginator = Paginator(topic_list, 10) # Show 25 contacts per page
        topics = paginator.page(page)
    else:
        topic_list = Topic.objects.filter(language_id = lid)
        paginator = Paginator(topic_list, 10) # Show 25 contacts per page
        topics = paginator.page(page)

    context = {
        'categories': categories,
        'topics': topics,
        'category_id' : category_id,
        'lid': lid
    }
    return render(request, 'spirit/topic/_ques_and_ans_index.html', context)

def comment_likes(request):
    comment_id = request.POST.get('comment_id',None)
    comment = Comment.objects.get(pk = comment_id)
    userprofile = request.user.st
    liked,is_created = Like.objects.get_or_create(comment_id = comment_id,user = request.user)
    if is_created:
            comment.likes_count = F('likes_count')+1
            comment.save()
            add_bolo_score(request.user.id,'liked')
            userprofile.like_count = F('like_count')+1
            userprofile.save()
            return HttpResponse(json.dumps({'success':'Success'}),content_type="application/json")
    else:
        if liked.like:
            liked.like = False
            liked.save()
            comment.likes_count = F('likes_count')-1
            comment.save()
            userprofile.like_count = F('like_count')-1
            userprofile.save()
        else:
            liked.like = True
            liked.save()
            comment.likes_count = F('likes_count')+1
            comment.save()
            userprofile.like_count = F('like_count')+1
            userprofile.save()
        return HttpResponse(json.dumps({'success':'Success'}),content_type="application/json")
    return HttpResponse(json.dumps({'fail':'Fail'}),content_type="application/json")


def index(request):
    return render(request, 'spirit/topic/_home.html')

def new_home(request):
    return render(request, 'spirit/topic/temporary_landing.html')
    # return render(request, 'spirit/topic/main_landing.html')

def get_about(request):
    return render(request, 'spirit/topic/about.html')

def get_termofservice(request):
    return render(request, 'spirit/topic/termsofservice.html')

def get_privacypolicy(request):
    return render(request, 'spirit/topic/privacypolicy.html')

def robotstext(request):
    return render(request, 'spirit/topic/robots.txt') 

def sitemapxml(request):
    return render(request, 'spirit/topic/sitemap.xml')       

# Share Pages Match 
def share_match_page(request, match_id, slug):
    cricket_match = CricketMatch.objects.get(pk=match_id)
    polls = Poll.objects.filter(cricketmatch = cricket_match,is_active = True)
    voting_status_array = []
    if polls:
        for index, poll in enumerate(polls):
            try:
                voting = Voting.objects.get(poll_id=poll.id,user = request.user)
                voting_status = True
            except:
                voting_status = False
            voting_status_array.append(poll)
            voting_status_array[index].voting_status = voting_status
    context = {
    'cricket_match': cricket_match,
    'polls': voting_status_array
    }
    return render(request, 'spirit/topic/cricket_match.html', context)
   
# Share Poll Match 
def share_poll_page(request, poll_id, slug):
    poll = Poll.objects.get(pk=poll_id)
    choices = Choice.objects.filter(poll = poll,is_active = True)
    voting = None
    try:
        voting = Voting.objects.get(poll_id=poll.id,user = request.user)
    except:
        voting = None
    context = {
        'cricket_match': poll.cricketmatch,
        'poll': poll,
        'choices': choices,
        'voting': voting
    }
    return render(request, 'spirit/topic/predict_match.html', context)

# Share User  
def share_user_page(request, user_id, username):
    try:        
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user = user)
        topics = Topic.objects.filter(user_id=user_id, is_removed=False)
        context = {
            'user_profile': user_profile,
            'topics': topics
        }
        return render(request, 'spirit/topic/particular_user.html', context)
    except:
        return render(request, 'spirit/topic/temporary_landing.html')