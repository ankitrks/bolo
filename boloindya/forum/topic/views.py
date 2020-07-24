# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponsePermanentRedirect
from django.utils.translation import ugettext_lazy as _
from djconfig import config
from django.conf import settings
from django.db.models import Sum

from ..core.utils.paginator import paginate, yt_paginate
from ..core.utils.ratelimit.decorators import ratelimit
from ..category.models import Category
from ..comment.models import MOVED
from ..comment.forms import CommentForm
from ..comment.utils import comment_posted
from ..comment.models import Comment
from .models import Topic,CricketMatch,Poll,Voting,Choice,TongueTwister,JobOpening,VBseen
from .forms import TopicForm
from .forms import JobRequestForm
from . import utils
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponse
import json
from django.core.paginator import Paginator
from forum.topic.models import Like
from django.db.models import F,Q
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
# Required for speech to text...
import io
import os
import urllib2
import copy
import random
import string
import subprocess
from datetime import datetime
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from drf_spirit.utils import add_bolo_score

from forum.user.models import UserProfile,AppPageContent

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.adapter import get_adapter as get_account_adapter

from allauth.account.utils import user_email 
from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.mail import send_mail
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .emails import send_job_request_mail
from drf_spirit.views import deafult_boloindya_follow
from drf_spirit.views import deafult_boloindya_follow

class AutoConnectSocialAccount(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        u = sociallogin.user
        u.set_unusable_password()
        if form:
            get_account_adapter().save_user(request, u, form)
        else:
            get_account_adapter().populate_username(request, u)
        sociallogin.save(request)
        emailId=user_email(u)
        try: 
            userDetails = User.objects.get(email=emailId)
            userToken=get_tokens_for_user(userDetails)
            print(userToken)

            userprofile = UserProfile.objects.get(user = userDetails)
            add_bolo_score(userDetails.id, 'initial_signup', userprofile)
            userprofile = UserProfile.objects.get(user = userDetails)
            if str(userprofile.language):
                default_follow = deafult_boloindya_follow(userDetails,str(userprofile.language))
        except EmailAddress.DoesNotExist:
            return u

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        #path = "/accounts/{username}/"
        
        return path.format(request.next)
        #return redirect(request.next)


def get_current_language(request):
    return request.COOKIES.get('language', request.GET.get('lid', 1))

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
    return HttpResponsePermanentRedirect('/analytics/')
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
            add_bolo_score(request.user.id, 'liked', comment)
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

def video_discover(request):
    language_id=1
    popular_bolo = []
    userprofile = []
    categories = []
    trending_videos = []
    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]
    try:
        categories = Category.objects.filter(parent__isnull=False)[:20]
    except Exception as e1:
        categories = []

        try:
            startdate = datetime.today()
            enddate = startdate - timedelta(days=125)
            trending_videos = Topic.objects.filter(is_removed=False, is_vb=True, is_popular=True, language_id=language_id, \
                    date__gte=enddate).order_by('-view_count')[:30]
        except Exception as e1:
            trending_videos = []

    try:
        if language_id:
            all_user = UserProfile.objects.filter(is_popular = True, language=language_id)[:10]
            popular_bolo=all_user
        else:
            all_user = UserProfile.objects.filter(is_popular = True)[:10]
            popular_bolo=all_user
    except Exception as e1:
        popular_bolo = []

    context = {
        'popular_bolo':popular_bolo,
        'trending_videos':trending_videos,
        'categories':categories
    }
    video_slug = request.GET.get('video',None)
    if(video_slug != None):
        return redirect('/video/'+video_slug)
    else:
        return render(request, 'spirit/topic/video_discover_hashtag.html', context)
        #return render(request, 'spirit/topic/video_discover.html', context)


def video_details(request,username='',id=''):
    
    #print topics
    #print user_profile.__dict__
    try:
        topics = Topic.objects.get(id = id)
    except:
        topics = None

    try:
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.filter(user=user,user__is_active = True)[0]
        
    except:
        user_profile = None
    context = {
        'topic': topics,
        'is_single_topic': "Yes",
        'user_profile': user_profile
    }

    return render(request, 'spirit/topic/video_details.html', context)

def video_details_by_slug(request,slug='',id=''):
    #print user_profile.__dict__
    #print 'videoId_'+id
    user_id=""
    try:
        if id != '':
            topics = Topic.objects.get(id = id)
        else:
            topics = Topic.objects.get(slug = slug)         
        user_id = topics.user_id
    except:
        topics = None

    try:
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.filter(user=user,user__is_active = True)[0]
        
    except:
        user_profile = None
    context = {
        'topic': topics,
        'is_single_topic': "Yes",
        'user_profile': user_profile
    }

    return render(request, 'spirit/topic/video_details.html', context)

def explore_video_details_by_slug(request,slug='',id=''):
    #print user_profile.__dict__
    #print 'videoId_'+id
    user_id=""
    try:
        if id != '':
            topics = Topic.objects.get(id = id)
        else:
            topics = Topic.objects.get(slug = slug)         
        user_id = topics.user_id
    except:
        topics = None

    try:
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.filter(user=user,user__is_active = True)[0]
        
    except:
        user_profile = None
    context = {
        'topic': topics,
        'is_single_topic': "Yes",
        'user_profile': user_profile
    }

    return render(request, 'spirit/topic/explore_video_details.html', context)

def bolo_user_details(request,username=''):
    #username=request.GET.get('lid');
    language_id=1
    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]

    popular_bolo = []
    try:      
        user = User.objects.get(username=username)
        #user_profile = UserProfile.objects.get(user = user)
        user_id=user.id
        user_profile = UserProfile.objects.filter(user=user,user__is_active = True)[0]
        topics = Topic.objects.filter(user_id=user_id, is_removed=False)
        topicsByLang = Topic.objects.filter(user_id=user_id, is_removed=False,language_id=language_id)
        try:
            if language_id:
                all_user = User.objects.filter(st__is_popular = True, st__language=language_id)[10]
                popular_bolo=all_user
            else:
                all_user = User.objects.filter(st__is_popular = True)[10]
                popular_bolo=all_user
        except Exception as e1:
            popular_bolo = []


        context = {
            'user_profile': user_profile,
            'user':user,
            'popular_bolo':popular_bolo,
            'topics': topics,
            'topicsCount': topicsByLang.count()
        }
        #print popular_bolo.__dict__

        video_slug = request.GET.get('video',None)
        if(video_slug != None):
            return redirect('/video/'+video_slug)
        else:
            return render(request, 'spirit/topic/user_details.html', context)
    except:
        return redirect('/')

def user_timeline(request):
    username=request.GET.get('username');
    language_id=1
    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]

    popular_bolo = []
    try:      
        user = User.objects.get(username=username)
        #user_profile = UserProfile.objects.get(user = user)
        user_id=user.id
        user_profile = UserProfile.objects.filter(user=user,user__is_active = True)[0]
        topics = Topic.objects.filter(user_id=user_id, is_removed=False)
        topicsByLang = Topic.objects.filter(user_id=user_id, is_removed=False,language_id=language_id)
        try:
            if language_id:
                all_user = User.objects.filter(st__is_popular = True, st__language=language_id)[10]
                popular_bolo=all_user
            else:
                all_user = User.objects.filter(st__is_popular = True)[10]
                popular_bolo=all_user
        except Exception as e1:
            popular_bolo = []


        context = {
            'user_profile': user_profile,
            'user':user,
            'popular_bolo':popular_bolo,
            'topics': topics,
            'topicsCount': topicsByLang.count()
        }
        #print popular_bolo.__dict__
        return render(request, 'spirit/topic/user_details.html', context)
    except:
        return redirect('/')

def boloindya_careers(request):
    return render(request, 'spirit/topic/boloindya_career_old.html')

def boloindya_team_details(request):
    return render(request, 'spirit/topic/boloindya_team.html')

def upload_video_boloindya(request):
    return render(request, 'spirit/topic/upload_videos.html')

def boloindya_openings(request):
    job_openings = []
    try:
        job_openings = JobOpening.objects.filter(publish_status = 1,expiry_date__gte = datetime.now())
    except:
        job_openings = None

    context = {
        'job_openings': job_openings,

    }

    return render(request, 'spirit/topic/boloindya_openings.html',context)

def boloindya_opening_details(request,slug):
    job_openings = None
    job_id=""
    try:
        
        job_opening = JobOpening.objects.filter(publish_status = True, expiry_date__gte = datetime.now(), slug=slug)
        job_openings =job_opening[0]
        job_id = job_openings.id
        
    except:
        job_openings = None
    if request.method == 'POST':
        details = JobRequestForm(request.POST,request.FILES)
        if details.is_valid():
            jobRequest=details.save()
            #emailRe='sarfarazalam115@gmail.com';
            emailRe='sarfaraz@careeranna.com,varun@boloindya.com,ankit@careeranna.com';
            email = request.POST.get('email')
            subject = 'Job Request'
            name = request.POST.get('name')
            mobile = request.POST.get('mobile')
            document = request.FILES.get('document')
            email_from = settings.EMAIL_SENDER
            recipient_list = [emailRe]
            job_profile=""
            if job_openings is not None:
                job_profile =job_openings.title

            messages=[]
            email_body = """\
                <html>
                  <head></head>
                  <body>
                        Hello, <br><br>
                        We have received a job request from %s. Please find the details below:<br><br>
                        <b>Job for :</b> %s <br>
                        <b>Name:</b> %s <br>
                        <b>Email:</b> %s <br>
                        <b>Contact:</b> %s <br>
                        Thanks,<br>
                        Team BoloIndya
                  </body>
                </html>
                """ % (name,job_profile,name, email, mobile)
            email = EmailMessage(subject,email_body,email_from,recipient_list)
            base_dir = 'media/media/documents/'+str(document)
            email.content_subtype = "html"
            email.attach_file('media/media/documents/'+str(document))
            email.send()
            messageResponse='Request Submitted Successfully';
            context = {
                'job_openings': job_openings,
                'message':messageResponse

            }            
            return render(request, 'spirit/topic/boloindya_opening_details.html',context)
    else:
        initial={'jobOpening_id': job_id}
        form = JobRequestForm(initial)
        context = {
            'job_openings': job_openings,
            'form': form

        }          
        return render(request, 'spirit/topic/boloindya_opening_details.html',context)

def job_request(request):
    if request.method == 'POST':
        #form = JobRequestForm(request.POST)
        details = JobRequestForm(request.POST)
        if details.is_valid():
            details.save()
            return HttpResponse("data submitted successfully")
    else:
        form = JobRequestForm()
    return render(request, 'spirit/topic/job_request_form.html', {'form': form})


def help_support(request):
    messageResponse=None
    if request.method == 'POST':
        #emailRe='sarfarazalam115@gmail.com';
        emailRe='sarfaraz@careeranna.com,varun@boloindya.com,ankit@careeranna.com';
        email = request.POST.get('email')
        subject = 'Help Request'
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        queryRe = request.POST.get('document')
        email_from = settings.EMAIL_SENDER
        recipient_list = [emailRe]

        messages=[]
        email_body = """\
            <html>
              <head></head>
              <body>
                    Hello, <br><br>
                    We have received a help request from %s. Please find the details below:<br><br>
                    <b>Name:</b> %s <br>
                    <b>Email:</b> %s <br>
                    <b>Contact:</b> %s <br>
                    <p> %s </p>
                    Thanks,<br>
                    Team BoloIndya
              </body>
            </html>
            """ % (name,name, email, mobile,queryRe)
        email = EmailMessage(subject,email_body,email_from,recipient_list)
        email.content_subtype = "html"
        email.send()
        messageResponse='Request Submitted Successfully';
        context = {
            'message':messageResponse

        }            
        return render(request, 'spirit/topic/help_support.html',context)
    else:
        context = {
            'message': messageResponse

        }          
        return render(request, 'spirit/topic/help_support.html',context)


def get_challenge_details(request):
    challengeHash=request.GET.get('ChallengeHash');
    language_id=1
    popular_bolo = []
    tongue=[]
    category_details=""
    challengehash=""
    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode] 
    challengehash = '#' + challengeHash
    tongue = TongueTwister.objects.filter(hash_tag__iexact=challengehash[1:]).order_by('-hash_counter')
    if len(tongue):
        tongue = tongue[0]
    context = {
        'tongue':tongue,
        'hashtag':challengeHash,

    }
    #print TongueTwister.__dict__
    return render(request, 'spirit/topic/topic_list_by_hashtag.html', context)

       
def get_topic_details_by_category(request,category_slug):
    language_id=1
    popular_bolo = []
    category_details=""
    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]  

    try:     
        category = Category.objects.get(slug=category_slug)
        #topics = Topic.objects.filter(m2mcategory=category,is_removed = False,is_vb = False)
        all_vb = Topic.objects.filter(m2mcategory=category, is_removed=False, is_vb=True, language_id=language_id)
        vb_count = all_vb.count()
        all_seen = category.view_count
        #print topics
        #user_profile = UserProfile.objects.filter(user=user,user__is_active = True)[0]
        #topics = Topic.objects.filter(category=category, is_removed=False)
        try:
            if language_id:
                all_user = UserProfile.objects.filter(is_popular = True, language=language_id)[:10]
                popular_bolo=all_user
            else:
                all_user = UserProfile.objects.filter(is_popular = True)[:10]
                popular_bolo=all_user
        except Exception as e1:
            popular_bolo = []
    
        context = {
            'popular_bolo':popular_bolo,
            'category_details':category,
            'vb_count':vb_count,
            'all_seen':all_seen,
            'topics':all_vb
        }
        #print category.__dict__
        video_slug = request.GET.get('video',None)
        if(video_slug != None):
            return redirect('/video/'+video_slug)
        else:
            return render(request, 'spirit/topic/topic_details_by_category.html', context)
    except:
        return redirect('/')

def get_feed_list_by_category(request,category_slug):
    language_id=1
    popular_bolo = []
    category_details=""
    categories=[]
    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]  
    try:
        categories = Category.objects.filter(parent__isnull=False)[:20]
    except Exception as e1:
        categories = [] 
    try:     
        category = Category.objects.get(slug=category_slug)
        #topics = Topic.objects.filter(m2mcategory=category,is_removed = False,is_vb = False)
        all_vb = Topic.objects.filter(m2mcategory=category, is_removed=False, is_vb=True, language_id=language_id)
        vb_count = all_vb.count()
        all_seen = category.view_count
        #print topics
        #user_profile = UserProfile.objects.filter(user=user,user__is_active = True)[0]
        #topics = Topic.objects.filter(category=category, is_removed=False)
        try:
            if language_id:
                all_user = UserProfile.objects.filter(is_popular = True, language=language_id)[:10]
                popular_bolo=all_user
            else:
                all_user = UserProfile.objects.filter(is_popular = True)[:10]
                popular_bolo=all_user
        except Exception as e1:
            popular_bolo = []
        try:
            hash_tags = TongueTwister.objects.order_by('-hash_counter')[:10]
        except Exception as e1:
            hash_tags = []
        context = {
            'popular_bolo':popular_bolo,
            'category_details':category,
            'categories':categories,
            'vb_count':vb_count,
            'hash_tags':hash_tags,
            'all_seen':all_seen,
            'topics':all_vb
        }
        #print category.__dict__
        video_slug = request.GET.get('video',None)
        if(video_slug != None):
            return redirect('/video/'+video_slug)
        else:
            #return render(request, 'spirit/topic/feed_list_by_categories.html', context)
            return render(request, 'spirit/topic/video_discover_by_category.html', context)
    except:
        return render(request, 'spirit/topic/video_discover_by_category.html', context)
        #return render(request, 'spirit/topic/feed_list_by_categories.html', context)

def get_topic_list_by_hashtag(request,hashtag):
    language_id=1
    popular_bolo = []
    tongue=[]
    category_details=""
    challengehash=""
    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode] 
    challengehash = '#' + hashtag
    try:

        tongue = TongueTwister.objects.filter(hash_tag__iexact=challengehash[1:]).order_by('-hash_counter')
        if len(tongue):
            tongue = tongue[0]
        context = {
            'tongue':tongue,
            'hashtag':hashtag,

        }
        #print TongueTwister.__dict__
        video_slug = request.GET.get('video',None)
        if(video_slug != None):
            return redirect('/video/'+video_slug)
        else:
            return render(request, 'spirit/topic/topic_list_by_hashtag.html', context)
    except:
        return render(request, 'spirit/topic/topic_list_by_hashtag.html')



def search_by_term(request):
    search_term = request.GET.get('term','')
    context = {
        'is_single_topic': "Yes",
        'search_term':search_term
    } 

    video_slug = request.GET.get('video',None)
    if(video_slug != None):
        return redirect('/video/'+video_slug)

    return render(request, 'spirit/topic/search_results.html',context)

def new_home(request):
    categories = []
    hash_tags = []
    try:
        categories = Category.objects.filter(parent__isnull=False)[:4]
    except Exception as e1:
        categories = []    
    try:
        hash_tags = TongueTwister.objects.order_by('-hash_counter')[:4]
    except Exception as e1:
        hash_tags = []

    context = {
        'categories':categories,
        'hash_tags':hash_tags,
        'is_single_topic': "Yes",
    }  
    video_slug = request.GET.get('video',None)
    if(video_slug != None):
        return redirect('/video/'+video_slug)
    else:
        return render(request, 'spirit/topic/new_landing.html',context)
    return redirect('/')
    #return render(request, 'spirit/topic/temporary_landing.html')
    # return render(request, 'spirit/topic/new_landing.html')
    # return render(request, 'spirit/topic/main_landing.html')

def trending_polyplayer(request):
    categories = []
    hash_tags = []
    topics = []
    popular_bolo=[]
    language_id=0
    try:
        categories = Category.objects.filter(parent__isnull=False)[:20]
    except Exception as e1:
        categories = []   
    language_id = request.GET.get('language_id', 1)

    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]

    try:
        all_seen_vb = []
        if request.user.is_authenticated:
            all_seen_vb = VBseen.objects.filter(user = request.user, topic__language_id=language_id, topic__is_popular=True).distinct('topic_id').values_list('topic_id',flat=True)[:15]
        excluded_list =[]
        superstar_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:15]
        for each in superstar_post:
            excluded_list.append(each.id)
        popular_user_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:10]
        for each in popular_user_post:
            excluded_list.append(each.id)
        popular_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=False,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:2]
        for each in popular_post:
            excluded_list.append(each.id)
        other_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,is_popular=True).exclude(pk__in=list(all_seen_vb)+list(excluded_list)).order_by('-date')[:2]
        orderd_all_seen_post=[]
        all_seen_post = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=all_seen_vb)[:5]
        if all_seen_post:
            for each_id in all_seen_vb:
                for each_vb in all_seen_post:
                    if each_vb.id == each_id:
                        orderd_all_seen_post.append(each_vb)

        topics=list(superstar_post)+list(popular_user_post)+list(popular_post)+list(other_post)+list(orderd_all_seen_post)
    except Exception as e1:
        topics = []

    try:
        if language_id:
            all_user = UserProfile.objects.filter(is_popular = True, language=language_id)[:20]
            popular_bolo=all_user
        else:
            all_user = UserProfile.objects.filter(is_popular = True)[:20]
            popular_bolo=all_user
    except Exception as e1:
        popular_bolo = []

    try:
        hash_tags = TongueTwister.objects.order_by('-hash_counter')[:20]
    except Exception as e1:
        hash_tags = []
    print popular_bolo.__dict__

 
    context = {
        'categories':categories,
        'hash_tags':hash_tags,
        'topics':topics,
        'popular_bolo':popular_bolo,
        'is_single_topic': "Yes",
    }  
    video_slug = request.GET.get('video',None)
    if(video_slug != None):
        return redirect('/video/'+video_slug)
    else:
        return render(request, 'spirit/topic/trending_poly_player.html',context)


def trending_videojs(request):
    categories = []
    hash_tags = []
    topics = []
    popular_bolo=[]
    language_id=0
    try:
        categories = Category.objects.filter(parent__isnull=False)[:20]
    except Exception as e1:
        categories = []   
    language_id = request.GET.get('language_id', 1)

    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]

    try:
        all_seen_vb = []
        if request.user.is_authenticated:
            all_seen_vb = VBseen.objects.filter(user = request.user, topic__language_id=language_id, topic__is_popular=True).distinct('topic_id').values_list('topic_id',flat=True)[:15]
        excluded_list =[]
        superstar_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:15]
        for each in superstar_post:
            excluded_list.append(each.id)
        popular_user_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:10]
        for each in popular_user_post:
            excluded_list.append(each.id)
        popular_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=False,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:2]
        for each in popular_post:
            excluded_list.append(each.id)
        other_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,is_popular=True).exclude(pk__in=list(all_seen_vb)+list(excluded_list)).order_by('-date')[:2]
        orderd_all_seen_post=[]
        all_seen_post = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=all_seen_vb)[:5]
        if all_seen_post:
            for each_id in all_seen_vb:
                for each_vb in all_seen_post:
                    if each_vb.id == each_id:
                        orderd_all_seen_post.append(each_vb)

        topics=list(superstar_post)+list(popular_user_post)+list(popular_post)+list(other_post)+list(orderd_all_seen_post)
    except Exception as e1:
        topics = []

    try:
        if language_id:
            all_user = UserProfile.objects.filter(is_popular = True, language=language_id)[:20]
            popular_bolo=all_user
        else:
            all_user = UserProfile.objects.filter(is_popular = True)[:20]
            popular_bolo=all_user
    except Exception as e1:
        popular_bolo = []

    try:
        hash_tags = TongueTwister.objects.order_by('-hash_counter')[:20]
    except Exception as e1:
        hash_tags = []
    print popular_bolo.__dict__

 
    context = {
        'categories':categories,
        'hash_tags':hash_tags,
        'topics':topics,
        'popular_bolo':popular_bolo,
        'is_single_topic': "Yes",
    }  
    video_slug = request.GET.get('video',None)
    if(video_slug != None):
        return redirect('/video/'+video_slug)
    else:
        return render(request, 'spirit/topic/trending_videojs.html',context)


def old_home(request):
    categories = []
    hash_tags = []
    topics = []
    all_slider_topic = []
    try:
        categories = Category.objects.filter(parent__isnull=False)[:10]
    except Exception as e1:
        categories = []   
    language_id = request.GET.get('language_id', 1)

    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]

    try:
        all_seen_vb = []
        if request.user.is_authenticated:
            all_seen_vb = VBseen.objects.filter(user = request.user, topic__language_id=language_id, topic__is_popular=True).distinct('topic_id').values_list('topic_id',flat=True)[:15]
        excluded_list =[]
        superstar_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:15]
        for each in superstar_post:
            excluded_list.append(each.id)
        popular_user_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:10]
        for each in popular_user_post:
            excluded_list.append(each.id)
        popular_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=False,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:2]
        for each in popular_post:
            excluded_list.append(each.id)
        other_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,is_popular=True).exclude(pk__in=list(all_seen_vb)+list(excluded_list)).order_by('-date')[:2]
        orderd_all_seen_post=[]
        all_seen_post = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=all_seen_vb)[:5]
        if all_seen_post:
            for each_id in all_seen_vb:
                for each_vb in all_seen_post:
                    if each_vb.id == each_id:
                        orderd_all_seen_post.append(each_vb)

        topics=list(superstar_post)+list(popular_user_post)+list(popular_post)+list(other_post)+list(orderd_all_seen_post)
    except Exception as e1:
        topics = []

    topicsIds =[16092,25156,26248,23820,3449,4196,4218,17534,12569,12498,9681,9419,9384,8034,8024,26835,24352,14942]
    try:
        all_slider_topic = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=topicsIds)[:16]
    except Exception as e1:
        all_slider_topic = []

    try:
        hash_tags = TongueTwister.objects.order_by('-hash_counter')[:4]
    except Exception as e1:
        hash_tags = []

    context = {
        'categories':categories,
        'hash_tags':hash_tags,
        'topics':topics,
        'sliderVideos':all_slider_topic,
        'is_single_topic': "Yes",
    }  
    video_slug = request.GET.get('video',None)
    if(video_slug != None):
        return redirect('/video/'+video_slug)
    else:
        return render(request, 'spirit/topic/_latest_home.html',context)


    #return render(request, 'spirit/topic/temporary_landing.html')
    # return render(request, 'spirit/topic/new_landing.html')
    # return render(request, 'spirit/topic/main_landing.html')


#====================New Home =============================
def new_home_updated(request):
    categories = []
    hash_tags = []
    topics = []
    all_slider_topic = []
    try:
        categories = Category.objects.filter(parent__isnull=False)[:10]
    except Exception as e1:
        categories = []   
    language_id = request.GET.get('language_id', 1)

    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]

    try:
        all_seen_vb = []
        if request.user.is_authenticated:
            all_seen_vb = VBseen.objects.filter(user = request.user, topic__language_id=language_id, topic__is_popular=True).distinct('topic_id').values_list('topic_id',flat=True)[:15]
        excluded_list =[]
        superstar_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:15]
        for each in superstar_post:
            excluded_list.append(each.id)
        popular_user_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:10]
        for each in popular_user_post:
            excluded_list.append(each.id)
        popular_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=False,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:2]
        for each in popular_post:
            excluded_list.append(each.id)
        other_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,is_popular=True).exclude(pk__in=list(all_seen_vb)+list(excluded_list)).order_by('-date')[:2]
        orderd_all_seen_post=[]
        all_seen_post = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=all_seen_vb)[:5]
        if all_seen_post:
            for each_id in all_seen_vb:
                for each_vb in all_seen_post:
                    if each_vb.id == each_id:
                        orderd_all_seen_post.append(each_vb)

        topics=list(superstar_post)+list(popular_user_post)+list(popular_post)+list(other_post)+list(orderd_all_seen_post)
    except Exception as e1:
        topics = []

    topicsIds =[16092,25156,26248,23820,3449,4196,4218,17534,12569,12498,9681,9419,9384,8034,8024,26835,24352,14942]
    try:
        all_slider_topic = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=topicsIds)[:16]
    except Exception as e1:
        all_slider_topic = []

    try:
        hash_tags = TongueTwister.objects.order_by('-hash_counter')[:4]
    except Exception as e1:
        hash_tags = []

    context = {
        'categories':categories,
        'hash_tags':hash_tags,
        'topics':topics,
        'sliderVideos':all_slider_topic,
        'is_single_topic': "Yes",
    }  
    video_slug = request.GET.get('video',None)
    if(video_slug != None):
        return redirect('/video/'+video_slug)
    else:
        return render(request, 'spirit/topic/_new_updated_home.html',context)


    #return render(request, 'spirit/topic/temporary_landing.html')
    # return render(request, 'spirit/topic/new_landing.html')
    # return render(request, 'spirit/topic/main_landing.html')

#====================== End ==============================



def boloindya_feed(request):
    categories = []
    hash_tags = []
    topics = []
    popular_bolo=[]
    language_id=0
    try:
        categories = Category.objects.filter(parent__isnull=False)[:20]
    except Exception as e1:
        categories = []   
    language_id = request.GET.get('language_id', 1)

    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]

    try:
        all_seen_vb = []
        if request.user.is_authenticated:
            all_seen_vb = VBseen.objects.filter(user = request.user, topic__language_id=language_id, topic__is_popular=True).distinct('topic_id').values_list('topic_id',flat=True)[:15]
        excluded_list =[]
        superstar_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:15]
        for each in superstar_post:
            excluded_list.append(each.id)
        popular_user_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=True,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:10]
        for each in popular_user_post:
            excluded_list.append(each.id)
        popular_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,user__st__is_superstar = False,user__st__is_popular=False,is_popular=True).exclude(pk__in=all_seen_vb).distinct('user_id').order_by('user_id','-date')[:2]
        for each in popular_post:
            excluded_list.append(each.id)
        other_post = Topic.objects.filter(is_removed = False,is_vb = True,language_id = language_id,is_popular=True).exclude(pk__in=list(all_seen_vb)+list(excluded_list)).order_by('-date')[:2]
        orderd_all_seen_post=[]
        all_seen_post = Topic.objects.filter(is_removed=False,is_vb=True,pk__in=all_seen_vb)[:5]
        if all_seen_post:
            for each_id in all_seen_vb:
                for each_vb in all_seen_post:
                    if each_vb.id == each_id:
                        orderd_all_seen_post.append(each_vb)

        topics=list(superstar_post)+list(popular_user_post)+list(popular_post)+list(other_post)+list(orderd_all_seen_post)
    except Exception as e1:
        topics = []

    try:
        if language_id:
            all_user = UserProfile.objects.filter(is_popular = True, language=language_id)[:20]
            popular_bolo=all_user
        else:
            all_user = UserProfile.objects.filter(is_popular = True)[:20]
            popular_bolo=all_user
    except Exception as e1:
        popular_bolo = []

    try:
        hash_tags = TongueTwister.objects.order_by('-hash_counter')[:20]
    except Exception as e1:
        hash_tags = []
    print popular_bolo.__dict__

 
    context = {
        'categories':categories,
        'hash_tags':hash_tags,
        'topics':topics,
        'popular_bolo':popular_bolo,
        'is_single_topic': "Yes",
    }  
    video_slug = request.GET.get('video',None)
    if(video_slug != None):
        return redirect('/video/'+video_slug)
    else:
        #return render(request, 'spirit/topic/boloindya_feed.html',context)
        return render(request, 'spirit/topic/trending_feed.html',context)




def latest_home(request):
    utmURL = ''
    currentQueryString=request.GET.get('utm_source',None)
    if(currentQueryString != None):
        utmURL = '&referrer=web&utm_source='+currentQueryString+'&utm_medium=cpc&anid=admob'
    context = {
        'utm_url':utmURL
    } 

    return render(request, 'spirit/topic/single_page_landing.html',context)


def login_user(request):

    nextURL = request.GET.get('next',None)
    if nextURL == None:
        nextURL= '/feed/'

    context = {
        'is_single_topic': "Yes",
        'next_page_url':nextURL
    }    
    return render(request, 'spirit/topic/_login.html',context)
def user_profile(request,username):
    language_id=1
    languages_with_id=settings.LANGUAGES_WITH_ID
    languageCode =request.LANGUAGE_CODE
    language_id=languages_with_id[languageCode]

    popular_bolo = []
    try:      
        user = User.objects.get(username=username)
        #user_profile = UserProfile.objects.get(user = user)
        user_id=user.id
        user_profile = UserProfile.objects.filter(user=user,user__is_active = True)[0]
        topics = Topic.objects.filter(user_id=user_id, is_removed=False)
        topicsByLang = Topic.objects.filter(user_id=user_id, is_removed=False,language_id=language_id)
        try:
            if language_id:
                all_user = User.objects.filter(st__is_popular = True, st__language=language_id)[10]
                popular_bolo=all_user
            else:
                all_user = User.objects.filter(st__is_popular = True)[10]
                popular_bolo=all_user
        except Exception as e1:
            popular_bolo = []


        context = {
            'user_profile': user_profile,
            'user':user,
            'popular_bolo':popular_bolo,
            'topics': topics,
            'topicsCount': topicsByLang.count()
        } 
        return render(request, 'spirit/topic/user_profile.html', context)
    except:
        return redirect('/')
        #return render(request, 'spirit/topic/new_landing.html')  

def get_about(request):
    name = 'about_us'
    about_us_page_object = None
    try:
        about_us_page_object = AppPageContent.objects.filter(page_name = name)[0]
    except:
        about_us_page_object = None
    context = {
        'about_us': about_us_page_object
    }
    return render(request, 'spirit/topic/about.html',context)

def get_termofservice(request):
    name = 'terms_and_condition'
    terms_and_condition = None
    try:
        terms_and_condition = AppPageContent.objects.filter(page_name = name)[0]
    except:
        terms_and_condition = None
    context = {
        'terms_and_condition': terms_and_condition
    }
    return render(request, 'spirit/topic/termsofservice.html',context)

def get_privacypolicy(request):
    name = 'privacy_poilcy'
    privacy_poilcy = None
    try:
        privacy_poilcy = AppPageContent.objects.filter(page_name = name)[0]
    except:
        privacy_poilcy = None
    context = {
        'privacy_policy': privacy_poilcy
    }
    
    return render(request, 'spirit/topic/privacypolicy.html',context)

def get_bolo_action(request):
    name = 'bolo_action'
    bolo_action = None
    try:
        bolo_action = AppPageContent.objects.filter(page_name = name)[0]
    except:
        bolo_action = None
    context = {
        'bolo_action': bolo_action
    }
    
    return render(request, 'spirit/topic/bolo_action.html',context)

def robotstext(request):
    return render(request, 'spirit/topic/robots.txt') 

def sitemapxml(request):
    return render(request, 'spirit/topic/sitemap.xml') 

def video_status(request):
    return  '{"success":"true"}';      

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

# Share Pages Match 
def share_challenge_page(request, hashtag):
    challenge = TongueTwister.objects.get(hash_tag = hashtag)
    context = {
    'challenge': challenge,
    }
    return render(request, 'spirit/topic/challenge_details.html', context)
   
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

def login_using_api(request):
    username = request.POST.get('username', '')
    user_id = request.POST.get('user_id', '')
    user = User.objects.get(id=user_id)
    if user:
        login(request, user,backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponse(json.dumps({'success':'Success'}),content_type="application/json")
    return HttpResponse(json.dumps({'success':'Fail'}),content_type="application/json")

        

def testurllang(request):
    print 'Pass';
    languages_with_id=settings.LANGUAGES_WITH_ID
    print languages_with_id
    #languageCode =request.LANGUAGE_CODE
    #language_id=languages_with_id[languageCode]

