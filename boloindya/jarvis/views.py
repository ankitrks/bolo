# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv, io
from django.contrib import messages
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import permission_required
import requests
from bs4 import BeautifulSoup
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import S3Transfer
from django.http import HttpResponse, HttpRequest, JsonResponse
import json
import string
import random
import os
import hashlib
import time
import re
from drf_spirit.views import getVideoLength
from drf_spirit.utils  import calculate_encashable_details
from forum.user.models import UserProfile, ReferralCode, ReferralCodeUsed, VideoCompleteRate, VideoPlaytime
from forum.topic.models import Topic, VBseen
from forum.category.models import Category
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from forum.userkyc.models import UserKYC, KYCBasicInfo, KYCDocumentType, KYCDocument, AdditionalInfo, BankDetail
from forum.payment.models import PaymentCycle,EncashableDetail,PaymentInfo
from django.conf import settings
from forum.payment.forms import PaymentForm,PaymentCycleForm
from django.views.generic.edit import FormView
from datetime import datetime
from forum.userkyc.forms import KYCBasicInfoRejectForm,KYCDocumentRejectForm,AdditionalInfoRejectForm,BankDetailRejectForm
from .models import VideoUploadTranscode,VideoCategory, PushNotification, PushNotificationUser, language_options, user_group_options, FCMDevice, notification_type_options
from drf_spirit.models import MonthlyActiveUser, HourlyActiveUser, DailyActiveUser, VideoDetails
from forum.category.models import Category
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import make_aware
from datetime import timedelta
from itertools import groupby
from django.db.models import Count
import ast
from drf_spirit.serializers import VideoCompleteRateSerializer
from .forms import VideoUploadTranscodeForm
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, imencode
from django.core.files.base import ContentFile
from drf_spirit.serializers import UserWithUserSerializer

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
    return render(request,'jarvis/layout/base.html')

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
    all_upload = VideoUploadTranscode.objects.all().distinct().values('folder_to_upload').annotate(folder_count=Count('folder_to_upload')).order_by('folder_to_upload')
    print all_upload
    return render(request,'jarvis/pages/upload_n_transcode/upload_n_transcode.html',{'all_category':all_category,'all_upload':all_upload})

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
        m3u8_url = os.path.join('https://s3.amazonaws.com/'+bucket_credentials['AWS_BUCKET_NAME_TS']+'/', \
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
    if request.user.is_superuser:
        all_kyc = UserKYC.objects.all()
        return render(request,'jarvis/pages/userkyc/user_kyc_list.html',{'all_kyc':all_kyc})
def get_submitted_kyc_user_list(request):
    if request.user.is_superuser:
        all_kyc = UserKYC.objects.filter(is_kyc_completed=True,is_kyc_accepted=False)
        return render(request,'jarvis/pages/userkyc/submitted_kyc.html',{'all_kyc':all_kyc})

def get_pending_kyc_user_list(request):
    if request.user.is_superuser:
        all_kyc = UserKYC.objects.filter(is_kyc_completed=False,is_kyc_accepted=False)
        return render(request,'jarvis/pages/userkyc/pending_kyc.html',{'all_kyc':all_kyc})

def get_accepted_kyc_user_list(request):
    if request.user.is_superuser:
        all_kyc = UserKYC.objects.filter(is_kyc_completed=True,is_kyc_accepted=True)
        return render(request,'jarvis/pages/userkyc/accepted_kyc.html',{'all_kyc':all_kyc})

def get_kyc_of_user(request):
    if request.user.is_superuser or request.user.is_staff:
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
    if request.user.is_superuser or request.user.is_staff:
        if to_be_calculated:
            for each_user in User.objects.all():
                calculate_encashable_details(each_user)
        all_encash_details = EncashableDetail.objects.all().order_by('-bolo_score_earned')[:300]
    pay_cycle = PaymentCycle.objects.all().first()
    payement_cycle_form = PaymentCycleForm(initial=pay_cycle.__dict__)
    return render(request,'jarvis/pages/payment/encashable_detail.html',{'all_encash_details':all_encash_details,'payement_cycle_form':payement_cycle_form})

def calculate_encashable_detail(request):
    if request.user.is_superuser or request.user.is_staff:
        for each_user in User.objects.all():
            calculate_encashable_details(each_user)
    return HttpResponse(json.dumps({'success':'success'}),content_type="application/json")

def get_single_encash_detail(request):
    if request.user.is_superuser or request.user.is_staff:
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
        if self.request.user.is_superuser or self.request.user.is_staff:
            pay_cycle = PaymentCycle.objects.all().update(**form.cleaned_data)
            for each_user in User.objects.all():
                calculate_encashable_details(each_user)
            all_encash_details = EncashableDetail.objects.all().order_by('-bolo_score_earned')
            pay_cycle = PaymentCycle.objects.all().first()
            payement_cycle_form = PaymentCycleForm(initial=pay_cycle.__dict__)
            return render(request,'jarvis/pages/payment/encashable_detail.html',{'all_encash_details':all_encash_details,'payement_cycle_form':payement_cycle_form})


def accept_kyc(request):
    if request.user.is_superuser or request.user.is_staff:
        kyc_type = request.GET.get('kyc_type',None)
        user_id = request.GET.get('user_id',None)
        user_kyc = UserKYC.objects.get(user_id = user_id)
        if kyc_type == "basic_info":
            user_kyc.is_kyc_basic_info_accepted = True
        elif kyc_type == "kyc_document":
            user_kyc.is_kyc_document_info_accepted = True
        elif kyc_type == "kyc_pan":
            user_kyc.is_kyc_pan_info_accepted = True
        elif kyc_type == "kyc_profile_pic":
            user_kyc.is_kyc_selfie_info_accepted = True
        elif kyc_type == "kyc_additional_info":
            user_kyc.is_kyc_additional_info_accepted = True
        elif kyc_type == "kyc_bank_details":
            user_kyc.is_kyc_bank_details_accepted = True
        user_kyc.save()
        if user_kyc.is_kyc_basic_info_accepted and user_kyc.is_kyc_document_info_accepted and user_kyc.is_kyc_selfie_info_accepted and\
        user_kyc.is_kyc_bank_details_accepted:
            user_kyc.is_kyc_accepted = True
            user_kyc.save()

        return HttpResponse(json.dumps({'success':'success','kyc_accepted':user_kyc.is_kyc_accepted}),content_type="application/json")

def reject_kyc(request):
    if request.user.is_superuser or request.user.is_staff:
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
    if not upload_file.name.endswith('.mp4'):
        return HttpResponse(json.dumps({'message':'fail','reason':'This is not a mp4 file'}),content_type="application/json")
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
            thumbnail_url = get_video_thumbnail(uploaded_url,upload_to_bucket)
            try:
                videolength = getVideoLength(uploaded_url)
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
            my_upload_transcode = VideoUploadTranscode.objects.create(**my_dict)
            os.remove(urlify(upload_file_name))
            try:
                update_careeranna_db(my_upload_transcode)
            except Exception as e:
                return HttpResponse(json.dumps({'message':'fail','reason':'Could not update careeranna db'+str(e)}),content_type="application/json")

    return HttpResponse(json.dumps({'message':'success','file_id':my_upload_transcode.id}),content_type="application/json")


@login_required
def upload_details(request):
    file_id = request.GET.get('id',None)
    if file_id:
        my_video = VideoUploadTranscode.objects.get(pk=file_id)
        return render(request,'jarvis/pages/upload_n_transcode/video_urls.html',{'my_video':my_video})
    return render(request,'jarvis/pages/upload_n_transcode/video_urls.html')


@login_required
def uploaded_list(request):
    all_uploaded = VideoUploadTranscode.objects.filter(is_active = True)
    return render(request,'jarvis/pages/upload_n_transcode/uploaded_list.html',{'all_uploaded':all_uploaded})

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
        print request.POST
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
        print virtual_thumb_file
        url_thumbnail= upload_thumbail(virtual_thumb_file,bucket_name)
        print url_thumbnail
        # obj.thumbnail = url_thumbnail
        # obj.media_duration = media_duration
        # obj.save()
        return url_thumbnail
    else:
        return False

def upload_thumbail(virtual_thumb_file,bucket_name):
    try:
        bucket_credentials = get_bucket_details('careeranna')
        client = boto3.client('s3',aws_access_key_id=bucket_credentials['AWS_ACCESS_KEY_ID'],aws_secret_access_key=bucket_credentials['AWS_SECRET_ACCESS_KEY'])
        ts = time.time()
        created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        final_filename = "img-" + str(ts).replace(".", "")  + ".jpg"
        client.put_object(Bucket=bucket_credentials['AWS_BUCKET_NAME'], Key='thumbnail/' +bucket_name+"/"+final_filename, Body=virtual_thumb_file, ACL='public-read')
        # client.resource('s3').Object(settings.BOLOINDYA_AWS_BUCKET_NAME, 'thumbnail/' + final_filename).put(Body=open(virtual_thumb_file, 'rb'))
        filepath = "https://"+bucket_credentials['AWS_BUCKET_NAME']+".s3.amazonaws.com/thumbnail/"+bucket_name+"/"+final_filename
        # if os.path.exists(file):
        #     os.remove(file)
        return filepath
    except:
        return None

def update_careeranna_db(uploaded_video):
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
        'video_url' : uploaded_video.transcoded_file_url,
        'backup_url' : uploaded_video.s3_file_url,
        'status' : status,
        'duration' : uploaded_video.media_duration

    }
    reseponse_careeranna = requests.post(settings.CAREERANNA_VIDEOFILE_UPDATE_URL, data=payload, headers=headers)
    return reseponse_careeranna
    

def notification_panel(request):
  
    lang = request.POST.get('lang')
    notification_type = request.POST.get('notification_type')
    user_group = request.POST.get('user_group')
    scheduled_status = request.POST.get('scheduled_status')
    title = request.POST.get('title', '')

    filters = {'language': lang, 'notification_type': notification_type, 'user_group': user_group, 'is_scheduled': scheduled_status, 'title__icontains': title}

    pushNotifications = PushNotification.objects.filter(*[Q(**{k: v}) for k, v in filters.items() if v], is_removed=False).order_by('-created_at')

    return render(request,'jarvis/pages/notification/index.html', {'pushNotifications': pushNotifications, \
        'language_options': language_options, 'notification_types': notification_type_options, \
            'user_group_options': user_group_options, 'language': lang, 'notification_type': notification_type, \
                'user_group': user_group, 'scheduled_status': scheduled_status, 'title': title})

from drf_spirit.models import UserLogStatistics
import datetime

def send_notification(request):

    pushNotification = {}
    
    if request.method == 'POST':
        
        title = request.POST.get('title', "")
        upper_title = request.POST.get('upper_title', "")
        notification_type = request.POST.get('notification_type', "")
        id = request.POST.get('id', "")
        user_group = request.POST.get('user_group', "")
        lang = request.POST.get('lang', "")
        schedule_status = request.POST.get('schedule_status', "")
        datepicker = request.POST.get('datepicker', '')
        timepicker = request.POST.get('timepicker', '').replace(" : ", ":")

        pushNotification = PushNotification()
        pushNotification.title = upper_title
        pushNotification.description = title
        pushNotification.language = lang
        pushNotification.notification_type = notification_type
        pushNotification.user_group = user_group
        pushNotification.instance_id = id
        pushNotification.save()

        if schedule_status == '1':
            if datepicker:
                pushNotification.scheduled_time = datetime.datetime.strptime(datepicker + " " + timepicker, "%m/%d/%Y %H:%M")
            pushNotification.is_scheduled = True            
            pushNotification.save()
        else:

            device = ''

            language_filter = {} 
        
            if lang != '0':
                language_filter = { 'user__st__language': lang }
            
            if user_group == '1':
                end_date = datetime.datetime.today()
                start_date = end_date - datetime.timedelta(hours=3)
                device = FCMDevice.objects.filter(user__isnull=True, created_at__range=(start_date, end_date))
            
            elif user_group == '2':
                device = FCMDevice.objects.filter(user__isnull=True)
            
            else:
                filter_list = []

                if user_group == '3':
                    filter_list = VBseen.objects.distinct('user__pk').values_list('user__pk', flat=True)
                
                elif user_group == '4' or user_group == '5':
                    hours_ago = datetime.datetime.now()
                    if user_group == '4':
                        hours_ago -= datetime.timedelta(days=1)
                    else:
                        hours_ago -=  datetime.timedelta(days=2)

                    filter_list = UserLogStatistics.objects.filter(session_starttime__gte=hours_ago).values_list('user', flat=True)
                    filter_list = map(int , filter_list)
                    
                elif user_group == '6':
                    filter_list = Topic.objects.filter(is_vb=True).values_list('user__pk', flat=True)

                device = FCMDevice.objects.exclude(user__pk__in=filter_list).filter(**language_filter)

            print(device)
            device.send_message(data={"title": title, "id": id, "title_upper": upper_title, "type": notification_type, "notification_id": pushNotification.pk})
        return redirect('/jarvis/notification_panel/')

    if request.method == 'GET':
        id = request.GET.get('id', None)
        try:
            pushNotification = PushNotification.objects.get(pk=id)
        except Exception as e:
            print e
    return render(request,'jarvis/pages/notification/send_notification.html', { 'language_options': language_options, 'user_group_options' : user_group_options, 'notification_types': notification_type_options, 'pushNotification': pushNotification })


def particular_notification(request, notification_id=None):
    pushNotification = PushNotification.objects.get(pk=notification_id)
    return render(request,'jarvis/pages/notification/particular_notification.html', {'pushNotification': pushNotification})

from rest_framework.decorators import api_view

@api_view(['POST'])
def create_user_notification_delivered(request):
    notification_id = request.POST.get('notification_id', "")

    pushNotificationUser = PushNotificationUser()
    if request.user:
        print(request.user)
        pushNotificationUser.user = request.user
    pushNotification = PushNotification.objects.get(pk=notification_id)
    pushNotificationUser.push_notification_id = pushNotification
    pushNotificationUser.save()

    return JsonResponse({"status":"Success"})

@api_view(['POST'])
def open_notification_delivered(request):
    notification_id = request.POST.get('notification_id', "")

    pushNotification = PushNotification.objects.get(pk=notification_id)
    if request.user:
        pushNotificationUser = PushNotificationUser.objects.get(push_notification_id=pushNotification, user=request.user)
        pushNotificationUser.status = '1'
        pushNotificationUser.save()

    return JsonResponse({"status":"Success"})


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
    today = datetime.today()
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
    date_begin = datetime.today() + timedelta(days=-1)
    date_begin.replace(hour=0, minute=0, second=0)
    date_end = datetime.today()

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



@csrf_exempt
def get_hau_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            hau_day = raw_data['hau_day']
            print hau_day
            hau_day_begin = hau_day + " 00:00:00"

            date_begin = datetime.strptime(hau_day_begin,"%d-%m-%Y %H:%M:%S").date()
            date_end = date_begin + timedelta(days=1)

            data = HourlyActiveUser.objects.filter(date_time_field__gte=date_begin,
                                                date_time_field__lte=date_end).order_by('date_time_field')

            hau_labels = []
            hau_freq = []
            for obj in data:
                hau_labels.append(str(obj.date_time_field.strftime("%I %p")))
                hau_freq.append(str(obj.frequency))

            print(hau_labels)
            print(hau_freq)

            all_data = {'hau_labels': hau_labels, 'hau_freq': hau_freq}
            return JsonResponse(all_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
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

            begin_time_obj = datetime.strptime(begin_time,"%d-%m-%Y %H:%M:%S").date()
            end_temp_obj = datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").date()
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
            print("Exception: "+e)
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

            begin_time_obj = datetime.strptime(begin_time,"%d-%m-%Y %H:%M:%S").date()
            end_temp_obj = datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").date()
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
            print("Exception: "+str(e))
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)            

@login_required
def video_statistics(request):
    return render(request,'jarvis/pages/video_statistics/video_statistics.html')

def get_daily_impressions_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)            
        try:
            impr_begin = raw_data['impr_from']
            impr_end = raw_data['impr_to']

            print("impr_begin and end = "+impr_begin+", "+impr_end)

            begin_time = impr_begin + " 00:00:00"
            end_time = impr_end + " 00:00:00"

            begin_time_obj = datetime.strptime(begin_time,"%d-%m-%Y %H:%M:%S").date()
            end_temp_obj = datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").date()
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
            print("Exception: "+str(e))
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)  

def get_top_impressions_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            top_impr_date = raw_data['date']
            print top_impr_date

            day_begin = top_impr_date + " 00:00:00"

            date_begin = datetime.strptime(day_begin,"%d-%m-%Y %H:%M:%S").date()
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
            print("Exception: "+str(e))
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)  

def weekly_vplay_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)
        weekly_begin = raw_data['week_begin']
        weekly_end = raw_data['week_end']

        print("weekly_begin and end = "+weekly_begin+", "+weekly_end)

        begin_time = weekly_begin + " 00:00:00"
        end_time = weekly_end + " 00:00:00"

        begin_time_obj = datetime.strptime(begin_time,"%d-%m-%Y %H:%M:%S").date()
        end_temp_obj = datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").date()
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

                print(str(obj.user)+"    "+str(obj.videoid)+"     "+str(obj.playtime))

            this_date_data['total_playtime'] = total_playtime
            this_date_data['total_plays'] = total_plays    
            this_date_data['date'] = date.strftime("%d-%B-%Y")

            weekly_vplay_data.append(this_date_data)

        print(weekly_vplay_data)

        return JsonResponse({'weekly_data': weekly_vplay_data}, status=status.HTTP_200_OK) 

    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)              

def daily_vplay_data(request):
    if request.is_ajax():
        raw_data = json.loads(request.body)
        try:
            vplay_date = raw_data['date']
            print vplay_date

            day_begin = vplay_date + " 00:00:00"

            date_begin = datetime.strptime(day_begin,"%d-%m-%Y %H:%M:%S").date()
            date_end = date_begin + timedelta(days=1)

            vid_id_queryset = VideoCompleteRate.objects.filter(timestamp__gte=date_begin,\
                timestamp__lte=date_end)\
                .order_by('videoid')
            
            vid_list = VideoCompleteRateSerializer(vid_id_queryset, many=True).data

            vid_id = []

            for obj in vid_list:
                vid_id.append(obj.get('videoid'))
               
            vid_titles_queryset = list(Topic.objects.filter(id__in=vid_id).values('id','title'))
            vid_titles = {}
            for item in vid_titles_queryset:
                vid_titles[str(item.get('id'))] = item.get('title')

            for obj in vid_list:
                obj['title'] = vid_titles.get(obj.get('videoid'))
            
            print("vid titles : "+str(vid_titles))
            print("vid info: "+str(vid_list))

            return JsonResponse({'daily_data': vid_list}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception: "+str(e))
            return JsonResponse({'error':str(e)}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error':'not ajax'}, status=status.HTTP_200_OK)   

