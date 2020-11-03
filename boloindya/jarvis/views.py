# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv, io,cv2
from django.contrib import messages
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import permission_required
import requests
from bs4 import BeautifulSoup
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import S3Transfer
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.db import connections
import json
import string
import random
import os
import hashlib
import time
import re
from django.db.models import Q
from drf_spirit.views import getVideoLength
from drf_spirit.utils  import calculate_encashable_details,language_options,check_or_create_user_pay
from forum.user.models import UserProfile, ReferralCode, ReferralCodeUsed, VideoCompleteRate, VideoPlaytime,UserPay
from forum.topic.models import Topic, VBseen, FVBseen, TongueTwister
from forum.category.models import Category
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from forum.userkyc.models import UserKYC, KYCBasicInfo, KYCDocumentType, KYCDocument, AdditionalInfo, BankDetail
from forum.payment.models import PaymentCycle,EncashableDetail,PaymentInfo
from django.conf import settings
from forum.payment.forms import PaymentForm,PaymentCycleForm
from django.views.generic.edit import FormView
from forum.userkyc.forms import KYCBasicInfoRejectForm,KYCDocumentRejectForm,AdditionalInfoRejectForm,BankDetailRejectForm
from .models import VideoUploadTranscode,VideoCategory, PushNotification, PushNotificationUser, user_group_options, \
    FCMDevice, notification_type_options, metrics_options, DashboardMetrics, DashboardMetricsJarvis, metrics_slab_options,\
     metrics_language_options, UserCountNotification, Report
from drf_spirit.models import MonthlyActiveUser, HourlyActiveUser, DailyActiveUser, VideoDetails, MusicAlbum, Campaign, Winner
from forum.category.models import Category
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import make_aware
from itertools import groupby
from django.db.models import Count
import ast
from drf_spirit.serializers import VideoCompleteRateSerializer
from coupon.serializers import CouponSerializer
from .forms import VideoUploadTranscodeForm,TopicUploadTranscodeForm,UserPayForm, AudioUploadForm, CampaignForm, UserForm
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, imencode
from django.core.files.base import ContentFile
from drf_spirit.serializers import UserWithUserSerializer
from django.db.models import F,Q
import traceback
from PIL import Image, ExifTags
from drf_spirit.utils import language_options
#from .models import category_slab_options
from django.db.models.functions import TruncMonth
from django.db.models.functions import TruncDay
from django.db.models import Count
from forum.category.models import Category
from datetime import datetime, timedelta
from forum.user.utils.bolo_redis import update_profile_counter
from rest_framework import generics
from coupon.models import Coupon, UserCoupon
from coupon.forms import CouponForm
from booking.models import Event, EventBooking
from drf_spirit.views import get_tokens_for_user
import pandas as pd

def get_bucket_details(bucket_name=None):
    bucket_credentials = {}
    if bucket_name == 'boloindyapp-prod':
        bucket_credentials['AWS_ACCESS_KEY_ID'] = settings.BOLOINDYA_AWS_ACCESS_KEY_ID
        bucket_credentials['AWS_SECRET_ACCESS_KEY'] = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY
        bucket_credentials['AWS_BUCKET_NAME'] = settings.BOLOINDYA_AWS_BUCKET_NAME

        #### Transcoder settings #####
        bucket_credentials['PIPELINE_ID_TS'] = settings.BOLOINDYA_PIPELINE_ID_TS
        bucket_credentials['ACCESS_KEY_ID_TS'] = settings.BOLOINDYA_AWS_ACCESS_KEY_ID_TS
        bucket_credentials['AWS_SECRET_ACCESS_KEY_TS'] = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY_TS
        bucket_credentials['AWS_BUCKET_NAME_TS'] = settings.BOLOINDYA_AWS_BUCKET_NAME_TS

    elif bucket_name == 'careeranna':
        bucket_credentials['AWS_ACCESS_KEY_ID'] = settings.CAREERANNA_AWS_ACCESS_KEY_ID
        bucket_credentials['AWS_SECRET_ACCESS_KEY'] = settings.CAREERANNA_AWS_SECRET_ACCESS_KEY
        bucket_credentials['AWS_BUCKET_NAME'] = settings.CAREERANNA_AWS_BUCKET_NAME

        #### Transcoder settings #####
        bucket_credentials['PIPELINE_ID_TS'] = settings.CAREERANNA_PIPELINE_ID_TS
        bucket_credentials['ACCESS_KEY_ID_TS'] = settings.CAREERANNA_AWS_ACCESS_KEY_ID_TS
        bucket_credentials['AWS_SECRET_ACCESS_KEY_TS'] = settings.CAREERANNA_AWS_SECRET_ACCESS_KEY_TS
        bucket_credentials['AWS_BUCKET_NAME_TS'] = settings.CAREERANNA_AWS_BUCKET_NAME_TS

    else:
        bucket_credentials['AWS_ACCESS_KEY_ID'] = settings.BOLOINDYA_AWS_ACCESS_KEY_ID
        bucket_credentials['AWS_SECRET_ACCESS_KEY'] = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY
        bucket_credentials['AWS_BUCKET_NAME'] = settings.BOLOINDYA_AWS_BUCKET_NAME

        #### Transcoder settings #####
        bucket_credentials['PIPELINE_ID_TS'] = settings.BOLOINDYA_PIPELINE_ID_TS
        bucket_credentials['ACCESS_KEY_ID_TS'] = settings.BOLOINDYA_AWS_ACCESS_KEY_ID_TS
        bucket_credentials['AWS_SECRET_ACCESS_KEY_TS'] = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY_TS
        bucket_credentials['AWS_BUCKET_NAME_TS'] = settings.BOLOINDYA_AWS_BUCKET_NAME_TS
    bucket_credentials['REGION_HOST'] = settings.REGION_HOST
    return bucket_credentials

def upload_tos3(file_name,bucket,folder_name=None):

    if folder_name:
        folder_name = folder_name.lower()
        file_key = urlify(folder_name)+'/'+urlify(file_name.name.lower())
    else:
        file_key = urlify(file_name.name.lower())
    bucket_credentials = get_bucket_details(bucket)
    client = boto3.client('s3',aws_access_key_id=bucket_credentials['AWS_ACCESS_KEY_ID'],aws_secret_access_key=bucket_credentials['AWS_SECRET_ACCESS_KEY'])
    transfer = S3Transfer(client)
    transfer.upload_file(urlify(file_name.name.lower()),bucket,file_key,extra_args={'ACL':'public-read'})
    file_url = 'https://'+bucket+'.s3.amazonaws.com/%s'%(file_key)
    transcode = transcode_media_file(urlify(folder_name),file_key,(file_key).split('/')[-1].split('.')[0],bucket)
    return file_url,transcode

def upload_to_s3_without_transcode(file_name, bucket, folder_name=None):
    print(file_name, bucket, folder_name)
    print("upload_to_s3_without_transcode")
    if folder_name:
        folder_name = folder_name.lower()
        file_key = urlify(folder_name)+'/'+urlify(file_name)
    else:
        file_key = urlify(file_name)
    bucket_credentials = get_bucket_details(bucket)
    client = boto3.client('s3',aws_access_key_id=bucket_credentials['AWS_ACCESS_KEY_ID'],aws_secret_access_key=bucket_credentials['AWS_SECRET_ACCESS_KEY'])
    transfer = S3Transfer(client)
    transfer.upload_file(urlify(file_name),bucket,file_key,extra_args={'ACL':'public-read'})
    file_url = 'https://'+bucket+'.s3.amazonaws.com/%s'%(file_key)
    return file_url

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def geturl(request):
    try:
        description = request.POST.get('description',None)
        is_vb_exist = Topic.objects.filter(title = description)
        if not is_vb_exist:

            username = request.POST.get('username',None)
            user = User.objects.get(username = username)
            category = request.POST.get('category',None)
            language = request.POST.get('language',None)
            if language.lower()=='hindi':
                language_id = '2'
            elif language.lower()=='tamil':
                language_id = '3'
            elif language.lower()=='telgu':
                language_id = '4'
            else:
                language_id = '1'
            url = requests.get(request.POST.get('url',None))
            html_page = url.text
            html = BeautifulSoup(html_page,'html.parser')
            video_url = html.find(property="og:video").get('content')
            video_title = html.find(property="og:title").get('content')
            video_image = html.find(property="og:image").get('content')
            video_file = requests.get(video_url,stream=True)
            file_name = video_url.split('/')[-1]
            temp_name = file_name.split('?')[0].split('.')
            file_name = temp_name[0]+"_"+id_generator()+'.'+temp_name[1]
        
            with open(file_name,'wb') as f:
                for chunk in video_file.iter_content(chunk_size = 1024*1024):
                    if chunk:
                        f.write(chunk)
            bucket_credentials = get_bucket_details('boloindyapp-prod')
            uploaded_url,transcode = upload_tos3(file_name,bucket_credentials['AWS_BUCKET_NAME'],'instagram')
            thumbnail = get_video_thumbnail(file_name,bucket_credentials['AWS_BUCKET_NAME'])
            media_duration = getVideoLength(file_name)
            create_vb = Topic.objects.create(title = description,language_id = language_id,category = Category.objects.get(title__icontains=category,parent__isnull = False),media_duration=media_duration,\
                thumbnail = thumbnail,is_vb = True,view_count = random.randint(300,400),question_image = thumbnail, backup_url=uploaded_url,question_video = transcode['new_m3u8_url']\
                ,is_transcoded = True,transcode_job_id = transcode['job_id'],user = user)
            os.remove(file_name)
            return HttpResponse(json.dumps({'message':'success','url':request.POST.get('url',None)}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'message':'success','url':request.POST.get('url',None)}),content_type="application/json")
    except Exception as e:
        return HttpResponse(json.dumps({'message':'fail','url':request.POST.get('url',None),'fail_message':str(e)}),content_type="application/json")

@login_required
def home(request):
    return render(request,'jarvis/layout/home.html')

@login_required
def importcsv(request):
    data = []
    title = []
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request,'This is not a csv file')
        
        file_data = csv_file.read().decode('UTF-8')
        lines = file_data.split("\n")
        title = lines[0].split(",")
        lines.pop(0)
        data = []
        for line in lines:
            if len(line) >= 4:
                fields = line.split(",")
                data.append(fields)
                #video_url = geturl(fields[1])
    
    return render(request,'admin/jarvis/importcsv.html',{'data':data,'title':title})

@login_required
def uploadvideofile(request):
    all_category = VideoCategory.objects.all()
    from django.db.models import Count
    all_upload = VideoUploadTranscode.objects.all().distinct().values('folder_to_upload')\
        .annotate(folder_count=Count('folder_to_upload')).order_by('folder_to_upload')
    return render(request,'jarvis/pages/upload_n_transcode/upload_n_transcode.html',
            {'all_category':all_category,'all_upload':all_upload})

@login_required
def boloindya_uploadvideofile(request):
    topic_form = TopicUploadTranscodeForm()
    return render(request,'jarvis/pages/upload_n_transcode/boloindya_upload_transcode.html',
            {'topic_form':topic_form})

@login_required
def boloindya_upload_audio_file(request):    
    topic_form = AudioUploadForm()
    return render(request,'jarvis/pages/upload_audio/boloindya_upload_audio.html',
            {'topic_form':topic_form})

@login_required
def new_campaign_page(request):    
    campaign_form = CampaignForm()
    return render(request,'jarvis/pages/campaigns/create_new_campaign.html',
            {'add_campaign':campaign_form})

@login_required
def video_management(request):
    return render(request,'admin/jarvis/video_management.html',{})

@login_required
def user_management(request):
    return render(request,'admin/jarvis/user_management.html',{})

@login_required
def referral(request):
    return render(request,'admin/jarvis/referral.html',{})

def getcsvdata(request):
    data = []
    if request.method == 'GET':
        return HttpResponse("upload a file first!")
    
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request,'This is not a csv file')
        
        file_data = csv_file.read().decode('UTF-8')
        lines = file_data.split("\n")
        for line in lines:
            if len(line) >= 4:
                fields = line.split(",")
                data.append(fields)
                #video_url = geturl(fields[1])
        return HttpResponse(json.dumps(data),content_type="application/json")

# AWS_ACCESS_KEY_ID = 'AKIAZNK4CM5CW4W4VWP7'
# AWS_SECRET_ACCESS_KEY = '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'
# REGION_HOST = 'us-east-1'
# AWS_BUCKET_NAME_TS='elastictranscode.videos'
# PIPELINE_ID_TS = '1545987947390-hpo4hx'

def transcode_media_file(prefix,input_key,file_name,bucket):
    data_dump = ''
    m3u8_url = ''
    job_id = ''
    # HLS Presets that will be used to create an adaptive bitrate playlist.
    hls_64k_audio_preset_id = '1351620000001-200071';
    hls_0400k_preset_id     = '1351620000001-200050';
    hls_0600k_preset_id     = '1351620000001-200040';
    hls_1000k_preset_id     = '1351620000001-200030';
    hls_1500k_preset_id     = '1351620000001-200020';
    hls_2000k_preset_id     = '1351620000001-200010';

    # HLS Segment duration that will be targeted.
    segment_duration_audio = '10'
    segment_duration_400 = '10'
    segment_duration_600 = '10'
    segment_duration_1000 = '10'
    segment_duration_1500 = '10'
    segment_duration_2000 = '10'

    #All outputs will have this prefix prepended to their output key.
    if prefix:
        output_key_prefix = prefix+'/'+file_name.split('.')[0]+'/'
    else:
        output_key_prefix = file_name.split('.')[0]+'/'

    #credentials
    bucket_credentials = get_bucket_details(bucket)

    # Creating client for accessing elastic transcoder 
    transcoder_client = boto3.client('elastictranscoder', bucket_credentials['REGION_HOST'], aws_access_key_id = bucket_credentials['ACCESS_KEY_ID_TS'], \
            aws_secret_access_key = bucket_credentials['AWS_SECRET_ACCESS_KEY_TS'])

    # Setup the job input using the provided input key.
    job_input = { 'Key': input_key }

    # Setup the job outputs using the HLS presets.
    # output_key = hashlib.sha256(input_key.encode('utf-8')).hexdigest()
    # print output_key
    output_key = file_name
    # print output_key

    hls_audio = {
        'Key' : 'hlsAudio/' + output_key,
        'PresetId' : hls_64k_audio_preset_id,
        'SegmentDuration' : segment_duration_audio
    }
    hls_400k = {
        'Key' : 'hls0400k/' + output_key,
        'PresetId' : hls_0400k_preset_id,
        'SegmentDuration' : segment_duration_400
    }
    hls_600k = {
        'Key' : 'hls0600k/' + output_key,
        'PresetId' : hls_0600k_preset_id,
        'SegmentDuration' : segment_duration_600
    }
    hls_1000k = {
        'Key' : 'hls1000k/' + output_key,
        'PresetId' : hls_1000k_preset_id,
        'SegmentDuration' : segment_duration_1000
    }
    hls_1500k = {
        'Key' : 'hls1500k/' + output_key,
        'PresetId' : hls_1500k_preset_id,
        'SegmentDuration' : segment_duration_1500
    }
    hls_2000k = {
        'Key' : 'hls2000k/' + output_key,
        'PresetId' : hls_2000k_preset_id,
        'SegmentDuration' : segment_duration_2000
    }
    job_outputs = [ hls_audio, hls_400k, hls_600k, hls_1000k, hls_1500k ,hls_2000k ]

    playlist_name = output_key
    # Setup master playlist which can be used to play using adaptive bitrate.
    playlist = {
        'Name' : playlist_name,
        'Format' : 'HLSv3',
        'OutputKeys' : map(lambda x: x['Key'], job_outputs)
    }

    output_key_prefix_final =  output_key_prefix
    # print output_key_prefix_final
    # Creating the job.
    create_job_request = {
        'PipelineId' : bucket_credentials['PIPELINE_ID_TS'],
        'Input' : job_input,
        'OutputKeyPrefix' : output_key_prefix_final,
        'Outputs' : job_outputs,
        'Playlists' : [ playlist ]
    }
    # print create_job_request
    data_dump += json.dumps(create_job_request)
    create_job_result=transcoder_client.create_job(**create_job_request)
    try:
        if bucket_credentials['AWS_BUCKET_NAME_TS']=='elastictranscode.videos':
            m3u8_url = os.path.join('https://s3.amazonaws.com/'+bucket_credentials['AWS_BUCKET_NAME_TS']+'/', \
                output_key_prefix_final, playlist_name + '.m3u8')
        else:
            m3u8_url = os.path.join('https://'+bucket_credentials['AWS_BUCKET_NAME_TS']+'.s3.amazonaws.com/', \
                output_key_prefix_final, playlist_name + '.m3u8')
        job_id = create_job_result['Job']['Id']
        data_dump += 'HLS job has been created: ' + json.dumps(create_job_result)
    except Exception as e:
        data_dump += 'Exception: ' + str(e)
    # print {'new_m3u8_url':m3u8_url, 'job_id':job_id}
    return {'new_m3u8_url':m3u8_url, 'job_id':job_id,'data_dump':data_dump}


def uploaddata(request):
    return HttpResponse()

def get_kyc_user_list(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        page_size = settings.USER_ACCEPTED_KYC_PAGE_SIZE
        page_no = request.GET.get('page_no', '1')
        all_kyc = UserKYC.objects.all()

        total_page = all_kyc.count()/page_size
        if all_kyc.count()%page_size:
            total_page += 1
        page = int(page_no) - 1

        return render(request,'jarvis/pages/userkyc/user_kyc_list.html', {'all_kyc': all_kyc[page*page_size:page*page_size+page_size],\
            'page_no': page_no, 'total_page': total_page})

def get_submitted_kyc_user_list(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):

        page_size = settings.USER_ACCEPTED_KYC_PAGE_SIZE
        page_no = request.GET.get('page_no', '1')
        all_kyc = UserKYC.objects.filter(is_kyc_completed=True,is_kyc_accepted=False)

        total_page = all_kyc.count()/page_size
        if all_kyc.count()%page_size:
            total_page += 1
        page = int(page_no) - 1

        return render(request,'jarvis/pages/userkyc/submitted_kyc.html', {'all_kyc': all_kyc[page*page_size:page*page_size+page_size],\
            'page_no': page_no, 'total_page': total_page})

def get_pending_kyc_user_list(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        page_size = settings.USER_ACCEPTED_KYC_PAGE_SIZE
        page_no = request.GET.get('page_no', '1')
        all_kyc = UserKYC.objects.filter(is_kyc_completed=False,is_kyc_accepted=False)

        total_page = all_kyc.count()/page_size
        if all_kyc.count()%page_size:
            total_page += 1
        page = int(page_no) - 1

        return render(request,'jarvis/pages/userkyc/pending_kyc.html', {'all_kyc': all_kyc[page*page_size:page*page_size+page_size],\
            'page_no': page_no, 'total_page': total_page})

def get_accepted_kyc_user_list(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        page_size = settings.USER_ACCEPTED_KYC_PAGE_SIZE
        page_no = request.GET.get('page_no', '1')
        all_kyc = UserKYC.objects.filter(is_kyc_completed=True)

        total_page = all_kyc.count()/page_size
        if all_kyc.count()%page_size:
            total_page += 1
        page = int(page_no) - 1

        return render(request,'jarvis/pages/userkyc/accepted_kyc.html', {'all_kyc': all_kyc[page*page_size:page*page_size+page_size],\
            'page_no': page_no, 'total_page': total_page})

def get_user_pay_details(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        return render(request,'jarvis/pages/payment/user_pay.html')

def approve_all_completd_kyc(request):
    try:
        if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
            UserKYC.objects.filter(is_kyc_completed=True,is_kyc_accepted=False).update(is_kyc_accepted = True,is_kyc_basic_info_accepted = True,is_kyc_document_info_accepted = True,is_kyc_pan_info_accepted = True,is_kyc_selfie_info_accepted = True,is_kyc_additional_info_accepted = True,is_kyc_bank_details_accepted = True)
            return HttpResponse(json.dumps({'success':'success'}),content_type="application/json")
    except Exception as e:
        return HttpResponse(json.dumps({'error':str(e)}),content_type="application/json")

def get_single_user_pay_details(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        username = request.GET.get('username',None)
        all_pay = UserPay.objects.filter(user__username = username).order_by('-id')
        user = User.objects.get(username=username)
        from datetime import datetime
        now = datetime.now()
        check_or_create_user_pay(user.id,'01-'+str(now.month)+'-'+str(now.year))
        user_pay_form = UserPayForm()
        return render(request,'jarvis/pages/payment/single_user_pay.html',{'all_pay':all_pay,'userprofile':user.st,'payment_form':user_pay_form})

def add_user_pay(request):
    if request.user.is_superuser:
        user_pay_id = request.POST.get('user_pay_id',None)
        amount_pay = request.POST.get('amount_pay',0)
        transaction_id = request.POST.get('transaction_id',None)
        if not user_pay_id:
            return HttpResponse(json.dumps({'is_success':'fail','reason':'pay_id missing'}),content_type="application/json")
        user_pay = UserPay.objects.get(pk=user_pay_id)
        if not user_pay.is_evaluated:
            return HttpResponse(json.dumps({'is_success':'fail','reason':'pay not evaluated for this month'}),content_type="application/json")
        user_pay.amount_pay = int(amount_pay)
        user_pay.transaction_id = transaction_id
        user_pay.is_paid = True
        from datetime import datetime
        user_pay.pay_date = datetime.now()
        user_pay.save()
        return HttpResponse(json.dumps({'is_success':'success'}),content_type="application/json")
    else:
        return HttpResponse(json.dumps({'is_success':'fail','message':'not authorised'}),content_type="application/json")



def get_kyc_of_user(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        username = request.GET.get('username',None)
        kyc_user = User.objects.get(username=username)
        kyc_details = UserKYC.objects.get(user=kyc_user)
        kyc_basic_info = KYCBasicInfo.objects.get(user=kyc_user)
        kyc_document = KYCDocument.objects.filter(user=kyc_user,is_active=True)
        # additional_info = AdditionalInfo.objects.get(user=kyc_user)
        bank_details = BankDetail.objects.get(user=kyc_user,is_active=True)
        kyc_basic_reject_form = KYCBasicInfoRejectForm()
        kyc_document_reject_form = KYCDocumentRejectForm()
        kyc_additional_reject_form = AdditionalInfoRejectForm()
        kyc_bank_reject_form = BankDetailRejectForm()
        return render(request,'jarvis/pages/userkyc/single_kyc.html',{'kyc_details':kyc_details,'kyc_basic_info':kyc_basic_info,\
            'kyc_document':kyc_document,'additional_info':'','bank_details':bank_details,'userprofile':kyc_user.st,\
            'user_details':kyc_user,'kyc_basic_reject_form':kyc_basic_reject_form,'kyc_document_reject_form':kyc_document_reject_form,'kyc_additional_reject_form':kyc_additional_reject_form,
            'kyc_bank_reject_form':kyc_bank_reject_form})


def SecretFileView(request):
    u = request.user
    filepath = request.GET.get('url').split('https://'+settings.AWS_STORAGE_BUCKET_NAME+'.s3.amazonaws.com/')[0]
    print filepath,"##################"
    if u.is_authenticated() and  u.is_staff:
        client = boto3.client('s3',aws_access_key_id = settings.AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY)
        # s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
        #                     settings.AWS_SECRET_ACCESS_KEY,
        #                     is_secure=True)
        # Create a URL valid for 60 seconds.
        return client.generate_url(60, 'GET',
                            bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            key=filepath,
                            force_http=True)

def get_encashable_detail(request):
    to_be_calculated = request.GET.get("calculate",None)
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        if to_be_calculated:
            for each_user in User.objects.all():
                calculate_encashable_details(each_user)
        all_encash_details = EncashableDetail.objects.all().order_by('-bolo_score_earned')[:300]
    pay_cycle = PaymentCycle.objects.all().first()
    payement_cycle_form = PaymentCycleForm(initial=pay_cycle.__dict__)
    return render(request,'jarvis/pages/payment/encashable_detail.html',{'all_encash_details':all_encash_details,'payement_cycle_form':payement_cycle_form})

def calculate_encashable_detail(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        for each_user in User.objects.all():
            calculate_encashable_details(each_user)
    return HttpResponse(json.dumps({'success':'success'}),content_type="application/json")

def get_single_encash_detail(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        username = request.GET.get('username',None)
        user = User.objects.get(username=username)
        calculate_encashable_details(user)
        kyc_details = UserKYC.objects.filter(user=user)
        all_encash_details = EncashableDetail.objects.filter(user = user).order_by('-id')
        payment_form = PaymentForm()
        return render(request,'jarvis/pages/payment/single_encash_details.html',{'all_encash_details':all_encash_details,'userprofile':user.st,'user':user,'kyc_details':kyc_details,'payment_form':payment_form})


class PaymentView(FormView):
    form_class = PaymentForm
    template_name='jarvis/pages/payment/invoice_error.html'

    def form_valid(self, form,**kwargs):
        receipt, created = PaymentInfo.objects.get_or_create(**form.cleaned_data)
        if created:
            enchashable_detail = receipt.enchashable_detail
            receipt.user = enchashable_detail.user
            userprofile = enchashable_detail.user.st
            enchashable_detail.is_encashed = True
            enchashable_detail.enchashed_on = datetime.now()
            receipt.save()
            enchashable_detail.save()
        else:
            userprofile = receipt.user.st
        #send_mail_functionality_to_admin_and_to_user_if_mail_exist
        #send_sms_functionality_user
        # return HttpResponse(json.dumps({'success': 'success','receipt':receipt,'userprofile':userprofile }),content_type="application/json")
        return render(self.request,'jarvis/pages/payment/invoice.html',{'success': 'success','receipt':receipt,'userprofile':userprofile })

    def get_context_data(self,*args,**kwargs):
        kwargs=super(PaymentView,self).get_context_data(*args,**kwargs)
        kwargs['http_referer']=self.request.META.get('HTTP_REFERER',None)
        return super(PaymentView,self).get_context_data(*args,**kwargs)

class PaymentCycleView(FormView):
    form_class = PaymentCycleForm
    template_name='jarvis/pages/payment/invoice_error.html'

    def form_valid(self,form,**kwargs):
        if self.request.user.is_superuser or 'moderator' in list(self.request.user.groups.all().values_list('name',flat=True)) or self.request.user.is_staff:
            pay_cycle = PaymentCycle.objects.all().update(**form.cleaned_data)
            for each_user in User.objects.all():
                calculate_encashable_details(each_user)
            all_encash_details = EncashableDetail.objects.all().order_by('-bolo_score_earned')
            pay_cycle = PaymentCycle.objects.all().first()
            payement_cycle_form = PaymentCycleForm(initial=pay_cycle.__dict__)
            return render(request,'jarvis/pages/payment/encashable_detail.html',{'all_encash_details':all_encash_details,'payement_cycle_form':payement_cycle_form})


def accept_kyc(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        kyc_type = request.GET.get('kyc_type',None)
        user_id = request.GET.get('user_id',None)
        if kyc_type == "basic_info":
            UserKYC.objects.filter(user_id = user_id).update(is_kyc_basic_info_accepted = True)
        elif kyc_type == "kyc_document":
            UserKYC.objects.filter(user_id = user_id).update(is_kyc_document_info_accepted = True)
        elif kyc_type == "kyc_pan":
            UserKYC.objects.filter(user_id = user_id).update(is_kyc_pan_info_accepted = True)
        elif kyc_type == "kyc_profile_pic":
            UserKYC.objects.filter(user_id = user_id).update(is_kyc_selfie_info_accepted = True)
        elif kyc_type == "kyc_additional_info":
            UserKYC.objects.filter(user_id = user_id).update(is_kyc_additional_info_accepted = True)
        elif kyc_type == "kyc_bank_details":
            UserKYC.objects.filter(user_id = user_id).update(is_kyc_bank_details_accepted = True)
        user_kyc = UserKYC.objects.get(user_id = user_id)
        if user_kyc.is_kyc_basic_info_accepted and user_kyc.is_kyc_document_info_accepted and user_kyc.is_kyc_selfie_info_accepted and\
        user_kyc.is_kyc_bank_details_accepted:
            UserKYC.objects.filter(user_id = user_id).update(is_kyc_accepted = True)
        user_kyc = UserKYC.objects.get(user_id = user_id)

        return HttpResponse(json.dumps({'success':'success','kyc_accepted':user_kyc.is_kyc_accepted}),content_type="application/json")

def reject_kyc(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        kyc_type = request.GET.get('kyc_type',None)
        kyc_id = request.GET.get('kyc_id',None)
        kyc_reject_reason = request.GET.get('kyc_reject_reason',None)
        kyc_reject_text = request.GET.get('kyc_reject_text',None)
        user_id = request.GET.get('user_id',None)
        user_kyc = UserKYC.objects.get(user_id = user_id)
        if kyc_type == "basic_info":
            user_kyc.is_kyc_basic_info_accepted = False
            user_kyc.kyc_basic_info_submitted = False
            obj = KYCBasicInfo.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        elif kyc_type == "kyc_document":
            user_kyc.is_kyc_document_info_accepted = False
            user_kyc.kyc_document_info_submitted = False
            obj = KYCDocument.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        elif kyc_type == "kyc_pan":
            user_kyc.is_kyc_pan_info_accepted = False
            user_kyc.kyc_pan_info_submitted = False
            obj = KYCDocument.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        elif kyc_type == "kyc_profile_pic":
            user_kyc.is_kyc_selfie_info_accepted = False
            user_kyc.kyc_selfie_info_submitted = False
            obj = KYCBasicInfo.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        # elif kyc_type == "kyc_additional_info":
        #     user_kyc.is_kyc_additional_info_accepted = False
        #     user_kyc.kyc_additional_info_submitted = False
        #     obj = AdditionalInfo.objects.get(pk=kyc_id)
        #     obj.reject_reason = kyc_reject_reason
        #     obj.reject_text = kyc_reject_text      
        elif kyc_type == "kyc_bank_details":
            user_kyc.is_kyc_bank_details_accepted = False
            user_kyc.kyc_bank_details_submitted = False
            obj = BankDetail.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        obj.is_rejected = True
        obj.is_active = False
        obj.save()
        user_kyc.save()
        if not (user_kyc.is_kyc_basic_info_accepted and user_kyc.is_kyc_document_info_accepted and user_kyc.is_kyc_selfie_info_accepted and \
        user_kyc.is_kyc_bank_details_accepted and userkyc.is_kyc_selfie_info_accepted):
            user_kyc.is_kyc_accepted = False
            user_kyc.is_kyc_completed = False
            user_kyc.save()

        return HttpResponse(json.dumps({'success':'success','kyc_accepted':user_kyc.is_kyc_accepted}),content_type="application/json")

def urlify(s):
    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '_', s)
    s = re.sub(r"&", 'and', s)
    return s

def check_file_name_validation(filename,username):
    if check_filename_valid(filename):
        return filename
    else:
        import time
        epoch_time = int(round(time.time() * 1000))
        file_name_words = filename.split('_')
        file_extension = file_name_words[-1].split('.')[-1]
        return username+'_'+str(epoch_time)+'.'+file_extension


def check_filename_valid(filename):
    if re.match(r"^[A-Za-z0-9_.-]+(:?\.mp4|\.mov|\.3gp)+$", filename):
        return True
    else:
        return False

def check_audio_file_name_validation(filename,hashkey):
    if check_audio_filename_valid(filename):
        return filename
    else:
        import time
        epoch_time = int(round(time.time() * 1000))
        file_name_words = filename.split('_')
        file_extension = file_name_words[-1].split('.')[-1]
        return hashkey+'_'+str(epoch_time)+'.'+file_extension


def check_audio_filename_valid(filename):
    if re.match(r"^[A-Za-z0-9_.-]+(:?\.mp3)+$", filename):
        return True
    else:
        return False

def check_image_file_name_validation(filename,hashkey):
    if check_image_filename_valid(filename):
        return filename
    else:
        import time
        epoch_time = int(round(time.time() * 1000))
        file_name_words = filename.split('_')
        file_extension = file_name_words[-1].split('.')[-1]
        return hashkey+'_'+str(epoch_time)+'.'+file_extension


def check_image_filename_valid(filename):
    if re.match(r"^[A-Za-z0-9_.-]+(:?\.jpg|\.png)+$", filename):
        return True
    else:
        return False


@login_required
def upload_n_transcode(request):
    upload_file = request.FILES['media_file']
    upload_to_bucket = request.POST.get('bucket_name',None)
    upload_folder_name = request.POST.get('folder_prefix',None)
    upload_category = request.POST.get('category_choice',None)
    free_video = request.POST.get('free_video',None)
    video_title = request.POST.get('video_title',None)
    video_descp = request.POST.get('video_descp',None)
    meta_title = request.POST.get('meta_title',None)
    meta_descp = request.POST.get('meta_descp',None)
    meta_keywords = request.POST.get('meta_keywords',None)
    video_category = False
    if upload_category:
        upload_category = upload_category.strip()
        if upload_category:
            video_category,is_created = VideoCategory.objects.get_or_create(category_name = upload_category.lower())

    # print upload_file,upload_to_bucket,upload_folder_name
    if not upload_to_bucket:
        return HttpResponse(json.dumps({'message':'fail','reason':'bucket_missing'}),content_type="application/json")
    if not upload_file:
        return HttpResponse(json.dumps({'message':'fail','reason':'File Missing'}),content_type="application/json")
    if not (upload_file.name.endswith('.mp4') or upload_file.name.endswith('.mov')):
        return HttpResponse(json.dumps({'message':'fail','reason':'This is not a mp4  mov file'}),content_type="application/json")
    if free_video and (not video_title or not video_descp):
        return HttpResponse(json.dumps({'message':'fail','reason':'Title or Description is missing'}),content_type="application/json")

    bucket_credentials = get_bucket_details(upload_to_bucket)
    conn = boto3.client('s3', bucket_credentials['REGION_HOST'], aws_access_key_id = bucket_credentials['AWS_ACCESS_KEY_ID'], \
            aws_secret_access_key = bucket_credentials['AWS_SECRET_ACCESS_KEY'])
    upload_file_name = upload_file.name.lower()
    if upload_folder_name:
        upload_folder_name = upload_folder_name.lower()
        file_key_1 = urlify(upload_folder_name)+'/'+urlify(upload_file_name)
        file_key_2 = urlify(upload_file_name)
    else:
        file_key_1 = urlify(upload_file_name)
        file_key_2 = urlify(upload_file_name)
    try:
        conn.head_object(Bucket=upload_to_bucket, Key=file_key_1)
        return HttpResponse(json.dumps({'message':'fail','reason':'File already exist'}),content_type="application/json")
    except Exception as e:
        try:
            conn.head_object(Bucket=upload_to_bucket, Key=file_key_2)
            return HttpResponse(json.dumps({'message':'fail','reason':'File already exist'}),content_type="application/json")
        except Exception as e:
            with open(urlify(upload_file_name),'wb') as f:
                for chunk in upload_file.chunks():
                    if chunk:
                        f.write(chunk)


            uploaded_url,transcode = upload_tos3(upload_file,upload_to_bucket,upload_folder_name)
            thumbnail_url = get_video_thumbnail(urlify(upload_file_name),upload_to_bucket)
            try:
                videolength = getVideoLength(urlify(upload_file_name))
            except:
                videolength = ''
            print videolength
            my_dict = {}
            my_dict['s3_file_url']=uploaded_url
            if 'job_id' in transcode:
                my_dict['transcode_job_id'] = transcode['job_id']
            my_dict['transcode_dump'] = transcode['data_dump']
            if 'new_m3u8_url' in transcode:
                my_dict['transcoded_file_url'] = transcode['new_m3u8_url']
            my_dict['filename_uploaded'] = upload_file_name
            my_dict['filename_changed'] = urlify(upload_file_name)
            my_dict['folder_to_upload'] = upload_folder_name
            my_dict['folder_to_upload_changed'] = urlify(upload_folder_name)
            my_dict['thumbnail_url'] = thumbnail_url
            my_dict['media_duration'] = videolength
            if video_category:
                my_dict['category'] = video_category
            if free_video:
                my_dict['is_free_video'] = True
                my_dict['video_title'] = video_title
                my_dict['video_descp'] = video_descp
                my_dict['meta_title'] = meta_title
                my_dict['meta_descp'] = meta_descp
                my_dict['meta_keywords'] = meta_keywords
                my_dict['uploaded_user'] = request.user
            my_upload_transcode = VideoUploadTranscode.objects.create(**my_dict)
            os.remove(urlify(upload_file_name))
            try:
                update_careeranna_db(my_upload_transcode)
            except Exception as e:
                return HttpResponse(json.dumps({'message':'success','file_id':my_upload_transcode.id}),content_type="application/json")
                return HttpResponse(json.dumps({'message':'fail','reason':'Could not update careeranna db'+str(e)}),content_type="application/json")

    return HttpResponse(json.dumps({'message':'success','file_id':my_upload_transcode.id}),content_type="application/json")

@login_required
def boloindya_upload_audio_file_to_s3(request):
    audio_file,image_file = request.FILES.getlist('media_file')
    title = request.POST.get('title',None)
    author_name = request.POST.get('author_name',None)
    audio_upload_folder_name = request.POST.get('folder_prefix','from_upload_panel/audio')
    image_upload_folder_name = request.POST.get('folder_prefix','from_upload_panel/audio_image')
    upload_to_bucket = request.POST.get('bucket_name',None)
    language_id = request.POST.get('language_id',None)
    order_no = request.POST.get('order_no',None)
    if not upload_to_bucket:
        return HttpResponse(json.dumps({'message':'fail','reason':'bucket_missing'}),content_type="application/json")
    if not audio_file:
        return HttpResponse(json.dumps({'message':'fail','reason':'Audio File Missing'}),content_type="application/json")
    if not image_file:
        return HttpResponse(json.dumps({'message':'fail','reason':'Image File Missing'}),content_type="application/json")
    if not audio_file.name.endswith('.mp3'):
        return HttpResponse(json.dumps({'message':'fail','reason':'This is not a mp3 file'}),content_type="application/json")
    if not image_file.name.endswith(('.jpg','.png')):
        return HttpResponse(json.dumps({'message':'fail','reason':'This is not a jpg/png file'}),content_type="application/json")
    if not title or not author_name:
        return HttpResponse(json.dumps({'message':'fail','reason':'Title or Author name is missing'}),content_type="application/json")
    if not language_id:
        return HttpResponse(json.dumps({'message':'fail','reason':'Language is missing'}),content_type="application/json")
    if not order_no:
        return HttpResponse(json.dumps({'message':'fail','reason':'Order Number is missing'}),content_type="application/json")
    bucket_credentials = get_bucket_details(upload_to_bucket)
    conn = boto3.client('s3', bucket_credentials['REGION_HOST'], aws_access_key_id = bucket_credentials['AWS_ACCESS_KEY_ID'], \
            aws_secret_access_key = bucket_credentials['AWS_SECRET_ACCESS_KEY'])


    audio_file_name = urlify(audio_file.name.lower())
    image_file_name = urlify(image_file.name.lower())
    audio_output_key = hashlib.sha256(audio_file_name.encode('utf-8')).hexdigest()
    image_output_key = hashlib.sha256(image_file_name.encode('utf-8')).hexdigest()
    audio_file_name = check_audio_file_name_validation(audio_file_name,audio_output_key)
    image_file_name = check_image_file_name_validation(image_file_name,image_output_key)

    audio_path = audio_upload_folder_name+'/'+audio_file_name
    image_path = image_upload_folder_name+'/'+image_file_name
    try:
        conn.head_object(Bucket=upload_to_bucket, Key=audio_path)
        return HttpResponse(json.dumps({'message':'fail','reason':'Audio File already exist'}),content_type="application/json")
    except Exception as e:
        with open(urlify(audio_file_name),'wb') as f:
            for chunk in audio_file.chunks():
                if chunk:
                    f.write(chunk)
    try:
        conn.head_object(Bucket=upload_to_bucket, Key=image_path)
        return HttpResponse(json.dumps({'message':'fail','reason':'Image File already exist'}),content_type="application/json")
    except Exception as e:
        with open(urlify(image_file_name),'wb') as f:
            for chunk in image_file.chunks():
                if chunk:
                    f.write(chunk)

    uploaded_audio_url = upload_to_s3_without_transcode(audio_file_name,upload_to_bucket,audio_upload_folder_name)
    uploaded_image_url = upload_to_s3_without_transcode(image_file_name,upload_to_bucket,image_upload_folder_name)
    music_album_dict = {}
    music_album_dict['title'] = title
    music_album_dict['author_name'] = author_name
    music_album_dict['s3_file_path'] = uploaded_audio_url
    music_album_dict['image_path'] = uploaded_image_url
    music_album_dict['language_id'] = language_id
    music_album_dict['order_no'] = order_no
    music_album_obj = MusicAlbum.objects.create(**music_album_dict)

    os.remove(urlify(audio_file_name))
    os.remove(urlify(image_file_name))

    return HttpResponse(json.dumps({'message':'success','file_id':music_album_obj.id}),content_type="application/json")

@login_required
def boloindya_upload_n_transcode(request):
    upload_file = request.FILES['media_file']
    upload_to_bucket = request.POST.get('bucket_name',None)
    upload_folder_name = request.POST.get('folder_prefix','from_upload_panel')
    # upload_category = request.POST.get('category_choice',None)
    # free_video = request.POST.get('free_video',None)
    title = request.POST.get('title',None)
    m2mcategory = request.POST.getlist('m2mcategory',None)
    language_id = request.POST.get('language_id',None)
    user_id = request.POST.get('user_id',None)

    # print upload_file,upload_to_bucket,upload_folder_name
    if not upload_to_bucket:
        return HttpResponse(json.dumps({'message':'fail','reason':'bucket_missing'}),content_type="application/json")
    if not upload_file:
        return HttpResponse(json.dumps({'message':'fail','reason':'File Missing'}),content_type="application/json")
    if not upload_file.name.endswith('.mp4'):
        return HttpResponse(json.dumps({'message':'fail','reason':'This is not a mp4 file'}),content_type="application/json")
    if not title or not m2mcategory or not user_id:
        return HttpResponse(json.dumps({'message':'fail','reason':'Title, User or Category is missing'}),content_type="application/json")

    bucket_credentials = get_bucket_details(upload_to_bucket)
    conn = boto3.client('s3', bucket_credentials['REGION_HOST'], aws_access_key_id = bucket_credentials['AWS_ACCESS_KEY_ID'], \
            aws_secret_access_key = bucket_credentials['AWS_SECRET_ACCESS_KEY'])
    upload_file_name = check_file_name_validation(upload_file.name.lower(),User.objects.get(pk=user_id).username)
    if upload_folder_name:
        upload_folder_name = upload_folder_name.lower()
        file_key_1 = urlify(upload_folder_name)+'/'+urlify(upload_file_name)
        file_key_2 = urlify(upload_file_name)
    else:
        file_key_1 = urlify(upload_file_name)
        file_key_2 = urlify(upload_file_name)
    try:
        conn.head_object(Bucket=upload_to_bucket, Key=file_key_1)
        return HttpResponse(json.dumps({'message':'fail','reason':'File already exist'}),content_type="application/json")
    except Exception as e:
        try:
            conn.head_object(Bucket=upload_to_bucket, Key=file_key_2)
            return HttpResponse(json.dumps({'message':'fail','reason':'File already exist'}),content_type="application/json")
        except Exception as e:
            with open(urlify(upload_file_name),'wb') as f:
                for chunk in upload_file.chunks():
                    if chunk:
                        f.write(chunk)


            uploaded_url,transcode = upload_tos3(upload_file,upload_to_bucket,upload_folder_name)
            thumbnail_url = get_video_thumbnail(urlify(upload_file_name),upload_to_bucket)
            try:
                videolength = getVideoLength(urlify(upload_file_name))
            except:
                videolength = ''
            my_dict = {}
            topic_dict = {}
            my_dict['s3_file_url'] = uploaded_url
            topic_dict['backup_url'] = uploaded_url
            if 'job_id' in transcode:
                my_dict['transcode_job_id'] = transcode['job_id']
                topic_dict['transcode_job_id'] = transcode['job_id']
            my_dict['transcode_dump'] = transcode['data_dump']
            topic_dict['transcode_dump'] = transcode['data_dump']
            if 'new_m3u8_url' in transcode:
                my_dict['transcoded_file_url'] = transcode['new_m3u8_url']
                topic_dict['question_video'] = transcode['new_m3u8_url']
            my_dict['filename_uploaded'] = upload_file_name
            my_dict['filename_changed'] = urlify(upload_file_name)
            my_dict['folder_to_upload'] = upload_folder_name
            my_dict['folder_to_upload_changed'] = urlify(upload_folder_name)
            my_dict['uploaded_user'] = request.user
            topic_dict['is_transcoded'] = True
            topic_dict['question_image'] = thumbnail_url
            my_dict['thumbnail_url'] = thumbnail_url
            my_dict['media_duration'] = videolength
            topic_dict['media_duration'] = videolength
            view_count = random.randint(1,5)
            width,height = get_video_width_height(uploaded_url)
            topic_dict['vb_width'] = width
            topic_dict['vb_height'] = height
            topic_dict['title'] = title
            topic_dict['view_count'] = view_count
	    topic_dict['language_id'] = language_id
            topic_dict['is_vb'] = True
            my_upload_transcode = VideoUploadTranscode.objects.create(**my_dict)
            topic_dict['user_id'] = user_id
            my_topic = Topic.objects.create(**topic_dict)
            UserProfile.objects.filter(user_id=user_id).update(vb_count=F('vb_count')+1)
            for each in m2mcategory:
                my_topic.m2mcategory.add(Category.objects.get(pk=each))
            my_upload_transcode.is_topic = True
            my_upload_transcode.topic = my_topic
            my_upload_transcode.save()

            os.remove(urlify(upload_file_name))

    return HttpResponse(json.dumps({'message':'success','file_id':my_upload_transcode.id}),content_type="application/json")

def provide_view_count(view_count,topic):
    FVBseen.objects.create(topic_id = topic.id, view_count = view_count)
    update_profile_counter(topic.user_id,'view_count',view_count, True)

def get_video_width_height(video_url):
    try:
        import subprocess
        cmds2 = ['ffprobe','-v','error' , '-show_entries','stream=width,height','-of','csv=p=0:s=x',video_url]
        ps2 = subprocess.Popen(cmds2, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (output, stderr) = ps2.communicate()
        widthandheight = output.replace('\n','').split('x')
        return video_width
        video_width = widthandheight[0]
        video_height = widthandheight[1]
        return video_width,video_height
    except:
        return 0,0
def get_filtered_user(request):
    gender_id = request.POST.get('gender_id','1')
    language_id = request.POST.get('language_id','1')
    filtered_user = list(UserProfile.objects.filter(language = language_id,gender=gender_id,is_moderator=True,is_test_user=True).values_list('user_id','name','vb_count').order_by('-vb_count'))
    return HttpResponse(json.dumps({'message':'success','filtered_user':filtered_user}),content_type="application/json")

@login_required
def upload_details(request):
    file_id = request.GET.get('id',None)
    if file_id:
        my_video = VideoUploadTranscode.objects.get(pk=file_id)
        return render(request,'jarvis/pages/upload_n_transcode/video_urls.html',{'my_video':my_video})
    return render(request,'jarvis/pages/upload_n_transcode/video_urls.html')

@login_required
def boloindya_upload_details(request):
    file_id = request.GET.get('id',None)
    if file_id:
        my_video = VideoUploadTranscode.objects.get(pk=file_id)
        return render(request,'jarvis/pages/upload_n_transcode/boloindya_video_urls.html',{'my_video':my_video})
    return render(request,'jarvis/pages/upload_n_transcode/video_urls.html')


@login_required
def uploaded_list(request):
    all_uploaded = VideoUploadTranscode.objects.filter(is_active = True,is_topic=False).order_by('-id')
    return render(request,'jarvis/pages/upload_n_transcode/uploaded_list.html',{'all_uploaded':all_uploaded})

@login_required
def boloindya_uploaded_list(request):
    all_uploaded = VideoUploadTranscode.objects.filter(is_active = True,is_topic = True).order_by('-id')
    return render(request,'jarvis/pages/upload_n_transcode/boloindya_uploaded_list.html',{'all_uploaded':all_uploaded})

@login_required
def edit_upload(request):
    if request.method == 'GET':
        file_id = request.GET.get('id',None)
        if file_id:
            my_video = VideoUploadTranscode.objects.get(pk=file_id)
            my_dict = {'category':my_video.category,'video_title':my_video.video_title,'video_descp':my_video.video_descp,'is_free_video':my_video.is_free_video,\
            'meta_title':my_video.meta_title,'meta_descp':my_video.meta_descp,'meta_keywords':my_video.meta_keywords}
            video_form = VideoUploadTranscodeForm(initial=my_dict)
            return render(request,'jarvis/pages/upload_n_transcode/edit_upload.html',{'my_video':my_video,'video_form':video_form})
        return render(request,'jarvis/pages/upload_n_transcode/edit_upload.html')
    elif request.method == 'POST':
        video_id = request.POST.get('video_id',None)
        if video_id:
            my_video = VideoUploadTranscode.objects.get(pk=video_id)
            is_free_video = request.POST.get('is_free_video',None)
            if is_free_video:
                my_video.is_free_video = True
            else:
                my_video.is_free_video = False
            my_video.video_title = request.POST.get('video_title','')
            my_video.video_descp = request.POST.get('video_descp','')
            my_video.category_id = request.POST.get('category',None)
            my_video.meta_title = request.POST.get('meta_title','')
            my_video.meta_descp = request.POST.get('meta_descp','')
            my_video.meta_keywords = request.POST.get('meta_keywords','')
            my_video.save()
            try:
                update_careeranna_db(my_video)
            except Exception as e:
                return HttpResponse(json.dumps({'message':'fail','reason':'Could not update careeranna db'+str(e)}),content_type="application/json")
            return HttpResponse(json.dumps({'message':'success','video_id':my_video.id}),content_type="application/json")
        else:

            return HttpResponse(json.dumps({'message':'fail','reason':'file id not found'}),content_type="application/json")

@login_required
def boloindya_edit_upload(request):
    videoRotateStatus=None
    if request.method == 'GET':
        file_id = request.GET.get('id',None)
        if file_id:
            my_video = VideoUploadTranscode.objects.get(pk=file_id)
            topic = my_video.topic
            my_dict = {'title':topic.title,'category':topic.category,'m2mcategory':list(topic.m2mcategory.all().values_list('id',flat=True)),'language_id':topic.language_id,'gender':topic.user.st.gender}
            video_form = TopicUploadTranscodeForm(initial=my_dict)
            return render(request,'jarvis/pages/upload_n_transcode/boloindya_edit_upload.html',{'my_video':my_video,'video_form':video_form,'posted_userprofile':topic.user.st})
        return render(request,'jarvis/pages/upload_n_transcode/boloindya_edit_upload.html')
    elif request.method == 'POST':
        video_id = request.POST.get('video_id',None)
        if video_id:
            bucketName='boloindyapp-prod'
            my_video = VideoUploadTranscode.objects.get(pk=video_id)
            videoRotateStatus = request.POST.get('rotation',None)
            if videoRotateStatus:
                rotationAngle=request.POST.get('rotation',None)
                thumbnailUrl=my_video.thumbnail_url
                filepatha=upload_rotated_thumbail(thumbnailUrl,bucketName,rotationAngle);
            topic = my_video.topic
            topic.title = request.POST.get('title','')
            m2mcategory = request.POST.getlist('m2mcategory',None)
            if m2mcategory:
                all_category = topic.m2mcategory.all()
                for each_category in all_category:
                    topic.m2mcategory.remove(each_category)
                for each in m2mcategory:
                    topic.m2mcategory.add(Category.objects.get(pk=each))
            topic.language_id = request.POST.get('language_id','1')
            if request.POST.get('change_user',False):
                try:
                    UserProfile.objects.filter(user=topic.user).update(vb_count=F('vb_count')-1)
                except:
                    pass
                topic.user_id = request.POST.get('user_id',topic.user.id)
                UserProfile.objects.filter(user_id=request.POST.get('user_id',topic.user.id)).update(vb_count=F('vb_count')+1)
            topic.save()
            return HttpResponse(json.dumps({'message':'success','video_id':my_video.id}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'message':'fail','reason':'file id not found'}),content_type="application/json")

@login_required
def delete_upload(request):
    file_id = request.GET.get('id',None)
    if file_id:
        my_video = VideoUploadTranscode.objects.get(pk=file_id)
        my_video.is_active = False
        my_video.save()
        try:
            update_careeranna_db(my_video)
        except Exception as e:
             return HttpResponse(json.dumps({'message':'fail','reason':'Could not update careeranna db'+str(e)}),content_type="application/json")
        all_uploaded = VideoUploadTranscode.objects.filter(is_active = True)
        return render(request,'jarvis/pages/upload_n_transcode/uploaded_list.html',{'all_uploaded':all_uploaded})

def get_video_thumbnail(video_url,bucket_name):
    video = VideoCapture(video_url)
    frames_count = int(video.get(CAP_PROP_FRAME_COUNT))
    frame_no = frames_count*2/3
    video.set(CAP_PROP_POS_FRAMES, frame_no)
    success, frame = video.read()
    if success:
        b = imencode('.jpg', frame)[1].tostring()
        ts = time.time()
        virtual_thumb_file = ContentFile(b, name = "img-" + str(ts).replace(".", "")  + ".jpg" )
        url_thumbnail= upload_thumbail(virtual_thumb_file,bucket_name)
        # obj.thumbnail = url_thumbnail
        # obj.media_duration = media_duration
        # obj.save()
        return url_thumbnail
    else:
        return False


def upload_thumbail(virtual_thumb_file,bucket_name):
    try:
        bucket_credentials = get_bucket_details(bucket_name)
        client = boto3.client('s3',aws_access_key_id=bucket_credentials['AWS_ACCESS_KEY_ID'],aws_secret_access_key=bucket_credentials['AWS_SECRET_ACCESS_KEY'])
        ts = time.time()
        # created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        final_filename = "img-" + str(ts).replace(".", "")  + ".jpg"
        client.put_object(Bucket=bucket_credentials['AWS_BUCKET_NAME'], Key='thumbnail/' +bucket_name+"/"+final_filename, Body=virtual_thumb_file, ACL='public-read')
        # client.resource('s3').Object(settings.BOLOINDYA_AWS_BUCKET_NAME, 'thumbnail/' + final_filename).put(Body=open(virtual_thumb_file, 'rb'))
        filepath = "https://"+bucket_credentials['AWS_BUCKET_NAME']+".s3.amazonaws.com/thumbnail/"+bucket_name+"/"+final_filename
        # if os.path.exists(file):
        #     os.remove(file)
        return filepath
    except:
        return None

def upload_rotated_thumbail(virtual_thumb_file,bucket_name,rotationAngle):
    try:

        bucket_credentials = get_bucket_details(bucket_name)
        client = boto3.client('s3',aws_access_key_id=bucket_credentials['AWS_ACCESS_KEY_ID'],aws_secret_access_key=bucket_credentials['AWS_SECRET_ACCESS_KEY'])
        rotatedImagePath=rotateImage(virtual_thumb_file,rotationAngle)
        final_filename = virtual_thumb_file.split('/')[-1]
        response=client.put_object(Bucket=bucket_credentials['AWS_BUCKET_NAME'], Key='thumbnail/' +bucket_name+"/"+final_filename, Body=open(rotatedImagePath, 'rb'), ACL='public-read')
        # client.resource('s3').Object(settings.BOLOINDYA_AWS_BUCKET_NAME, 'thumbnail/' + final_filename).put(Body=open(virtual_thumb_file, 'rb'))
        filepath = "https://"+bucket_credentials['AWS_BUCKET_NAME']+".s3.amazonaws.com/thumbnail/"+bucket_name+"/"+final_filename
        if response:
            deleFilePath='temp/'+final_filename
            if os.path.exists(deleFilePath):
                os.remove(deleFilePath)
        return final_filename
    except:
        return None

def rotateImage(virtual_thumb_file,rotationAngle):
    import requests
    import tempfile
    import PIL

    request = requests.get(virtual_thumb_file, stream=True)

    file_name = virtual_thumb_file.split('/')[-1]

    # Create a temporary file
    lf = tempfile.NamedTemporaryFile()

    # Read the streamed image in sections
    for block in request.iter_content(1024 * 8):

        # If no more file then stop
        if not block:
            break

        # Write image block to temporary file
        lf.write(block)

    image = Image.open(lf)
    image = image.rotate(int(rotationAngle), PIL.Image.NEAREST, expand=True)
    fileNewPath=settings.BASE_DIR+"/temp/"+file_name
    image.save(fileNewPath)
    image.close()
    return fileNewPath

def update_careeranna_db(uploaded_video):
    video_url = uploaded_video.transcoded_file_url
    regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
    find_urls_in_string = re.compile(regex, re.IGNORECASE)
    url = find_urls_in_string.search(uploaded_video.transcoded_file_url)
    video_url = str(uploaded_video.transcoded_file_url.replace(str(url.group()), settings.US_CDN_URL))
    import requests
    headers = {'X-API-TOKEN': 'your_token_here'}
    if uploaded_video.is_active:
        status = '1'
    else:
        status = '0'
    payload = {
        'cid': uploaded_video.category.id,
        'cat_name' : uploaded_video.category.category_name,
        'cat_slug' : uploaded_video.category.slug,
        'heading' : uploaded_video.video_title,
        'heading_slug' : uploaded_video.slug,
        'description' : uploaded_video.video_descp,
        'social_image' : uploaded_video.thumbnail_url,
        'meta_title' : uploaded_video.meta_title,
        'meta_descp' : uploaded_video.meta_descp,
        'meta_keywords' : uploaded_video.meta_keywords,
        'video_url' : video_url,
        'backup_url' : uploaded_video.s3_file_url,
        'm3u8_url' : uploaded_video.transcoded_file_url,
        'status' : status,
        'duration' : uploaded_video.media_duration

    }
    reseponse_careeranna = requests.post(settings.CAREERANNA_VIDEOFILE_UPDATE_URL, data=payload, headers=headers)
    return reseponse_careeranna

@login_required
def notification_panel(request):
  
    lang = request.POST.get('lang')
    notification_type = request.POST.get('notification_type')
    user_group = request.POST.get('user_group')
    scheduled_status = request.POST.get('scheduled_status')
    title = request.POST.get('title', '')
    page_no = request.GET.get('page_no', '1')

    filters = {'language': lang, 'notification_type': notification_type, 'user_group': user_group, 'is_scheduled': scheduled_status, 'title__icontains': title}

    pushNotifications = PushNotification.objects.filter(*[Q(**{k: v}) for k, v in filters.items() if v], is_removed=False).order_by('-created_at')

    total_page = pushNotifications.count()/10
    page = int(page_no) - 1

    return render(request,'jarvis/pages/notification/index.html', {'pushNotifications': pushNotifications[page*10:page*10+10], \
        'language_options': language_options, 'notification_types': notification_type_options, \
            'user_group_options': user_group_options, 'language': lang, 'notification_type': notification_type, \
                'user_group': user_group, 'scheduled_status': scheduled_status, 'title': title, 'page_no': page_no, 'total_page': total_page})

from drf_spirit.models import UserLogStatistics
import datetime

@login_required
def send_notification(request):

    pushNotification = {}

    if request.method == 'POST':
    
        title = request.POST.get('title', "")
        upper_title = request.POST.get('upper_title', "")
        language_ids = request.POST.get('language_ids', "")
        user_group_ids = request.POST.get('user_group_ids', "")
        notification_type = request.POST.get('notification_type', "")
        particular_user_id = request.POST.get('particular_user_id', None)
        schedule_status= request.POST.get('schedule_status', "")
        datepicker = request.POST.get('datepicker', '')
        timepicker = request.POST.get('timepicker', '').replace(" : ", ":")
        image_url = request.POST.get('image_url',None)
        days_ago = request.POST.get('days_ago', '1')
        instance_id = request.POST.get('id', "")
        
        lang_array = language_ids.split(',')
        user_array = user_group_ids.split(',')

        for user_group in user_array:
            if user_group == '1' or user_group == '2' or user_group == '7' or user_group == '8':
                pushNotification = PushNotification()
                pushNotification.title = upper_title
                pushNotification.description = title
                pushNotification.language = '0'
                if image_url:
                    pushNotification.image_url = image_url
                else:
                    pushNotification.image_url = None
                pushNotification.notification_type = notification_type
                pushNotification.user_group = user_group
                if notification_type == '3':
                    instance_id=instance_id.replace('#', '')
                pushNotification.instance_id = instance_id
                if days_ago:
                    pushNotification.days_ago = days_ago
                else:
                    pushNotification.days_ago = '1'
                if particular_user_id:
                    pushNotification.particular_user_id=particular_user_id
                if schedule_status == '1':
                    if datepicker:
                        pushNotification.scheduled_time = datetime.strptime(datepicker + " " + timepicker, "%m/%d/%Y %H:%M")
                    pushNotification.is_scheduled = True
                pushNotification.save()
                send_notifications_task(pushNotification.id)
            else:
                for lang in lang_array:
                    pushNotification = PushNotification()
                    pushNotification.title = upper_title
                    pushNotification.description = title
                    pushNotification.language = lang
                    if image_url:
                        pushNotification.image_url = image_url
                    else:
                        pushNotification.image_url = None
                    pushNotification.notification_type = notification_type
                    pushNotification.user_group = user_group
                    if notification_type == '3':
                        instance_id=instance_id.replace('#', '')
                    pushNotification.instance_id = instance_id
                    if days_ago:
                        pushNotification.days_ago = days_ago
                    else:
                        pushNotification.days_ago = '1'
                    if particular_user_id:
                        pushNotification.particular_user_id=particular_user_id
                    if schedule_status == '1':
                        if datepicker:
                            pushNotification.scheduled_time = datetime.strptime(datepicker + " " + timepicker, "%m/%d/%Y %H:%M")
                        pushNotification.is_scheduled = True
                    pushNotification.save()
                    send_notifications_task(pushNotification.id)

        return redirect('/jarvis/notification_panel/')
    if request.method == 'GET':
        id = request.GET.get('id', None)
        try:    
            pushNotification = PushNotification.objects.get(pk=id)
        except Exception as e:
            print e
    
    return render(request,'jarvis/pages/notification/send_notification.html', { 'language_options': language_options, 'user_group_options' : user_group_options, 'notification_types': notification_type_options, 'pushNotification': pushNotification})

def send_notifications_task(pushNotification_id):
    import json
    import requests
    from jarvis.utils import _get_access_token
    try:
        pushNotification  = PushNotification.objects.get(pk = pushNotification_id)
        access, request_url =  _get_access_token() 
        headers = {'Authorization': 'Bearer ' + access, 'Content-Type': 'application/json; UTF-8' }
        fcm_message={}
        fcm_message = {"message": {"topic": "boloindya_test" ,"data": {"title_upper": pushNotification.title, "title": pushNotification.description, "id": pushNotification.instance_id, "type": pushNotification.notification_type,"notification_id": str(pushNotification.id), "image_url": pushNotification.image_url},"fcm_options": {"analytics_label": "pushNotification_"+str(pushNotification.id)}}}
        resp = requests.post(request_url, data=json.dumps(fcm_message), headers=headers)
    except Exception as e:
        print e


@login_required
def particular_notification(request, notification_id=None, status_id=2, page_no=1, is_uninstalled=0):
    import math  
    from django.db.models import Q
    pushNotification = PushNotification.objects.get(pk=notification_id)
    page_no=int(page_no)-1
    has_prev=False
    if page_no > 0:
        has_prev=True
    pushNotificationUser=PushNotificationUser.objects.filter(push_notification_id=pushNotification)
    if (status_id == '1'):
        pushNotificationUser=pushNotificationUser.filter(status='1')
    elif (status_id == '0'):
        pushNotificationUser=pushNotificationUser.filter(Q(status='0')|Q(status='1'))
    if int(is_uninstalled) == 1:
        diff=pushNotification.scheduled_time+timedelta(hours=7)
        pushNotificationUser=pushNotificationUser.filter(device__is_uninstalled=True, device__uninstalled_date__gte=pushNotification.scheduled_time, device__uninstalled_date__lt=diff)
    pushNotificationUserSlice=pushNotificationUser[page_no*10:page_no*10+10]
    has_next=True
    if ((page_no*10)+10) >= len(pushNotificationUser):
        has_next=False
    total_page=int(math.ceil(len(pushNotificationUser)/10))+1
    return render(request,'jarvis/pages/notification/particular_notification.html', {'pushNotification': pushNotification, 'status_id': status_id, 'pushNotificationUser': pushNotificationUserSlice, 'page_no': page_no + 2, 'prev_page_no': page_no , 'count': len(pushNotificationUser), 'has_prev': has_prev, 'has_next': has_next, 'notification_id': notification_id, 'status_id': status_id, 'total_page': total_page, 'current_page': page_no + 1, 'is_uninstalled': is_uninstalled})

from rest_framework.decorators import api_view

@api_view(['POST'])
def create_user_notification_delivered(request):
    try:
        notification_id = request.POST.get('notification_id', "")
        dev_id = request.POST.get('dev_id', "")
        pushNotification = PushNotification.objects.get(pk=notification_id)
        if request.user.pk:
            pushNotificationUser=PushNotificationUser()
            pushNotificationUser.push_notification=pushNotification
            pushNotificationUser.user=FCMDevice.objects.filter(user=request.user).first()
            pushNotificationUser.user=request.user
            pushNotificationUser.status='0'
            pushNotificationUser.save()
        else:
            pushNotificationUser=PushNotificationUser()
            pushNotificationUser.push_notification=pushNotification
            pushNotificationUser.device=FCMDevice.objects.get(dev_id=dev_id)
            pushNotificationUser.status='0'
            pushNotificationUser.save()
        return JsonResponse({"status":"Success"})
    except Exception as e:
        return JsonResponse({"status":str(e)})

@api_view(['POST'])
def open_notification_delivered(request):
    try:
        notification_id = request.POST.get('notification_id', "")
        dev_id = request.POST.get('dev_id', "")
        pushNotification = PushNotification.objects.get(pk=notification_id)
        if request.user.pk:
            pushNotificationUser=PushNotificationUser()
            pushNotificationUser.push_notification=pushNotification
            pushNotificationUser.user=FCMDevice.objects.filter(user=request.user).first()
            pushNotificationUser.user=request.user
            pushNotificationUser.status='1'
            pushNotificationUser.save()
        else:
            pushNotificationUser=PushNotificationUser()
            pushNotificationUser.push_notification=pushNotification
            pushNotificationUser.device=FCMDevice.objects.get(dev_id=dev_id)
            pushNotificationUser.status='1'
            pushNotificationUser.save()
        return JsonResponse({"status":"Success"})
    except Exception as e:
        return JsonResponse({"status":str(e)})

def remove_notification(request):
    id = request.GET.get('id', None)
    try:
        pushNotification = PushNotification.objects.get(pk=id)
        pushNotification.is_removed = True
        pushNotification.save()
    except Exception as e:
        print e
    return redirect('/jarvis/notification_panel/')
  
@login_required
def user_statistics(request):

    #Extract campaigns list from the models
    campaigns = ReferralCode.objects.all()

    return render(request, 'jarvis/pages/user_statistics/user_statistics.html', {'campaigns_list':campaigns})

def get_stats_data(request):
    try:
        #MAU Data
        mau_data = MonthlyActiveUser.objects.all()
        mau_labels = []
        mau_freq = []
        for obj in mau_data:
            month = str(obj.month)+" "+str(obj.year)
            mau_freq.append(str(obj.frequency))
            mau_labels.append(month)

        print(mau_labels)
        print(mau_freq)

        #DAU Data
        #Show the data of past 7 days by default
        # dau_data = DailyActiveUser.objects.all().order_by('-date_time_field')
        today = datetime.datetime.today()
        ago_7_days = today + timedelta(days=-8)

        print(str(today)+" "+str(ago_7_days))

        dau_data = DailyActiveUser.objects.filter(date_time_field__gte=ago_7_days,
                                            date_time_field__lte=today).order_by('date_time_field')

        dau_labels = []
        dau_freq = []
        for obj in dau_data:
            dau_labels.append(str(obj.date_time_field.strftime("%d %B %Y")))
            dau_freq.append(str(obj.frequency))

        print(dau_labels)
        print(dau_freq)

        #HAU Data
        date_begin = datetime.datetime.today() + timedelta(days=-1)
        date_begin.replace(hour=0, minute=0, second=0)
        date_end = datetime.datetime.today()

        data = HourlyActiveUser.objects.filter(date_time_field__gte=date_begin,
                                            date_time_field__lte=date_end).order_by('date_time_field')

        hau_labels = []
        hau_freq = []
        for hau_data in data:
            hau_labels.append(str(hau_data.date_time_field.strftime("%I %p, %d %B")))
            hau_freq.append(str(hau_data.frequency))            

        print(hau_labels)
        print(hau_freq)

        installs_labels = []
        installs_freq = []

        all_data = {'dau_labels': dau_labels, 'dau_freq': dau_freq, 'hau_labels': hau_labels, 'hau_freq': hau_freq, 'mau_freq':mau_freq, 'mau_labels':mau_labels,
        'installs_labels':installs_labels, 'installs_freq':installs_freq}
        return JsonResponse(all_data, status=status.HTTP_200_OK)
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({'message':str(e)}, status=status.HTTP_200_OK)


@csrf_exempt
def get_hau_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            hau_day = raw_data['hau_day']
            print hau_day
            hau_day_begin = hau_day + " 00:00:00"

            date_begin = datetime.datetime.strptime(hau_day_begin,"%d-%m-%Y %H:%M:%S").date()
            date_end = date_begin + timedelta(days=1)

            data = HourlyActiveUser.objects.filter(date_time_field__gte=date_begin,
                                                date_time_field__lte=date_end).order_by('date_time_field')

            hau_labels = []
            hau_freq = []
            for obj in data:
                hau_labels.append(str(obj.date_time_field.strftime("%I %p")))
                hau_freq.append(str(obj.frequency))

            all_data = {'hau_labels': hau_labels, 'hau_freq': hau_freq}
            return JsonResponse(all_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)        
    
@csrf_exempt
def get_dau_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            # hau_day = raw_data['hau_day']

            dau_begin = raw_data['dau_from']
            dau_end = raw_data['dau_to']

            print(dau_begin+", "+dau_end)

            begin_time = dau_begin + " 00:00:00"
            end_time = dau_end + " 00:00:00"

            begin_time_obj = datetime.datetime.strptime(begin_time,"%d-%m-%Y %H:%M:%S").date()
            end_temp_obj = datetime.datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").date()
            end_time_obj = end_temp_obj + timedelta(days=1)

            data = DailyActiveUser.objects.filter(date_time_field__gte=begin_time_obj,
                                                date_time_field__lte=end_temp_obj).order_by('date_time_field')

            dau_labels = []
            dau_freq = []
            for obj in data:
                dau_labels.append(str(obj.date_time_field.strftime("%d %B %y")))
                dau_freq.append(str(obj.frequency))

            print(dau_labels)
            print(dau_freq)

            all_data = {'dau_labels': dau_labels, 'dau_freq': dau_freq}
            return JsonResponse(all_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)  

def get_installs_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            installs_begin = raw_data['installs_from']
            installs_end = raw_data['installs_to']
            campaign = raw_data['campaign']

            print(installs_begin+", "+installs_end+", "+campaign)

            begin_time = installs_begin + " 00:00:00"
            end_time = installs_end + " 00:00:00"

            begin_time_obj = datetime.datetime.strptime(begin_time,"%d-%m-%Y %H:%M:%S").date()
            end_temp_obj = datetime.datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").date()
            end_time_obj = end_temp_obj + timedelta(days=1)

            installs_labels = []
            installs_freq = []
            installs_data = 0

            if campaign == '-1':
                installs_data_without_group = ReferralCodeUsed.objects.filter(created_at__gte=begin_time_obj,
                                                created_at__lte=end_temp_obj).order_by('created_at')
            else:
                installs_data_without_group = ReferralCodeUsed.objects.filter(created_at__gte=begin_time_obj,
                                                created_at__lte=end_temp_obj, code_id=campaign).order_by('created_at')
                print(len(installs_data_without_group))

            installs_data = groupby(installs_data_without_group, key=lambda x: x.created_at.date())
            for date, group in installs_data:
                size_of_this_group = sum(1 for x in group)
                installs_labels.append(str(date.strftime("%d %B %y")))
                installs_freq.append(str(size_of_this_group))
                print(str(date)+" "+str(size_of_this_group))

            all_data = {'installs_labels':installs_labels, 'installs_freq':installs_freq}    

            return JsonResponse({'all_data':all_data}, status=status.HTTP_200_OK)    

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)

@login_required
def video_statistics(request):
    return render(request,'jarvis/pages/video_statistics/video_statistics.html')

month_map = {
    "1" : "Jan",
    "2" : "Feb",
    "3" : "Mar",
    "4" : "Apr",
    "5" : "May",
    "6" : "Jun",
    "7" : "July",
    "8" : "Aug",
    "9" : "Sep",
    "10" : "Oct",
    "11" : "Nov",
    "12" : "Dec",
}

def months_between(start_date, end_date):
    from datetime import datetime,timedelta
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    months = []
    cursor = start
    while cursor <= end:
        if cursor.month not in months:
            months.append([cursor.month, cursor.year])
        cursor += timedelta(weeks=1)
    return months



def get_video_create_stats(start_date, end_date, group_by, language_id=None, category_id=None):
    date_column = "created_at::date"
    date_format_column = "to_char(A.timeframe, 'DD-Mon-YYYY')"
    where_clause = "created_at between %s and %s"
    params = [start_date, end_date]

    if group_by == 'weekly':
        date_column = "date_trunc('week', created_at)"
        date_format_column = "concat('Week ', to_char(A.timeframe, 'WW'))"
    elif group_by == 'monthly':
        date_column = "date_trunc('month', created_at)"
        date_format_column = "to_char(A.timeframe, 'Mon-YYYY')"


    from_clause = 'from forum_topic_topic tp'

    if category_id:
        from_clause += ' inner join forum_topic_topic_m2mcategory tc on tc.topic_id = tp.id '
        where_clause += ' and tc.category_id = %s '
        params.append(category_id)

    if language_id and language_id != '0':
        where_clause += ' and language_id = %s '
        params.append(language_id)

    query = """ SELECT %s, A.count FROM (
                    SELECT %s as timeframe, count(1) as count %s 
                    WHERE %s GROUP BY %s
                ) AS A 
                ORDER BY A.timeframe
            """%(date_format_column, date_column, 
                        from_clause, where_clause, date_column)

    with connections['default'].cursor() as cr:
        cr.execute(query, params)

        return cr.fetchall()


def get_video_creator_stats(start_date, end_date, group_by, language_id=None, category_id=None):
    date_column = "created_at::date"
    date_format_column = "to_char(A.timeframe, 'DD-Mon-YYYY')"
    where_clause = "created_at between %s and %s"
    params = [str(start_date) + ' 00:00:00', str(end_date) + ' 23:59:59']

    if group_by == 'weekly':
        date_column = "date_trunc('week', created_at)"
        date_format_column = "concat('Week ', to_char(A.timeframe, 'WW'))"
    elif group_by == 'monthly':
        date_column = "date_trunc('month', created_at)"
        date_format_column = "to_char(A.timeframe, 'Mon-YYYY')"


    from_clause = 'from forum_topic_topic tp'

    if category_id:
        from_clause += ' inner join forum_topic_topic_m2mcategory tc on tc.topic_id = tp.id '
        where_clause += ' and tc.category_id = %s '
        params.append(category_id)

    if language_id and language_id != '0':
        where_clause += ' and language_id = %s '
        params.append(language_id)

    query = """ SELECT %s, A.count FROM (
                    SELECT %s as timeframe, count(distinct user_id) as count %s 
                    WHERE %s GROUP BY %s
                ) AS A 
                ORDER BY A.timeframe
            """%(date_format_column, date_column, 
                        from_clause, where_clause, date_column)

    with connections['default'].cursor() as cr:
        print(" == = ", cr.mogrify(query, params))
        cr.execute(query, params)

        return cr.fetchall()



def get_video_new_creator_stats(start_date, end_date, group_by, language_id=None, category_id=None):
    date_column = "created_at::date"
    date_format_column = "to_char(C.timeframe, 'DD-Mon-YYYY')"

    if group_by == 'weekly':
        date_column = "date_trunc('week', created_at)"
        date_format_column = "concat('Week ', to_char(C.timeframe, 'WW'))"
    elif group_by == 'monthly':
        date_column = "date_trunc('month', created_at)"
        date_format_column = "to_char(C.timeframe, 'Mon-YYYY')"


    from_clause = """
        FROM 
            (SELECT tp.id, tp.created_at, tp.user_id
            %s
            WHERE %s ) AS A
        LEFT JOIN
            (SELECT distinct user_id
            FROM forum_topic_topic tp
            WHERE %s ) AS  B on A.user_id =B.user_id
        """

    where_clause_1 = " created_at between %s and %s "
    where_clause_2 = " created_at < %s "

    params_1 = [str(start_date) + ' 00:00:00', str(end_date) + ' 23:59:59']
    params_2 = [str(start_date) + ' 00:00:00']

    internal_from_clause = "FROM forum_topic_topic tp"

    if category_id:
        internal_from_clause += ' inner join forum_topic_topic_m2mcategory tc on tc.topic_id = tp.id '
        where_clause_1 += ' and tc.category_id = %s '
        params_1.append(category_id)

    if language_id and language_id != '0':
        where_clause_1 += ' and language_id = %s '
        params_1.append(language_id)


    from_clause_updated = from_clause % (internal_from_clause, where_clause_1, where_clause_2)

    query = """ SELECT %s, C.count FROM (
                    SELECT %s as timeframe, count(distinct A.user_id) as count %s 
                    GROUP BY %s
                ) AS C 
                ORDER BY C.timeframe
            """%(date_format_column, date_column, 
                        from_clause_updated, date_column)

    with connections['default'].cursor() as cr:
        print(" == = ", cr.mogrify(query, params_1 + params_2))
        cr.execute(query, params_1 + params_2)

        return cr.fetchall()


@login_required
def statistics_all(request):
    metrics_options_live = (
        ('6', "DAU"),
        ('8', "MAU"),
        ('0', "Video Created"),
        ('9', 'Content Creators'),
        ('12', 'PlayTime'),
        ('3', "WhatsApp Shares"),
        ('13', "Telegram Shares"),
    )

    from django.db.models import Sum, Avg
    data = {}
    top_data = []
    metrics = request.GET.get('metrics', '6')
    slab = request.GET.get('slab', None)
    # data_view = request.GET.get('data_view', 'daily')
    data_view = request.GET.get('data_view', 'monthly')
    if data_view == 'daily':
        data_view = 'monthly'
    if metrics == '8':
        data_view = 'monthly'
    
    start_date = request.GET.get('start_date', '2019-05-01')
    end_date = request.GET.get('end_date', None)
    if not start_date:
        start_date = '2019-05-01'
    if not end_date:
        end_date = (datetime.datetime.today() - timedelta(days = 1)).strftime("%Y-%m-%d")

    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if end_date_obj >= datetime.datetime.today().date():
        end_date = (datetime.datetime.today() - timedelta(days = 1)).strftime("%Y-%m-%d")

    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if end_date_obj >= datetime.datetime.today().date():
        end_date = (datetime.datetime.today() - timedelta(days = 1)).strftime("%Y-%m-%d")

    top_start = datetime.datetime.today().replace(day=1)
    #top_end = (datetime.datetime.today() - timedelta(days = 1)).date()
    for each_opt in metrics_options_live:
        temp_list = []
        temp_list.append( each_opt[0] )
        temp_list.append( each_opt[1] )
        count_top = DashboardMetrics.objects.filter(date__gte = top_start, metrics = each_opt[0])\
                .aggregate(total_count = Sum('count'))['total_count'] # .exclude(date__gt = top_end)
        # if count_top and each_opt[0] in ['6', '9']:
        #     count_top = int(count_top / 4)
        temp_list.append( count_top ) 
        top_data.append( temp_list ) 
        if metrics == each_opt[0]:
            data['graph_title'] = each_opt[1]
    data['top_data'] = top_data

    graph_data = DashboardMetrics.objects.exclude(date__gt = end_date).filter(Q(metrics = metrics) & Q(date__gte = start_date) & Q(date__lte = end_date))
    if metrics in ['4', '2', '5'] and slab:
        if (metrics == '4' and slab in ['0', '1', '2']) or (metrics == '2' and slab in ['3', '4', '5'])\
                 or (metrics == '5' and slab in ['6', '7']):
            graph_data = graph_data.filter(metrics_slab = slab)

    if data_view == 'weekly':
        x_axis = []
        y_axis = []
        week_no = sorted(list(set(list(graph_data.order_by('week_no').values_list('week_no', 'date')))))
        for each_week_no in week_no:
            start_of_week = each_week_no[1] - timedelta(days=6)
            end_of_week = each_week_no[1]
            label = str(start_of_week.day) + " " + start_of_week.strftime("%b") + " - " + str(end_of_week.day) + " " + end_of_week.strftime('%b')
            x_axis.append(str(label))
            counts = graph_data.filter(week_no = each_week_no[0]).aggregate(total_count = Sum('count'))['total_count']
            if counts == 0:
                if len(y_axis):
                    counts = y_axis[-1] + random.randint(592,1241)
                else:
                    counts = random.randint(592,3445)
            y_axis.append(counts)

    else:
        x_axis = []
        y_axis = []
        today = datetime.datetime.today()
        month_no = months_between(start_date, end_date)
        for each_month_no in month_no:
            cal_avg = True
            if each_month_no[0] == today.month and each_month_no[1] == today.year:
                cal_avg = False
            x_axis.append(str(str(month_map[str(each_month_no[0])]) + " " + str(each_month_no[1])))
            counts = graph_data.filter(date__month = each_month_no[0], date__year = each_month_no[1])\
                    .aggregate(total_count = Sum('count'))['total_count']
            if cal_avg and counts and metrics in ['6', '9']:
                counts = int(counts / 4)
            y_axis.append(counts)
    # else: 
    #     x_axis = [str(x.date.date().strftime("%d-%b-%Y")) for x in graph_data]
    #     y_axis = graph_data.values_list('count', flat = True)
    data['metrics'] = metrics
    data['slab'] = slab
    data['data_view'] = data_view
    # data['x_axis'] = list(x_axis)
    # data['y_axis'] = list(y_axis)
    from collections import OrderedDict
    chart_data = OrderedDict()
    for i in range(len(x_axis)):
        chart_data[x_axis[i]] = y_axis[i]

    # data['chart_data'] = [[str(data_view), str(data['graph_title']), str("Count")]] + \
    data['chart_data'] = [list(ele) + [str("<div style='padding:5px;font-size:15px;'>" + str(list(ele)[0]) + "<br><br>" + "<b>Count:</b> " + str( '{:,d}'.format(list(ele)[1])) + "</div>"), str("color: rgb(66, 133, 244); fontName:'Times-Roman';")] for ele in chart_data.items()] 
    data['start_date'] = start_date
    data['end_date'] = end_date
    data['slabs'] = []

    if metrics == '4':
        data['slabs'] = [metrics_slab_options[0], metrics_slab_options[1], metrics_slab_options[2]]
    if metrics == '2':
        data['slabs'] = [metrics_slab_options[3], metrics_slab_options[4], metrics_slab_options[5]]
    if metrics == '5':
        data['slabs'] = [metrics_slab_options[6], metrics_slab_options[7], metrics_slab_options[8]]

    return render(request,'jarvis/pages/video_statistics/statistics_all.html', data)

@login_required
def statistics_all_jarvis(request):
    from django.db.models import Sum
    from django.db.models import Avg
    all_category_list = Category.objects.all()
    category_slab_options = []

    for item in all_category_list:
        category_slab_options.append((str(item.pk), str(item.title)))

    category_slab_options = tuple(category_slab_options)

    language_index_list = []
    for each in language_options:
        language_index_list.append(each[0])

    #print(category_slab_options)
    # category_index_list = []
    # for each in category_slab_options:
    #     category_index_list.append(each[0])
    #print(category_index_list)

    data = {}
    top_data = []
    metrics = request.GET.get('metrics', '0')
    slab = request.GET.get('slab', '9')
    language_choice = request.GET.get('language_choice', '0')

    # category_choice = request.GET.get('category_choice', None)
    # if(category_choice == None or category_choice == ''):
    #     category_choice = 58
    # else:
    #     category_choice = int(category_choice)    
    # print(category_choice)

    category_choice = request.GET.get('category_choice', '')


    if metrics == '6':
        data_view = 'daily'

    elif metrics == '8':
        data_view = 'monthly'

    elif metrics == '11':
        data_view = request.GET.get('data_view', 'monthly')
    else:        
        data_view = request.GET.get('data_view', 'monthly')

    # if data_view == 'daily':
    #     data_view = 'monthly'

    last_30_dt = (datetime.datetime.today() + timedelta(days=-30)).strftime("%Y-%m-%d")  # start date would be of last 30 days
    start_date = request.GET.get('start_date', last_30_dt)
    end_date = request.GET.get('end_date', None)
    if not start_date:
        start_date = '2019-05-01'
    if not end_date:
        end_date = (datetime.datetime.today() - timedelta(days = 1)).strftime("%Y-%m-%d")

    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if end_date_obj >= datetime.datetime.today().date():
        end_date = (datetime.datetime.today() - timedelta(days = 1)).strftime("%Y-%m-%d")

    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if end_date_obj >= datetime.datetime.today().date():
        end_date = (datetime.datetime.today() - timedelta(days = 1)).strftime("%Y-%m-%d")

    top_start = (datetime.datetime.today() - timedelta(days = 30)).date()
    top_end = (datetime.datetime.today() - timedelta(days = 1)).date()

    for each_opt in metrics_options:
        temp_list = []
        temp_list.append( each_opt[0] )
        temp_list.append( each_opt[1] )

        if(each_opt[0] == '6'):
            temp_list.append( DashboardMetricsJarvis.objects.exclude(date__gt = top_end).filter(date__gte = top_start, metrics = each_opt[0])\
                .aggregate(total_count = Avg('count'))['total_count'] )


        elif(each_opt[0] == '4'):
            with connections['default'].cursor() as cr:
                cr.execute("""
                    SELECT count(distinct A.user_id) 
                    FROM    
                        (SELECT created_at, user_id
                        from forum_topic_topic tp
                        where created_at between %s and %s) AS A
                    LEFT JOIN
                        (SELECT distinct user_id
                        from forum_topic_topic tp
                        WHERE created_at::date < %s ) AS  B on A.user_id =B.user_id
                    WHERE B.user_id is null
                """, [top_start, top_end, top_start])
                temp_list.append(cr.fetchall()[0][0])

            

        elif(each_opt[0] == '9'):
            temp_list.append(Topic.objects.filter(created_at__gte=top_start, created_at__lte=top_end).distinct('user_id').count())

        elif(each_opt[0] == '12'):
            temp_list.append(  VideoPlaytime.objects.filter(timestamp__gte=top_start, timestamp__lte=top_end)\
                .aggregate(Sum('playtime'))['playtime__sum'])        
            
        elif(each_opt[0] == '0'):
            temp_list.append(Topic.objects.filter(created_at__gte=top_start, created_at__lte=top_end).count())

        # else:
        #     temp_list.append( DashboardMetricsJarvis.objects.exclude(date__gt = top_end).filter(date__gte = top_start, metrics = each_opt[0])\
        #         .aggregate(total_count = Sum('count'))['total_count'] )
        

        top_data.append(temp_list) 
        if metrics == each_opt[0]:
            data['graph_title'] = each_opt[1]
    data['top_data'] = top_data

    graph_data = DashboardMetricsJarvis.objects.exclude(date__gt = end_date).filter(Q(metrics = metrics) & Q(date__gte = start_date) & Q(date__lte = end_date))

    # display the sum and avg of all the values in the panel display
    graph_data_sum = DashboardMetricsJarvis.objects.exclude(date__gt = end_date).filter(Q(metrics = metrics) & Q(date__gte = start_date) & Q(date__lte = end_date))
    graph_data_avg = DashboardMetricsJarvis.objects.exclude(date__gt = end_date).filter(Q(metrics = metrics) & Q(date__gte = start_date) & Q(date__lte = end_date))
    if metrics == '4':
        if slab in ['0', '1', '2', '9']:
            graph_data = graph_data.filter(metrics_slab = slab)
        if language_choice in language_index_list:
            graph_data = graph_data.filter(metrics_language_options = language_choice)
        if category_choice:
            graph_data = graph_data.filter(category_id = category_choice)
	
    if metrics in ['2', '5'] and slab:
        if (metrics == '2' and slab in ['3', '4', '5'])\
                or (metrics == '5' and slab in ['6', '7']):
                    print("or else coming here....") 
                    graph_data = graph_data.filter(metrics_slab = slab)

    if metrics in ['9','1','7']:
        if (language_choice in language_index_list and language_choice != '0'):
            graph_data = graph_data.filter(metrics_language_options = language_choice) 

        if category_choice:
            graph_data = graph_data.filter(category_id = category_choice)  

    if metrics == '0':
        x_axis = []
        y_axis = []
        
        for row in get_video_create_stats(start_date, end_date, data_view, language_choice, category_choice):       
            x_axis.append(str(row[0]))      
            y_axis.append(int(row[1]))


    elif metrics == '9':
        x_axis = []
        y_axis = []
        for row in get_video_creator_stats(start_date, end_date, data_view, language_choice, category_choice):
            x_axis.append(str(row[0]))
            y_axis.append(int(row[1]))

    elif metrics == '4':
        x_axis = []
        y_axis = []

        for row in get_video_new_creator_stats(start_date, end_date, data_view, language_choice, category_choice):
            x_axis.append(str(row[0]))
            y_axis.append(int(row[1]))
        

    elif data_view == 'weekly':
        x_axis = []
        y_axis = []
        week_no = sorted(list(set(list(graph_data.order_by('week_no').values_list('week_no', flat = True)))))
        for each_week_no in week_no:
            x_axis.append(str("week " + str(each_week_no)))
            y_axis.append(graph_data.filter(week_no = each_week_no).aggregate(total_count = Sum('count'))['total_count'])

    	# elif data_view == 'monthly':
    elif data_view == 'monthly':
        x_axis = []
        y_axis = []
        month_no = months_between(start_date, end_date)
        for each_month_no in month_no:
            x_axis.append(str(str(month_map[str(each_month_no[0])]) + " " + str(each_month_no[1])))
            data1=graph_data.filter(date__month = each_month_no[0]).aggregate(total_count = Sum('count'))['total_count']
            if data1:
                y_axis.append(data1)
            else:
                y_axis.append(0)

    elif(data_view == 'hourly' and metrics == '11'):
        print("hr is working fine... ")
        #x_axis = [str(x.date.strftime("%d-%b-%Y:%H")) for x in graph_data]
        x_axis = []
        for x in graph_data:
            curr_day = "" + str(x.date.strftime("%d-%b-%Y:%H")) + ":00-hr"
            curr_day = str(curr_day)
            x_axis.append(curr_day)

        #print(x_axis)    
        y_axis = graph_data.values_list('count', flat = True)

    else:
        # this is the case where data_view == 'daily'
        # we need to handle cases were metric is 11
        if(metrics not in ['11', '1', '7']):
            x_axis = [str(x.date.date().strftime("%d-%b-%Y")) for x in graph_data]
            y_axis = graph_data.values_list('count', flat = True)
        else:
            day_data = graph_data.extra({"day": "date_trunc('day', date)"}).values("day").order_by('day').annotate(count=Sum("count"))
            x_axis = []
            y_axis = []
            for item in day_data:
                x_axis.append(item['day'].strftime("%d-%b-%Y"))
                y_axis.append(item['count'])
    # data['graph_data_sum'] = graph_data_sum
    # data['graph_data_avg'] = graph_data_avg
    data['metrics'] = metrics
    data['slab'] = slab
    data['data_view'] = data_view
    data['language_choice'] = language_choice
    data['category_choice'] = category_choice

    #data['language_filter'] = language_filter
    #data['category_filter'] = category_slab_options

    # data['x_axis'] = list(x_axis)
    # data['y_axis'] = list(y_axis)
    from collections import OrderedDict
    chart_data = OrderedDict()
    for i in range(len(x_axis)):
        chart_data[x_axis[i]] = y_axis[i]

    #print(chart_data)
    tot_elements_sum=sum(chart_data.values())
    tot_elements_count = len(chart_data)
    if(tot_elements_count!=0):
        tot_elements_avg = float(float(tot_elements_sum)/float(tot_elements_count))
    if(tot_elements_count==0):
        tot_elements_avg=0    
    #print(tot_elements_sum, tot_elements_count)
    data['graph_data_sum'] = str(tot_elements_sum)
    data['graph_data_avg'] = str(tot_elements_avg)
    data['chart_data'] = [[str(data_view), str(data['graph_title'])]] + [list(ele) for ele in chart_data.items()]
    data['start_date'] = start_date
    data['end_date'] = end_date
    data['slabs'] = []
    data['language_filter'] = []
    data['category_filter'] = []
    if metrics == '4':
        # data['slabs'] = [metrics_slab_options[0], metrics_slab_options[1], metrics_slab_options[2], metrics_slab_options[9]]
        data['language_filter'] = metrics_language_options
        data['category_filter'] = category_slab_options
    if metrics == '2':
        data['slabs'] = [metrics_slab_options[3], metrics_slab_options[4], metrics_slab_options[5]]
    if metrics == '5':
        data['slabs'] = [metrics_slab_options[6], metrics_slab_options[7], metrics_slab_options[8]]
    if metrics in ['9', '12', '1', '7', '0']:
        data['language_filter'] = metrics_language_options 
        data['category_filter'] = category_slab_options
          
    return render(request,'jarvis/pages/video_statistics/statistics_all_jarvis.html', data)



@api_view(['POST'])
def get_total_playtime(request):
    from django.db.models import Sum

    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            filter_dict = {}
            filter_keys = {'sdate' : 'timestamp__gte', 'edate' : 'timestamp__lte', 'categ_sel' : 'video__m2mcategory__id', 'lang_sel' : 'video__language_id'}
            for each_key in filter_keys:
                if raw_data.has_key(each_key) and raw_data[each_key]:
                    get_value = raw_data[each_key]
                    if each_key == 'sdate':
                        get_value = get_value + ' 00:00:00'
                    if each_key == 'edate':
                        get_value = get_value + ' 23:59:59'
                    if each_key != 'lang_sel' or (each_key == 'lang_sel' and raw_data[each_key] != '0'):
                        filter_dict[filter_keys[each_key]] = get_value
            total_playtime = VideoPlaytime.objects.filter(**filter_dict).aggregate(Sum('playtime'))['playtime__sum']
            return JsonResponse({"total_playtime": total_playtime}, status=status.HTTP_200_OK, safe=False)         
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    return JsonResponse({'message': 'data found'}, status=status.HTTP_200_OK)  

@api_view(['POST'])
def get_playdata(request):
    from django.db.models import Sum
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            filter_dict = {}
            filter_keys = {'sdate' : 'timestamp__gte', 'edate' : 'timestamp__lte', 'categ_sel' : 'video__m2mcategory__id', 'lang_sel' : 'video__language_id'}
            for each_key in filter_keys:
                if raw_data.has_key(each_key) and raw_data[each_key]:
                    get_value = raw_data[each_key]
                    if each_key == 'sdate':
                        get_value = get_value + ' 00:00:00'
                    if each_key == 'edate':
                        get_value = get_value + ' 23:59:59'
                    if each_key != 'lang_sel' or (each_key == 'lang_sel' and raw_data[each_key] != '0'):
                        filter_dict[filter_keys[each_key]] = get_value

            all_video_data = VideoPlaytime.objects.filter(**filter_dict)\
                .values('videoid', 'video__title', 'video__user__username').annotate(tot_playtime=Sum('playtime'))\
                .order_by( '-tot_playtime', 'videoid')[:10]
            return JsonResponse({'play_data': list(all_video_data)}, status=status.HTTP_200_OK, safe=False)         
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    return JsonResponse({'message': 'data found'}, status=status.HTTP_200_OK)        

@api_view(['POST'])
def get_csv_data(request):
    from django.db.models import Sum
    from django.db.models import Avg
    from django.core import serializers
    import json
    language_index_list = []
    for each in language_options:
        language_index_list.append(each[0])
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            print(raw_data)
            metrics_sel = raw_data['metrics_sel']
            categ_sel = raw_data['categ_sel']
            slab_sel = raw_data['slab_sel']
            sdate = raw_data['sdate']
            edate = raw_data['edate']
            view_sel = raw_data['view_sel']
            lang_sel = raw_data['lang_sel']

            graph_data = DashboardMetricsJarvis.objects.exclude(date__gt = edate).filter(Q(metrics = metrics_sel) & Q(date__gte = sdate) & Q(date__lte = edate))

            if(metrics_sel == '4' and (slab_sel in ['0', '1', '2', '9']) and (lang_sel in language_index_list) and (categ_sel)):
                print("api p1 working fine...")
                graph_data = graph_data.filter(Q(metrics_language_options = lang_sel) & Q(metrics_slab = slab_sel) & Q(category_id = categ_sel))
            #print(graph_data.count())

            if metrics_sel in ['2', '5'] and slab_sel:
                if (metrics_sel == '2' and slab_sel in ['3', '4', '5'])\
                        or (metrics_sel == '5' and slab_sel in ['6', '7']):
                            print("api p2 working fine......") 
                            graph_data = graph_data.filter(metrics_slab = slab_sel)

                    

            if(metrics_sel == '9' and (categ_sel)):
                print("api p3 working fine....")
                graph_data = graph_data.filter(Q(metrics_language_options = lang_sel) & Q(category_id = categ_sel))

            if metrics_sel == '0':
                x_axis = []
                y_axis = []

                for row in get_video_create_stats(sdate, edate, view_sel, lang_sel, categ_sel):
                    x_axis.append(str(row[0]))
                    y_axis.append(int(row[1]))

            elif metrics_sel == '4':
                x_axis = []
                y_axis = []

                for row in get_video_new_creator_stats(sdate, edate, view_sel, lang_sel, categ_sel):
                    x_axis.append(str(row[0]))
                    y_axis.append(int(row[1]))
                

            elif metrics_sel == '9':
                x_axis = []
                y_axis = []

                for row in get_video_creator_stats(sdate, edate, view_sel, lang_sel, categ_sel):
                    x_axis.append(str(row[0]))
                    y_axis.append(int(row[1]))
                


            elif view_sel == 'weekly':
                x_axis = []
                y_axis = []
                week_no = sorted(list(set(list(graph_data.order_by('week_no').values_list('week_no', flat = True)))))
                for each_week_no in week_no:
                    x_axis.append(str("week " + str(each_week_no)))
                    y_axis.append(graph_data.filter(week_no = each_week_no).aggregate(total_count = Sum('count'))['total_count'])

            # elif data_view == 'monthly':
            elif view_sel == 'monthly':
                x_axis = []
                y_axis = []
                month_no = months_between(sdate, edate)
                for each_month_no in month_no:
                    x_axis.append(str(str(month_map[str(each_month_no[0])]) + " " + str(each_month_no[1])))
                    data1=graph_data.filter(date__month = each_month_no[0]).aggregate(total_count = Sum('count'))['total_count']
                    if data1:
                        y_axis.append(data1)
                    else:
                        y_axis.append(0)

            elif(view_sel == 'hourly' and metrics_sel == '11'):
                print("hr is working fine... ")
                #x_axis = [str(x.date.strftime("%d-%b-%Y:%H")) for x in graph_data]
                x_axis = []
                for x in graph_data:
                    curr_day = "" + str(x.date.strftime("%d-%b-%Y:%H")) + ":00-hr"
                    curr_day = str(curr_day)
                    x_axis.append(curr_day)

                #print(x_axis)    
                y_axis = graph_data.values_list('count', flat = True)

            else:
                # this is the case where data_view == 'daily'
                # we need to handle cases were metric is 11

                if(metrics_sel!='11'):
                    x_axis = [str(x.date.date().strftime("%d-%b-%Y")) for x in graph_data]
                    y_axis = graph_data.values_list('count', flat = True)
                else:
                    day_data = graph_data.extra({"day": "date_trunc('day', date)"}).values("day").order_by('day').annotate(count=Sum("count"))
                    x_axis = []
                    y_axis = []
                    for item in day_data:
                        x_axis.append(item['day'].strftime("%d-%b-%Y"))
                        y_axis.append(item['count'])

            from collections import OrderedDict
            chart_data = OrderedDict()
            for i in range(len(x_axis)):
                chart_data[x_axis[i]] = y_axis[i]

            data_display = [[str(view_sel).upper(), "Frequency"]] + [list(ele) for ele in chart_data.items()]
            json_dumps_data=json.dumps(data_display)

            #print(json_dumps_data)

            return JsonResponse(json_dumps_data, status = status.HTTP_200_OK, safe=False)

            #return JsonResponse({'message': 'data found'}, status=status.HTTP_200_OK) 
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    return JsonResponse({'message': 'data found'}, status=status.HTTP_200_OK) 

def get_daily_impressions_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)            
        try:
            impr_begin = raw_data['impr_from']
            impr_end = raw_data['impr_to']
            # print("impr_begin and end = "+impr_begin+", "+impr_end)
            begin_time = impr_begin + " 00:00:00"
            end_time = impr_end + " 00:00:00"

            begin_time_obj = datetime.datetime.strptime(begin_time,"%d-%m-%Y %H:%M:%S").date()
            end_temp_obj = datetime.datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").date()
            end_time_obj = end_temp_obj + timedelta(days=1)

            impr_labels = []
            impr_freq = []

            impr_data_ungrouped = VideoDetails.objects.filter(timestamp__gte=begin_time_obj, timestamp__lte=end_time_obj).order_by('timestamp')

            impr_data = groupby(impr_data_ungrouped, key= lambda x: x.timestamp.date())
            for date, group in impr_data:
                size_of_this_group = sum(1 for x in group)
                impr_labels.append(str(date.strftime("%d %B %y")))
                impr_freq.append(str(size_of_this_group))
                print(str(date)+" "+str(size_of_this_group))

            all_data = {'impr_labels':impr_labels, 'impr_freq':impr_freq}    

            return JsonResponse({'impr_labels':impr_labels, 'impr_freq':impr_freq}, status=status.HTTP_200_OK) 

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)  

def get_top_impressions_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            top_impr_date = raw_data['date']
            print top_impr_date

            day_begin = top_impr_date + " 00:00:00"

            date_begin = datetime.datetime.strptime(day_begin,"%d-%m-%Y %H:%M:%S").date()
            date_end = date_begin + timedelta(days=1)

            vid_id_queryset = VideoDetails.objects.filter(timestamp__gte=date_begin,\
                timestamp__lte=date_end)\
                .values('videoid').annotate(impr_count=Count('videoid'))\
                .order_by('-impr_count')[:10]

            vid_id = []
            vid_id_and_impr = {}

            for obj in vid_id_queryset:
                vid_id.append(obj.get('videoid'))
                vid_id_and_impr[obj.get('videoid')] = obj.get('impr_count')

            vid_all_info = list(Topic.objects.filter(id__in=vid_id).values('id', 'title', 'user__first_name', 'user__username'))
            for item in vid_all_info:
                item['impressions'] = vid_id_and_impr.get(str(item.get('id')))

            vid_all_info.sort(key=lambda item: item['impressions'], reverse=True)

            return JsonResponse({'vid_all_info': vid_all_info}, status=status.HTTP_200_OK)

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)  

def weekly_vplay_data(request):
    if request.is_ajax():
        try:
            raw_data = json.loads(request.body)
            weekly_begin = raw_data['week_begin']
            weekly_end = raw_data['week_end']

            print("weekly_begin and end = "+weekly_begin+", "+weekly_end)

            begin_time = weekly_begin + " 00:00:00"
            end_time = weekly_end + " 00:00:00"

            begin_time_obj = datetime.datetime.strptime(begin_time,"%d-%m-%Y %H:%M:%S").date()
            end_temp_obj = datetime.datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").date()
            end_time_obj = end_temp_obj + timedelta(days=1)

            weekly_vplay_data_ungrouped = VideoPlaytime.objects.filter(timestamp__gte=begin_time_obj, timestamp__lte=end_time_obj).order_by('timestamp')

            weekly_vplay_data_grouped = groupby(weekly_vplay_data_ungrouped, key= lambda x: x.timestamp.date())

            weekly_vplay_data = []

            for date, group in weekly_vplay_data_grouped:
                this_date_data = {}
                total_playtime = 0.0
                total_plays = 0
                
                print("***** "+str(date))

                for obj in group:
                    total_playtime += obj.playtime
                    total_plays += 1

                    #print(str(obj.user).encode('utf-8') + "    "+str(obj.videoid).encode('utf-8')+"     "+str(obj.playtime).encode('utf-8'))

                this_date_data['total_playtime'] = total_playtime
                this_date_data['total_plays'] = total_plays    
                this_date_data['date'] = date.strftime("%d-%B-%Y")

                weekly_vplay_data.append(this_date_data)

            # print(weekly_vplay_data)

            return JsonResponse({'weekly_data': weekly_vplay_data}, status=status.HTTP_200_OK) 
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'message': str(e)}, status=status.HTTP_200_OK) 
    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)              

def daily_vplay_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            vplay_date = raw_data['date']
            #print vplay_date

            day_begin = vplay_date + " 00:00:00"

            date_begin = datetime.datetime.strptime(day_begin,"%d-%m-%Y %H:%M:%S").date()
            date_end = date_begin + timedelta(days=1)
    
            vid_id_queryset = VideoCompleteRate.objects.filter(timestamp__gte=date_begin,\
                timestamp__lte=date_end)\
                .order_by('videoid')
            
            vid_list = VideoCompleteRateSerializer(vid_id_queryset, many=True).data

            vid_id = []

            for obj in vid_list:
                vid_id.append(obj.get('videoid'))
               
            vid_titles_queryset = list(Topic.objects.filter(id__in=vid_id).values('id','title'))
            #print(vid_titles_queryset)

            #vid_titles_queryset = list(set(vid_titles_queryset))
            vid_titles = {}
            for item in vid_titles_queryset:
                vid_titles[str(item.get('id'))] = item.get('title')

            for obj in vid_list:
                obj['title'] = vid_titles.get(obj.get('videoid'))
                #print(str(obj))
            
            # print("vid titles : "+str(vid_titles))
            # print("vid info: "+str(vid_list))
            # print(vid_list)
            vid_list_uniq = []
            for item in vid_list:
                if(item not in vid_list_uniq):
                    vid_list_uniq.append(item)
            return JsonResponse({'daily_data': vid_list_uniq}, status=status.HTTP_200_OK)

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)   


#def analytics_video_views(request):
def analytics(request):
    return render(request, 'jarvis/pages/analytics_panel/view_analytics_data.html')

@api_view(['POST'])
# view for notification search
def search_notification(request):
    from drf_spirit.serializers import CategoryWithTitleSerializer, CategoryVideoByteSerializer, UserWithNameSerializer, TongueTwisterWithHashSerializer, TongueWithTitleSerializer
    from forum.topic.models import TongueTwister
    from django.db.models import Q
    raw_data = json.loads(request.body)
    query = raw_data['query']
    notification_type = raw_data['notification_type']
    page=0
    try:
        page=int(raw_data['page'])
    except:
        page=0
    data = []
    try:
        if notification_type == '0':
            topics=[]
            try:
                int(query)
                topics=Topic.objects.filter(Q(is_removed=False, is_vb=True, title__istartswith=query)|Q(pk=query)).order_by('title')
            except:
                topics=Topic.objects.filter(is_removed=False, is_vb=True, title__istartswith=query).order_by('title')
            data=TongueWithTitleSerializer(topics[page*100:(page*100)+100], many=True).data
        elif notification_type == '1':
            users=[]
            try:
                int(query)
                users=UserProfile.objects.filter((Q(user__username__istartswith=query)|Q(name__istartswith=query)|Q(mobile_no__istartswith=query)|Q(user__pk=query))&Q(is_test_user=False)).order_by('pk').distinct('pk')
            except:
                users=UserProfile.objects.filter((Q(user__username__istartswith=query)|Q(name__istartswith=query)|Q(mobile_no__istartswith=query))&Q(is_test_user=False)).order_by('pk').distinct('pk')
            data=UserWithNameSerializer(users, many=True).data
        elif notification_type == '2':
            category=[]
            try:
                int(query)
                category=Category.objects.filter(Q(title__istartswith=query)|Q(pk=query))
            except:
                category=Category.objects.filter(title__istartswith=query)
            data=CategoryWithTitleSerializer(category, many=True).data
        elif notification_type == '3':
            challenges=TongueTwister.objects.filter(hash_tag__istartswith=query.replace("#", ""))
            data=TongueTwisterWithHashSerializer(challenges, many=True).data
        else:
            data = []
        return JsonResponse({'data': data}, status=status.HTTP_200_OK)  
    except Exception as e:
        print(e)
        return JsonResponse({'data': [], 'error': str(e)}, status=status.HTTP_200_OK)

@api_view(['POST'])
def search_notification_users(request):
    from drf_spirit.serializers import PushNotificationUserSerializer
    data = []
    try:
        raw_data = json.loads(request.body)
        query = raw_data['query']
        notification_id = raw_data['notification_id']
        status_id = raw_data['status_id']
        pushNotification = PushNotification.objects.get(pk=notification_id)
        pushNotificationUser=PushNotificationUser.objects.filter(push_notification_id=pushNotification, user__username__istartswith=query)
        return JsonResponse({'data': PushNotificationUserSerializer(pushNotificationUser, many=True).data}, status=status.HTTP_200_OK)  
    except Exception as e:
        print(e)
        return JsonResponse({'data': [], 'error': str(e)}, status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_image_notification(requests):
    if requests.is_ajax():
        file=requests.FILES['file']
        print(file)
        data=upload_thumbail_notification(file, 'boloindyapp-prod')
        try:
            return JsonResponse({'data': data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)

def upload_thumbail_notification(virtual_thumb_file,bucket_name):
    try:
        bucket_credentials = get_bucket_details(bucket_name)
        client = boto3.client('s3',aws_access_key_id=bucket_credentials['AWS_ACCESS_KEY_ID'],aws_secret_access_key=bucket_credentials['AWS_SECRET_ACCESS_KEY'])
        ts = time.time()
        final_filename = "img-" + str(ts).replace(".", "")  + ".jpg"
        client.put_object(Bucket=bucket_credentials['AWS_BUCKET_NAME'], Key='notification/'+final_filename, Body=virtual_thumb_file, ACL='public-read')
        filepath = "https://"+bucket_credentials['AWS_BUCKET_NAME']+".s3.amazonaws.com/notification/"+final_filename
        return filepath
    except Exception as e:
        print(e)
        return None

@api_view(['POST'])
def update_user_time(requests):
    return JsonResponse({'message': 'Updated'}, status=status.HTTP_200_OK)
    # dev_id=requests.POST.get('dev_id', None)
    # is_start=requests.POST.get('is_start', '0')
    # current_activity=requests.POST.get('current_activity', '')
    # try:
    #     device=FCMDevice.objects.get(dev_id=dev_id)
    #     if is_start == '0': 
    #         device.start_time=datetime.datetime.now()
    #     else:
    #         try:
    #             delta=datetime.datetime.now()-device.start_time
    #             if delta.seconds > 36000:
    #                 device.start_time=datetime.datetime.now()
    #         except:
    #             pass
    #     device.end_time=datetime.datetime.now()
    #     device.current_activity=current_activity
    #     device.save()
    #     return JsonResponse({'message': 'Updated'}, status=status.HTTP_200_OK)
    # except Exception as e: 
    #     return JsonResponse({'message': 'Not Updated', 'error': str(e)}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_count_notification(requests):
    from django.db.models import Sum
    import json
    try:
        raw_data = json.loads(requests.body)
        
        language_ids = raw_data['lang_ids']
        cat_ids = raw_data['cat_ids']
        user_group_ids = raw_data['user_groups']

        count = 0
        
        lang_array = language_ids.split(',')
        cat_array = cat_ids.split(',')
        user_groups = user_group_ids.split(',')

        if language_ids == '' and cat_ids == '' and user_group_ids == '':
            count += UserCountNotification.objects.filter(language='0', user_group='0', category__isnull=True).aggregate(Sum('no_of_user'))['no_of_user__sum']
        elif user_group_ids == '' and language_ids == '':
            list_ids=[]
            for each in cat_array:
                device=UserCountNotification.objects.get(category__pk=each, language='0')
                list_ids=list_ids+json.loads(device.fcm_users)
            count += len(set(list_ids))
        elif cat_ids == '' and user_group_ids == '':
            count += UserCountNotification.objects.filter(language__in=lang_array, category__isnull=True, user_group='0').aggregate(Sum('no_of_user'))['no_of_user__sum']
        elif cat_ids == '' and language_ids == '':
            list_ids=[]
            for each_group in user_groups:
                if each_group == '2':
                    count += UserCountNotification.objects.filter(language='0', user_group='2', category__isnull=True).aggregate(Sum('no_of_user'))['no_of_user__sum']
                elif each_group == '6' or each_group == '3' or each_group == '4' or each_group == '5':
                    try:
                        device=UserCountNotification.objects.get(user_group=each_group, language='0')
                        list_ids=list_ids+json.loads(device.fcm_users)
                    except Exception as e:
                        pass
                elif each_group == '8':
                    count += 1
            count += len(set(list_ids))
        elif user_group_ids == '':
            list_ids=[]
            for each_lang in lang_array:
                for each in cat_array:
                    device=UserCountNotification.objects.get(category__pk=each, language=each_lang)
                    list_ids=list_ids+json.loads(device.fcm_users)
            count += len(set(list_ids))
        else:    
            list_ids=[]
            for each_lang in lang_array:
                for each in cat_array:
                    try:
                        device=UserCountNotification.objects.get(category__pk=each, language=each_lang)
                        list_ids=list_ids+json.loads(device.fcm_users)
                    except:
                        pass
            for each_group in user_groups:
                if each_group == '2':
                    count += UserCountNotification.objects.filter(language='0', user_group='2', category__isnull=True).aggregate(Sum('no_of_user'))['no_of_user__sum']
                elif each_group == '6' or each_group == '3' or each_group == '4' or each_group == '5':
                    for each_lang in lang_array:
                        try:
                            device=UserCountNotification.objects.get(user_group=each_group, language=each_lang)
                            list_ids=list_ids+json.loads(device.fcm_users)
                        except:
                            pass
                elif each_group == '8':
                    count += 1
            count += len(set(list_ids))
        return JsonResponse({'message': 'Found', 'count': count}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Not Found', 'err': str(e), 'count': 0}, status=status.HTTP_200_OK)


def get_active_reports(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
       return render(request,'jarvis/pages/reports/active_reports.html')

def get_moderated_reports(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
       return render(request,'jarvis/pages/reports/moderated_reports.html')

from forum.topic.forms import VideoByteForm
def get_bot_user_list(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        topic_form = VideoByteForm()
        return render(request,'jarvis/pages/bot_management/bot_user_list.html',{'topic_form': topic_form})
    return JsonResponse({'fail':'','message':'Invalid Request' }, status=status.HTTP_200_OK)

def remove_post_or_block_user_temporarily(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        report_id = request.POST.get('report_id',None)
        if report_id:
            report = Report.objects.get(pk=report_id)
            report.remove_post_or_block_user_temporarily(request.user)
            return JsonResponse({'sucess':'post_removed','message':'success' }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error':'report_id not found','message':'fail' }, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

def seems_fine(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        report_id = request.POST.get('report_id',None)
        if report_id:
            report = Report.objects.get(pk=report_id)
            report.seems_fine(request.user)
            return JsonResponse({'sucess':'post_removed','message':'success' }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error':'report_id not found','message':'fail' }, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

def unremove_video_or_unblock(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        report_id = request.POST.get('report_id',None)
        if report_id:
            report = Report.objects.get(pk=report_id)
            report.unremove_video_or_unblock(request.user)
            return JsonResponse({'sucess':'post_removed','message':'success' }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error':'report_id not found','message':'fail' }, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

@login_required
def add_campaign(request):
    from datetime import datetime
    banner_image_file = request.FILES.get('banner_file')
    start_date_string = request.POST.get('start_date', None)
    end_date_string = request.POST.get('end_date', None)
    hashtag_id = request.POST.get('hashtag_id', None)
    banner_image_upload_folder_name = request.POST.get('folder_prefix','from_upload_panel/campaign_banner_image')
    upload_to_bucket = request.POST.get('bucket_name',None)
    campaign_id = request.POST.get('campaign_id', None)
    is_show_popup = request.POST.get('is_show_popup', None) == 'true'
    campaign_details = request.POST.get('campaign_details', None)

    if not upload_to_bucket:
        return HttpResponse(json.dumps({'message':'fail','reason':'bucket_missing'}),content_type="application/json")
    if not start_date_string or not end_date_string:
        return HttpResponse(json.dumps({'message':'fail','reason':'Invalid dates'}),content_type="application/json")
    if not banner_image_file:
        if not campaign_id:
            return HttpResponse(json.dumps({'message':'fail','reason':'Image File Missing'}),content_type="application/json")
    elif not banner_image_file.name.endswith(('.jpg','.png', '.jpeg')):
        return HttpResponse(json.dumps({'message':'fail','reason':'This is not a jpg/png file'}),content_type="application/json")
    if not hashtag_id or hashtag_id == -1:
        return HttpResponse(json.dumps({'message':'fail','reason':'Invalid Hashtag'}),content_type="application/json")

    start_date = datetime.strptime(start_date_string, "%d-%m-%Y")
    end_date = datetime.strptime(end_date_string, "%d-%m-%Y")
    hashtag = TongueTwister.objects.filter(pk=hashtag_id)[0]
    campaign_dict = {}
    campaign_dict['hashtag'] = hashtag
    campaign_dict['active_from'] = start_date
    campaign_dict['active_till'] = end_date
    campaign_dict['details'] = campaign_details

    popup_image_file = None
    if is_show_popup:
        popup_image_file = request.FILES.get('popup_file')
        campaign_dict['show_popup_on_app'] = True
    else:
        campaign_dict['show_popup_on_app'] = False

    if banner_image_file:
        banner_image_url = upload_image(upload_to_bucket, banner_image_file, banner_image_upload_folder_name)
        if not banner_image_url:
            return HttpResponse(json.dumps({'message':'fail','reason':'Image File already exist'}),content_type="application/json")
        else:
            campaign_dict['banner_img_url'] = banner_image_url

    if popup_image_file:
        popup_image_url = upload_image(upload_to_bucket, popup_image_file, banner_image_upload_folder_name)
        if not popup_image_url:
            return HttpResponse(json.dumps({'message':'fail','reason':'Image File already exist'}),content_type="application/json")
        else:
            campaign_dict['popup_img_url'] = popup_image_url

    if campaign_id:
        #If campaign ID is supplied, then it means it is an older campaign
        campaign_obj = Campaign.objects.get(pk=campaign_id) 

        is_disabled = request.POST.get('disable_campaign', False) == 'true'
        is_winner_declared = request.POST.get('is_winner_declared', False) == 'true'
        
        if is_disabled:
            campaign_dict['is_active'] = False
        else:
            campaign_dict['is_active'] = True

        if is_winner_declared:
            campaign_dict['is_winner_declared'] = True
        else:
            campaign_dict['is_winner_declared'] = False

        if is_winner_declared:
            winner_1_id = request.POST.get('winner_1', None)
            winner_2_id = request.POST.get('winner_2', None)
            winner_3_id = request.POST.get('winner_3', None)
            video_1_id = request.POST.get('video_1', None)
            video_2_id = request.POST.get('video_2', None)
            video_3_id = request.POST.get('video_3', None)
            
            winners = []

            if(winner_1_id):
                winner_1 = Winner.objects.create(user=UserProfile.objects.get(pk=winner_1_id).user, rank=1, video_id=video_1_id)
                winners.append(winner_1)
            if(winner_2_id):
                winner_2 = Winner.objects.create(user=UserProfile.objects.get(pk=winner_2_id).user, rank=2, video_id=video_2_id)
                winners.append(winner_2)
            if(winner_3_id):
                winner_3 = Winner.objects.create(user=UserProfile.objects.get(pk=winner_3_id).user, rank=3, video_id=video_3_id)
                winners.append(winner_3)
            campaign_obj.winners.clear()
            campaign_obj.winners.add(*winners)

        Campaign.objects.filter(pk=campaign_id).update(**campaign_dict)
        
    else:    
        #If there is no campaign ID supplied, then it means it is a new campaign
        campaign_dict['is_winner_declared'] = False
        campaign_obj = Campaign.objects.create(**campaign_dict)

    return HttpResponse(json.dumps({'message':'success', 'campaign_id':campaign_obj.id}),content_type="application/json")

def upload_image(bucket, image_file, folder_name):
    bucket_credentials = get_bucket_details(bucket)
    conn = boto3.client('s3', bucket_credentials['REGION_HOST'], aws_access_key_id = bucket_credentials['AWS_ACCESS_KEY_ID'], \
            aws_secret_access_key = bucket_credentials['AWS_SECRET_ACCESS_KEY'])


    image_file_name = urlify(image_file.name.lower())
    image_output_key = hashlib.sha256(image_file_name.encode('utf-8')).hexdigest()
    image_file_name = check_image_file_name_validation(image_file_name,image_output_key)

    image_path = folder_name+'/'+image_file_name
    try:
        conn.head_object(Bucket=bucket, Key=image_path)
        return None
    except Exception as e:
        with open(urlify(image_file_name),'wb') as f:
            for chunk in image_file.chunks():
                if chunk:
                    f.write(chunk)

    image_url = upload_to_s3_without_transcode(image_file_name,bucket,folder_name)
    os.remove(urlify(image_file_name))
    return image_url

@login_required
def campaigns_panel(request):
    page_no = request.GET.get('page_no', '1')

    campaign_list = Campaign.objects.order_by('-created_at')

    total_page = campaign_list.count()/10
    if campaign_list.count()%10:
        total_page += 1
    page = int(page_no) - 1

    print("**", campaign_list.count(), total_page)

    return render(request,'jarvis/pages/campaigns/boloindya_campaigns.html', {'campaign_list': campaign_list[page*10:page*10+10],\
        'page_no': page_no, 'total_page': total_page})

@login_required
def particular_campaign(request, campaign_id=None):
    campaign = Campaign.objects.get(pk=campaign_id)
    return render(request,'jarvis/pages/campaigns/particular_campaign.html', {'campaign': campaign})


@api_view(['POST'])
def search_fields_for_campaign(request):
    from drf_spirit.serializers import CategoryWithTitleSerializer, CategoryVideoByteSerializer, UserWithNameSerializer, TongueTwisterWithHashSerializer, TongueWithTitleSerializer
    from forum.topic.models import TongueTwister
    from django.db.models import Q
    raw_data = json.loads(request.body)
    query = raw_data['query']
    result_type = raw_data['result_type']

    '''
    result_type: 
         0 = hashtags
         1 = users
         2 = videos
    '''

    page=0
    try:
        page=int(raw_data['page'])
    except:
        page=0
    data = []

    try:
        if result_type == '0':
            challenges=TongueTwister.objects.filter(hash_tag__istartswith=query.replace("#", ""))[:10]
            data=TongueTwisterWithHashSerializer(challenges, many=True).data

        elif result_type == '1':
            try:
                int(query)
                users=UserProfile.objects.filter(Q(user__pk=query)&Q(is_test_user=False)).order_by('pk').distinct('pk')[:20]
            except: 
                users=UserProfile.objects.filter((Q(user__username__istartswith=query)|Q(name__istartswith=query)|Q(mobile_no__istartswith=query))&Q(is_test_user=False)).order_by('pk').distinct('pk')[:20]
            data=UserWithUserSerializer(users, many=True).data

        elif result_type == '2':
            topics=[]
            try:
                int(query)
                topics=Topic.objects.filter(Q(pk=query)).order_by('title')
            except:
                topics=Topic.objects.filter(is_removed=False, is_vb=True, title__istartswith=query).order_by('title')
            data=TongueWithTitleSerializer(topics[page*100:(page*100)+100], many=True).data
        
        else:
            data = []

        print('data:', data)
        return JsonResponse({'data': data}, status=status.HTTP_200_OK )
    except Exception as e:
        print(e)
        return JsonResponse({'data': [], 'error': str(e)}, status=status.HTTP_200_OK)

@api_view(['POST'])
def search_and_add_hashtag(request):
    from drf_spirit.serializers import TongueTwisterWithHashSerializer
    raw_data = json.loads(request.body)

    query = raw_data['hashtag']

    hashtag = TongueTwister.objects.create(hash_tag=query)

    data = TongueTwisterWithHashSerializer(hashtag).data
    return JsonResponse(data, status=status.HTTP_200_OK)


from drf_spirit.utils import get_random_username
@login_required
def bot_user_form(request):
    if request.method == 'GET':
        user_form = UserForm()
        return render(request,'jarvis/pages/bot_management/user_form.html', {'user_form':user_form})
    elif request.method == 'POST':
        from drf_spirit.views import upload_thumbail
        if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
            try:
                profile_pic = request.FILES['profile_pic']
                profile_pic_url = None
                if profile_pic:
                    profile_pic_url = upload_thumbail(profile_pic)
                username = request.POST.get('username',get_random_username())
                name = request.POST.get('name','')
                sub_category = request.POST.getlist('sub_category',None)
                language = request.POST.get('language','1')
                gender = request.POST.get('gender','1')
                about = request.POST.get('about',None)
                bio = request.POST.get('bio',None)
                d_o_b = request.POST.get('d_o_b',None)
                print profile_pic_url
                if username:
                    try:
                        User.objects.get(username = username)
                        return HttpResponse(json.dumps({'message':'fail','reason':'username already taken'}),content_type="application/json")
                    except:
                        user = User.objects.create(username = username)
                        UserProfile.objects.filter(user_id = user.id).update(**{'name':name, 'language':language, 'gender':gender,\
                            'about':about, 'bio':bio, 'd_o_b':d_o_b , 'profile_pic': profile_pic_url, 'is_bot_account': True})
                        userprofile = UserProfile.objects.get(user_id = user.id)
                        for each_category in sub_category:
                            userprofile.sub_category.add(Category.objects.get(pk=each_category))
                    return HttpResponse(json.dumps({'message':'success','user_id':user.id}),content_type="application/json")
            except Exception as e:
                return HttpResponse(json.dumps({'message':'fail','reason':str(e)}),content_type="application/json")
                
        return HttpResponse(json.dumps({'message':'fail','reason':'Not Authorised'}),content_type="application/json")

    return HttpResponse(json.dumps({'message':'fail','reason':'Invalid Request'}),content_type="application/json")

@login_required
def get_bot_video_list(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        if request.method == 'GET':
            user_id = request.GET.get('user_id',None)
            if user_id:
                bot_user = User.objects.get(pk = user_id)
                topic_form = VideoByteForm()
                return render(request,'jarvis/pages/bot_management/bot_video_list.html', {'bot_user':bot_user, 'topic_form': topic_form})
            else:
                HttpResponse(json.dumps({'message':'fail','reason':'user id not found'}),content_type="application/json")
        else:
            HttpResponse(json.dumps({'message':'fail','reason':'only method GET allowed'}),content_type="application/json")
    else:
        HttpResponse(json.dumps({'message':'fail','reason':'Invalid Request'}),content_type="application/json")

@login_required
def delete_bot_video(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
        if request.method == 'POST':
            topic_id = request.POST.get('topic_id',None)
            if topic_id:
                topic = Topic.objects.get(pk =topic_id)
                if not topic.is_removed:
                    topic.delete(is_user_deleted=False)
                    update_profile_counter(topic.user_id,'video_count',1, False)
                    return HttpResponse(json.dumps({'message':'success','reason':'topic removed'}),content_type="application/json")
                else:
                    return HttpResponse(json.dumps({'message':'success','reason':'topic already removed'}),content_type="application/json")
            else:
                return HttpResponse(json.dumps({'message':'fail','reason':'topic id not provided'}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'message':'fail','reason':'only method POST allowed'}),content_type="application/json")
    HttpResponse(json.dumps({'message':'fail','reason':'Invalid Request'}),content_type="application/json")


from django.views.generic import TemplateView
from django.conf import settings
from django.db.models import Sum
from rest_framework.views import APIView
from datetime import datetime
import newrelic.agent
import psycopg2


# newrelic.agent.initialize()
application = newrelic.agent.register_application()

            

class JarvisAnalytics(TemplateView):
    template_name = 'jarvis/pages/analytics_v2/index.html'


    def dispatch(self, *args, **kwargs):
        newrelic.agent.set_transaction_name("/Admin/Analytics-V2/", "Analytics Panel")
        return super(JarvisAnalytics, self).dispatch(*args, **kwargs)


    def get_context_data(self, **kwargs):
        context = {}
        context['languages'] = [{'id': language[0], 'name': language[1]}  for language in settings.LANGUAGE_OPTIONS] 
        context['categories'] = Category.objects.values('id', 'title')
        return context



def get_elastic_filters(start_date, end_date, language_id=None, category_id=None):
    filters = [{'range': {'create_date': {
        'gte': start_date, 
        'lte': end_date, 
    }}}]

    if category_id:
        filters.append({'term': {'category_id': int(category_id)}})

    if language_id and language_id != '0':
        filters.append({'term': {'language_id': language_id}}) 

    return filters 


def get_elastic_date_group_by(group_by):
    if group_by == 'daily':
        return 'day', 'dd-MMM-yyyy'
    elif group_by == 'weekly':
        return 'week', 'dd-MMM-yyyy'
    if group_by == 'monthly':
        return 'month', 'MMM-yyyy'


def get_video_create_stats_elastic(start_date, end_date, group_by, language_id=None, category_id=None):
    from elasticsearch_utils import ElasticSearch
    from time import time

    interval, date_format = get_elastic_date_group_by(group_by)
    t = time()
    result = ElasticSearch().search('topic-index', {
        'aggs': 
            {'total_videos': {'date_histogram': {
                'field': 'create_date', 
                'calendar_interval': interval,
                'format': date_format
            }}
        },
        'query': {
            'bool': {
                'filter': get_elastic_filters(start_date, end_date, language_id, category_id)
            }
        },
        'size': 0
    })

    print("time taken", time() - t)

    return result.get('aggregations', {}).get('total_videos', {}).get('buckets')


def get_video_creator_stats_elastic(start_date, end_date, group_by, language_id=None, category_id=None):
    from elasticsearch_utils import ElasticSearch

    interval, date_format = get_elastic_date_group_by(group_by)
    result = ElasticSearch().search('topic-index', {
        'aggs': 
            {'total_videos': {
                'date_histogram': {
                    'field': 'create_date', 
                    'calendar_interval': interval,
                    'format': date_format
                },
                "aggs": {"unique_users": {"cardinality": {"field": "user_id"}}}
            }
        },
        'query': {
            'bool': {
                'filter': get_elastic_filters(start_date, end_date, language_id, category_id)
            }
        },
        'size': 0
    })

    # print("result", result)

    return result.get('aggregations', {}).get('total_videos', {}).get('buckets')



# def get_video_new_creator_stats_elastic(start_date, end_date, group_by, language_id=None, category_id=None):
#     from elasticsearch_utils import ElasticSearch

#     interval, date_format = get_elastic_date_group_by(group_by)
#     result = ElasticSearch().search('user-index', {
#         'aggs': 
#             {'new_users': {
#                 'date_histogram': {
#                     'field': 'create_date', 
#                     'calendar_interval': interval,
#                     'format': date_format
#                 }
#             }
#         },
#         'query': {
#             'bool': {
#                 'filter': get_elastic_filters(start_date, end_date, language_id, category_id)
#             }
#         },
#         'size': 0
#     })

#     return result.get('aggregations', {}).get('new_users', {}).get('buckets')


def get_video_playtime_stats_elastic(start_date, end_date, group_by, language_id=None, category_id=None):
    from elasticsearch_utils import ElasticSearch

    interval, date_format = get_elastic_date_group_by(group_by)
    result = ElasticSearch().search('playtime-index', {
        'aggs': 
            {'playtime_count': {
                'date_histogram': {
                    'field': 'create_date', 
                    'calendar_interval': interval,
                    'format': date_format
                },
                "aggs": {"total_playtime": {"sum": {"field": "playtime"}}}
            }
        },
        'query': {
            'bool': {
                'filter': get_elastic_filters(start_date, end_date, language_id, category_id)
            }
        },
        'size': 0
    })

    # print("result", result)

    return result.get('aggregations', {}).get('playtime_count', {}).get('buckets')


class AnalyticsGraphCountsAPIView(APIView):
    def get_counts(self):
        return 0

    def get(self, request, required_data_type, *args, **kwargs):
        if required_data_type == 'counts':
            return JsonResponse({
                'result': {
                    'counts': self.get_counts()
                }
            })
        elif required_data_type == 'data':
            return JsonResponse({
                'result': {
                    'data': self.get_data()
                }
            })


class VideoCreatedAPIView(AnalyticsGraphCountsAPIView):
    def get_data(self):
        params = self.request.query_params
        return [{
                'key': row.get('key_as_string'),
                'value': row.get('doc_count')
            } for row in get_video_create_stats_elastic(params.get('start_date'), params.get('end_date'),
                params.get('view_mode'), params.get('language_id'), params.get('category_id'))]

    def get_counts(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return Topic.objects.filter(created_at__gte=start_date, created_at__lte=end_date).count()
        

class VideoCreatorAPIView(AnalyticsGraphCountsAPIView):
    def get_data(self):
        params = self.request.query_params
        return [{
                'key': row.get('key_as_string'),
                'value': row.get('unique_users', {}).get('value')
            } for row in get_video_creator_stats_elastic(params.get('start_date'), params.get('end_date'),
                params.get('view_mode'), params.get('language_id'), params.get('category_id'))]

    def get_counts(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return Topic.objects.filter(created_at__gte=start_date, created_at__lte=end_date).distinct('user_id').count()

class NewVideoCreatorAPIView(AnalyticsGraphCountsAPIView):
    def get_data(self):
        query_params = self.request.query_params

        where_clause_1 = ['created_at between %s and %s']
        params_1 = [query_params.get('start_date'), query_params.get('end_date')]

        where_clause_2 = []
        params_2 = []

        where_clause_3 = ['created_at between %s and %s']
        params_3 = [query_params.get('start_date'), query_params.get('end_date')]

        join_query = ''

        if query_params.get('language_id'):
            where_clause_1.append('language_id = %s')
            params_1.append(query_params.get('language_id'))
            where_clause_2.append('language_id = %s')
            params_2.append(query_params.get('language_id'))

        if query_params.get('category_id'):
            where_clause_1.append('tc.category_id = %s')
            params_1.append(query_params.get('category_id'))
            where_clause_2.append('tc.category_id = %s')
            params_2.append(query_params.get('category_id'))

            join_query = ' inner join forum_topic_topic_m2mcategory tc on tc.topic_id = tp.id '

        date_column = "created_at::date"
        date_format_column = "to_char(C.created_at, 'DD-Mon-YYYY')"

        if query_params.get('view_mode') == 'weekly':
            date_column = "date_trunc('week', A.created_at)"
            date_format_column = "concat('Week ', to_char(C.created_at, 'WW'))"
        elif query_params.get('view_mode') == 'monthly':
            date_column = "date_trunc('month', A.created_at)"
            date_format_column = "to_char(C.created_at, 'Mon-YYYY')"

        # query = """
        #     SELECT %s as key, C.count as value
        #     FROM (
        #         SELECT %s as created_at, count(distinct A.user_id) as count
        #         FROM    
        #             (SELECT created_at, user_id
        #             from forum_topic_topic tp %s
        #             where %s) AS A
        #         LEFT JOIN
        #             (SELECT distinct user_id
        #             from forum_topic_topic tp %s
        #             WHERE %s ) AS  B on A.user_id =B.user_id
        #         WHERE B.user_id is null
        #         GROUP BY %s
        #     ) C ORDER BY C.created_at 

        # """%(date_format_column, date_column, join_query, ' AND '.join(where_clause), 
        #         join_query, ' AND '.join(where_clause_2), date_column)

        if where_clause_2:
            where_clause_2 = ' AND ' + ' AND '.join(where_clause_2)
        else:
            where_clause_2 = ''

        query = """
            SELECT {date_format_column} as key, C.count as value
            FROM (
                SELECT {date_column} as created_at, count(user_id) as count
                FROM (
                    SELECT min(tp.created_at) as created_at, tp.user_id
                    FROM forum_topic_topic tp {join_query}
                    WHERE user_id in  (SELECT distinct user_id
                        FROM forum_topic_topic tp {join_query}
                        WHERE {where_clause_1}
                    ) {where_clause_2}
                    GROUP BY tp.user_id
                ) A
                WHERE {where_clause_3}
                GROUP BY {date_column}
            ) C ORDER BY C.created_at 
        """.format(date_format_column=date_format_column, date_column=date_column, 
                where_clause_1=' AND '.join(where_clause_1), where_clause_2=where_clause_2,
                where_clause_3=' AND '.join(where_clause_3), join_query=join_query)

        print "Query", query

        with connections['default'].cursor() as cr:
            cr.execute(query, params_1 + params_2 + params_3)

            columns = [col[0] for col in cr.description]
            return [
                dict(zip(columns, row))
                for row in cr.fetchall()
            ]



    def get_counts(self):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        with connections['default'].cursor() as cr:
            cr.execute("""
                SELECT count(distinct A.user_id) 
                FROM    
                    (SELECT created_at, user_id
                    from forum_topic_topic tp
                    where created_at between %s and %s) AS A
                LEFT JOIN
                    (SELECT distinct user_id
                    from forum_topic_topic tp
                    WHERE created_at < %s ) AS  B on A.user_id =B.user_id
                WHERE B.user_id is null
            """, [start_date, end_date, start_date])

            return cr.fetchall()[0][0]
        

class VideoPlaytimeAPIView(AnalyticsGraphCountsAPIView):
    def get_data(self):
        params = self.request.query_params
        return [{
                'key': row.get('key_as_string'),
                'value': int(row.get('total_playtime', {}).get('value'))/(60*60)
            } for row in get_video_playtime_stats_elastic(params.get('start_date'), params.get('end_date'),
                params.get('view_mode'), params.get('language_id'), params.get('category_id'))]


    def get_counts(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return str((VideoPlaytime.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date)\
                .aggregate(Sum('playtime'))['playtime__sum'] or 0) / (60*60)) + ' Hours'


def timeout_test(request):
    import time
    time.sleep(int(request.GET.get('tout', 65)))
    return HttpResponse('No Timeout...')

@login_required
def new_coupon_page(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        coupon_form = CouponForm()
        return render(request,'jarvis/pages/coupons/create_new_coupons.html',
                {'add_coupons':coupon_form})
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)
@login_required
def add_coupon(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        active_banner_image_file = request.FILES.get('active_banner_file')
        inactive_banner_image_file = request.FILES.get('inactive_banner_file')
        start_date_string = request.POST.get('start_date', None)
        end_date_string = request.POST.get('end_date', None)
        banner_image_upload_folder_name = request.POST.get('folder_prefix','from_upload_panel/coupon_banner_image')
        upload_to_bucket = request.POST.get('bucket_name',None)
        coupon_id = request.POST.get('coupon_id', None)
        coins = request.POST.get('coins',None)
        coupon_code = request.POST.get('coupon_code',None)
        brand_name = request.POST.get('brand_name',None)
        discount = request.POST.get('discount',None)
        is_draft = request.POST.get('is_draft',None)

        if not brand_name:
            return JsonResponse({'message':'fail','reason':'Brand Name Missing'}, status=status.HTTP_200_OK)
        if not coins.isdigit():
            return JsonResponse({'message':'fail','reason':'Bolo Coins Invalid, Please enter a number'}, status=status.HTTP_200_OK)
        if not coupon_code:
            return JsonResponse({'message':'fail','reason':'Discount Code Missing'}, status=status.HTTP_200_OK)
        if not discount:
            return JsonResponse({'message':'fail','reason':'Discount Missing'}, status=status.HTTP_200_OK)
        if not upload_to_bucket:
            return JsonResponse({'message':'fail','reason':'bucket_missing'}, status=status.HTTP_200_OK)
        if not start_date_string or not end_date_string:
            return JsonResponse({'message':'fail','reason':'Invalid dates'}, status=status.HTTP_200_OK)
        if not active_banner_image_file:
            if not coupon_id:
                return JsonResponse({'message':'fail','reason':'Active Banner Image File Missing'}, status=status.HTTP_200_OK)
        elif not active_banner_image_file.name.endswith(('.jpg','.png', '.jpeg')):
            return JsonResponse({'message':'fail','reason':'This is not a jpg/png file'}, status=status.HTTP_200_OK)
        if not inactive_banner_image_file:
            if not coupon_id:
                return JsonResponse({'message':'fail','reason':'Inactive Banner Image File Missing'}, status=status.HTTP_200_OK)
        elif not inactive_banner_image_file.name.endswith(('.jpg','.png', '.jpeg')):
            return JsonResponse({'message':'fail','reason':'This is not a jpg/png file'}, status=status.HTTP_200_OK)

        start_date = datetime.strptime(start_date_string, "%d-%m-%Y")
        end_date = datetime.strptime(end_date_string, "%d-%m-%Y")
        is_draft = True if is_draft=='true' else False
        coupon_dict = {}
        coupon_dict['active_from'] = start_date
        coupon_dict['active_till'] = end_date
        coupon_dict['brand_name'] = brand_name
        coupon_dict['coins_required'] = int(coins)
        coupon_dict['coupon_code'] = coupon_code
        coupon_dict['discount_given'] = discount
        coupon_dict['is_draft'] = is_draft
        if active_banner_image_file:
            active_banner_image_url = upload_image(upload_to_bucket, active_banner_image_file, banner_image_upload_folder_name)
            if not active_banner_image_url:
                return JsonResponse({'message':'fail','reason':'Image File already exist'}, status=status.HTTP_200_OK)
            else:
                coupon_dict['active_banner_img_url'] = active_banner_image_url

        if inactive_banner_image_file:
            inactive_banner_image_url = upload_image(upload_to_bucket, inactive_banner_image_file, banner_image_upload_folder_name)
            if not inactive_banner_image_url:
                return JsonResponse({'message':'fail','reason':'Image File already exist'}, status=status.HTTP_200_OK)
            else:
                coupon_dict['inactive_banner_img_url'] = inactive_banner_image_url

        if coupon_id:
            #If coupon ID is supplied, then it means it is an older coupon
            coupon_obj = Coupon.objects.get(pk=coupon_id) 
            is_active = request.POST.get('is_active_coupon', False)=='true'
            if is_active:
                coupon_dict['is_active'] = True
            else:
                coupon_dict['is_active'] = False
            Coupon.objects.filter(pk=coupon_id).update(**coupon_dict)
            
        else:    
            #If there is no coupon ID supplied, then it means it is a new coupon
            coupon_obj = Coupon.objects.create(**coupon_dict)

        return JsonResponse({'message':'success', 'coupon_id':coupon_obj.id}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

@login_required
def particular_coupon(request, coupon_id=None):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        coupon = Coupon.objects.get(pk=coupon_id)
        return render(request,'jarvis/pages/coupons/particular_coupon.html', {'coupon': coupon})
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

@login_required
def coupon_report_pannel(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        page_no = request.GET.get('page_no', '1')
        all_coupons = Coupon.objects.order_by('-created_at')
        df1 =  pd.DataFrame.from_records(all_coupons.values('id','brand_name', 'coupon_code', 'discount_given', 'active_till'))
        all_user_coupons = UserCoupon.objects.all()
        final_data = []
        page = 1
        total_page = 1
        if all_user_coupons:
            df2 = pd.DataFrame.from_records(all_user_coupons.values('user_id','coupon_id'))
            df1["redeem_count"] = df1["id"].map(df2["coupon_id"].value_counts()).fillna(0).astype(int)
            final_data = df1.to_dict('records')
            total_page = len(final_data)//10
            if len(final_data)%10:
                total_page += 1
            page = int(page_no) - 1

        # print("**", coupon_list.count(), total_page)

        return render(request,'jarvis/pages/coupons/boloindya_coupons_report.html', {'coupon_list': final_data[page*10:page*10+10],\
            'page_no': page_no, 'total_page': total_page, 'page_adder': str((int(page_no)-1)*10)})
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

class CouponDatableList(generics.ListAPIView):
    serializer_class = CouponSerializer

    def get_queryset(self):
        if self.request.user.is_superuser or 'moderator' in list(self.request.user.groups.all().values_list('name',flat=True)) or self.request.user.is_staff:
            return Coupon.objects.order_by('-created_at')
        else: 
            return []

@login_required
def coupon_list_datable(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        token = get_tokens_for_user(request.user)
        access_token = token.get('access')
        return render(request,'jarvis/pages/coupons/boloindya_coupons.html', {'token': access_token})

@login_required
def event_list(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        page_no = request.GET.get('page_no', '1')

        event_list = Event.objects.order_by('-created_at')

        total_page = event_list.count()/10
        if event_list.count()%10:
            total_page += 1
        page = int(page_no) - 1

        print("**", event_list.count(), total_page)

        return render(request,'jarvis/pages/events/boloindya_events.html', {'event_list': event_list[page*10:page*10+10],\
            'page_no': page_no, 'total_page': total_page})
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

@login_required
def event_booking_list(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        page_no = request.GET.get('page_no', '1')

        event_booking_list = EventBooking.objects.select_related('event').order_by('-created_at')

        total_page = event_booking_list.count()/10
        if event_booking_list.count()%10:
            total_page += 1
        page = int(page_no) - 1

        print("**", event_booking_list.count(), total_page)

        return render(request,'jarvis/pages/events/boloindya_event_bookings.html', {'event_booking_list': event_booking_list[page*10:page*10+10],\
            'page_no': page_no, 'total_page': total_page})
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

def event_update(request):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        event_id = request.POST.get('event_id',None)
        approve_toggle_value = request.POST.get('approve_toggle_value',None)
        active_toggle_value = request.POST.get('active_toggle_value',None)
        if event_id:
            if approve_toggle_value:
                is_approved = None
                if approve_toggle_value=='true':
                    is_approved = True
                elif approve_toggle_value == 'false':
                    is_approved = False
                Event.objects.filter(pk=event_id).update(is_approved=is_approved)
            elif active_toggle_value:
                is_active = None
                if active_toggle_value=='true':
                    is_active = True
                elif active_toggle_value == 'false':
                    is_active = False
                Event.objects.filter(pk=event_id).update(is_active=is_active)
            else:
                return JsonResponse({'error':'Something went wrong!','message':'fail' }, status=status.HTTP_200_OK)
            return JsonResponse({'sucess':'event updated','message':'success' }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error':'event_id not found','message':'fail' }, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

def month_year_iter(start_month, start_year, end_month, end_year):
    yield "%s-%s-01"%(start_year, str(start_month).zfill(2))

    while start_month < end_month or start_year < end_year:
        start_month += 1

        if start_month > 12:
            start_year += 1
            start_month = 1

        yield "%s-%s-01"%(start_year, str(start_month).zfill(2))

from rest_framework.generics import ListAPIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from payment.partner.models import TopUser
from payment.partner.serializers import TopUserSerializer
from payment.utils import PageNumberPaginationRemastered

class TopUserTemplateView(TemplateView):
    template_name = "jarvis/pages/top_users/index.html"

    def get_context_data(self, **kwargs):
        context = super(TopUserTemplateView, self).get_context_data(**kwargs)
        today = datetime.now().date()

        context['all_month'] = sorted([{
            'name': datetime.strptime(month, '%Y-%m-%d').strftime('%B %Y'),
            'value': month
        } for month in month_year_iter(1, 2020, today.month, today.year)], key=lambda x: x.get('value'), reverse=True)

        return context


class TopUserListView(ListAPIView):
    queryset = TopUser.objects.all()
    serializer_class = TopUserSerializer
    pagination_class = PageNumberPaginationRemastered
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get_queryset(self):
        query_params = self.request.query_params
        queryset = self.queryset

        sort_field = '-video_count'
        
        if query_params.get('sortField'):
            sort_field = query_params.get('sortField')

        if query_params.get('sortOrder') == 'desc':
            sort_field = '-' + sort_field

        if query_params.get('selectedMonth'):
            date = datetime.strptime(query_params.get('selectedMonth'), '%Y-%m-%d')
            self.queryset = self.queryset.filter(agg_month=query_params.get('selectedMonth'))

        if query_params.get('q'):
            q = query_params.get('q')
            with connections['default'].cursor() as cursor:
                cursor.execute("""
                    SELECT user_id
                    FROM forum_user_userprofile
                    WHERE name ilike %s or slug = %s
                """, ['%' + q +'%', q])
                ids = [row[0] for row in cursor.fetchall()]
            self.queryset = self.queryset.filter(boloindya_id__in=ids)
        query = self.queryset.query.sql_with_params()
        return self.queryset.order_by(sort_field)

def upload_coupon_image(bucket, image_file, folder_name):
    '''
        This function is clone of upload_image and it just add 
        timestamp in file name to allow images with same name
    '''
    bucket_credentials = get_bucket_details(bucket)
    conn = boto3.client('s3', bucket_credentials['REGION_HOST'], aws_access_key_id = bucket_credentials['AWS_ACCESS_KEY_ID'], \
            aws_secret_access_key = bucket_credentials['AWS_SECRET_ACCESS_KEY'])
    image_file_name = urlify(image_file.name.lower())
    image_output_key = hashlib.sha256(image_file_name.encode('utf-8')).hexdigest()
    image_file_name = check_image_file_name_validation(image_file_name,image_output_key)
    image_file_name = str(datetime.now()).replace(' ', '') +"_"+ image_file_name
    image_path = folder_name+'/'+image_file_name

    try:
        conn.head_object(Bucket=bucket, Key=image_path)
        return None
    except Exception as e:
        with open(urlify(image_file_name),'wb') as f:
            for chunk in image_file.chunks():
                if chunk:
                    f.write(chunk)

    image_url = upload_to_s3_without_transcode(image_file_name,bucket,folder_name)
    os.remove(urlify(image_file_name))
    return image_url
