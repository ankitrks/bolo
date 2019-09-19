# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv, io
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
import requests
from bs4 import BeautifulSoup
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import S3Transfer
from django.http import HttpResponse
import json
import string
import random
import os
import hashlib
import re
from drf_spirit.views import get_video_thumbnail,getVideoLength
from drf_spirit.utils  import calculate_encashable_details
from forum.topic.models import Topic
from forum.user.models import UserProfile
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





def upload_tos3(file_name,bucket):
    client = boto3.client('s3',aws_access_key_id='AKIAJMOBRHDIXGKM6W6Q',aws_secret_access_key='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')
    transfer = S3Transfer(client)
    transfer.upload_file(file_name,bucket,'instagram/'+file_name,extra_args={'ACL':'public-read'})
    file_url = 'https://'+bucket+'.s3.amazonaws.com/%s'%('instagram/'+file_name)
    transcode = transcode_media_file('instagram/'+file_name,('instagram/'+file_name).split('/')[-1].split('.')[0])
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
            uploaded_url,transcode = upload_tos3(file_name,'boloindyapp-prod')
            print uploaded_url
            thumbnail = get_video_thumbnail(file_name)
            media_duration = getVideoLength(file_name)
            create_vb = Topic.objects.create(title = description,language_id = language_id,category = Category.objects.get(title__icontains=category,parent__isnull = False),media_duration=media_duration,\
                thumbnail = thumbnail,is_vb = True,view_count = random.randint(300,400),question_image = thumbnail, backup_url=uploaded_url,question_video = transcode['new_m3u8_url']\
                ,is_transcoded = True,transcode_job_id = transcode['job_id'],user = user)
            os.remove(file_name)
            return HttpResponse(json.dumps({'message':'success','url':request.POST.get('url',None)}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'message':'success','url':request.POST.get('url',None)}),content_type="application/json")
    except Exception as e:
        print e
        return HttpResponse(json.dumps({'message':'fail','url':request.POST.get('url',None),'fail_message':str(e)}),content_type="application/json")
    


def home(request):
    return render(request,'admin/jarvis/base.html')

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




AWS_ACCESS_KEY_ID = 'AKIAZNK4CM5CW4W4VWP7'
AWS_SECRET_ACCESS_KEY = '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'
REGION_HOST = 'us-east-1'
AWS_BUCKET_NAME_TS='elastictranscode.videos'
PIPELINE_ID_TS = '1545987947390-hpo4hx'

def transcode_media_file(input_key,file_name):
    data_dump = ''
    m3u8_url = ''
    job_id = ''
    # HLS Presets that will be used to create an adaptive bitrate playlist.
    hls_64k_audio_preset_id = '1351620000001-200071';
    hls_0400k_preset_id     = '1351620000001-200050';
    # hls_0600k_preset_id     = '1351620000001-200040';
    hls_1000k_preset_id     = '1351620000001-200030';
    # hls_1500k_preset_id     = '1351620000001-200020';
    hls_2000k_preset_id     = '1351620000001-200010';

    # HLS Segment duration that will be targeted.
    segment_duration_audio = '10'
    segment_duration_400 = '10'
    segment_duration_1000 = '10'
    segment_duration_2000 = '10'

    #All outputs will have this prefix prepended to their output key.
    output_key_prefix = 'insta_transcoded/'

    # Creating client for accessing elastic transcoder 
    transcoder_client = boto3.client('elastictranscoder', REGION_HOST, aws_access_key_id = AWS_ACCESS_KEY_ID, \
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

    # Setup the job input using the provided input key.
    job_input = { 'Key': input_key }

    # Setup the job outputs using the HLS presets.
    output_key = hashlib.sha256(input_key.encode('utf-8')).hexdigest()
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
    # hls_600k = {
    #     'Key' : 'hls0600k/' + output_key,
    #     'PresetId' : hls_0600k_preset_id,
    #     'SegmentDuration' : segment_duration
    # }
    hls_1000k = {
        'Key' : 'hls1000k/' + output_key,
        'PresetId' : hls_1000k_preset_id,
        'SegmentDuration' : segment_duration_1000
    }
    # hls_1500k = {
    #     'Key' : 'hls1500k/' + output_key,
    #     'PresetId' : hls_1500k_preset_id,
    #     'SegmentDuration' : segment_duration
    # }
    hls_2000k = {
        'Key' : 'hls2000k/' + output_key,
        'PresetId' : hls_2000k_preset_id,
        'SegmentDuration' : segment_duration_2000
    }
    job_outputs = [ hls_audio, hls_400k, hls_1000k, hls_2000k ]

    playlist_name = output_key
    # Setup master playlist which can be used to play using adaptive bitrate.
    playlist = {
        'Name' : playlist_name,
        'Format' : 'HLSv3',
        'OutputKeys' : map(lambda x: x['Key'], job_outputs)
    }

    output_key_prefix_final = output_key_prefix+id_generator() + '/'
    # Creating the job.
    create_job_request = {
        'PipelineId' : PIPELINE_ID_TS,
        'Input' : job_input,
        'OutputKeyPrefix' : output_key_prefix_final,
        'Outputs' : job_outputs,
        'Playlists' : [ playlist ]
    }
    # print create_job_request
    data_dump += json.dumps(create_job_request)
    create_job_result=transcoder_client.create_job(**create_job_request)
    try:
        m3u8_url = os.path.join('https://boloindya-et.s3.amazonaws.com', \
                output_key_prefix_final, playlist_name + '.m3u8')
        job_id = create_job_result['Job']['Id']
        data_dump += 'HLS job has been created: ' + json.dumps(create_job_result)
    except Exception as e:
        data_dump += 'Exception: ' + str(e)
    return {'new_m3u8_url':m3u8_url, 'job_id':job_id}


def uploaddata(request):
    return HttpResponse()

def get_kyc_user_list(request):
    if request.user.is_superuser:
        all_kyc = UserKYC.objects.all()
        return render(request,'admin/jarvis/userkyc/user_kyc_list.html',{'all_kyc':all_kyc})

def get_kyc_of_user(request):
    if request.user.is_superuser or request.user.is_staff:
        username = request.GET.get('username',None)
        kyc_user = User.objects.get(username=username)
        kyc_details = UserKYC.objects.get(user=kyc_user)
        kyc_basic_info = KYCBasicInfo.objects.get(user=kyc_user)
        kyc_document = KYCDocument.objects.filter(user=kyc_user,is_active=True)
        additional_info = AdditionalInfo.objects.get(user=kyc_user)
        bank_details = BankDetail.objects.get(user=kyc_user,is_active=True)
        kyc_basic_reject_form = KYCBasicInfoRejectForm()
        kyc_document_reject_form = KYCDocumentRejectForm()
        kyc_additional_reject_form = AdditionalInfoRejectForm()
        kyc_bank_reject_form = BankDetailRejectForm()
        return render(request,'admin/jarvis/userkyc/single_kyc.html',{'kyc_details':kyc_details,'kyc_basic_info':kyc_basic_info,\
            'kyc_document':kyc_document,'additional_info':additional_info,'bank_details':bank_details,'userprofile':kyc_user.st,\
            'user':kyc_user,'kyc_basic_reject_form':kyc_basic_reject_form,'kyc_document_reject_form':kyc_document_reject_form,'kyc_additional_reject_form':kyc_additional_reject_form,
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
        all_encash_details = EncashableDetail.objects.all().order_by('-bolo_score_earned')
    pay_cycle = PaymentCycle.objects.all().first()
    payement_cycle_form = PaymentCycleForm(initial=pay_cycle.__dict__)
    return render(request,'admin/jarvis/payment/encashable_detail.html',{'all_encash_details':all_encash_details,'payement_cycle_form':payement_cycle_form})

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
        return render(request,'admin/jarvis/payment/single_encash_details.html',{'all_encash_details':all_encash_details,'userprofile':user.st,'user':user,'kyc_details':kyc_details,'payment_form':payment_form})


class PaymentView(FormView):
    form_class = PaymentForm
    template_name='admin/jarvis/payment/invoice_error.html'

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
        return render(self.request,'admin/jarvis/payment/invoice.html',{'success': 'success','receipt':receipt,'userprofile':userprofile })

    def get_context_data(self,*args,**kwargs):
        kwargs=super(PaymentView,self).get_context_data(*args,**kwargs)
        kwargs['http_referer']=self.request.META.get('HTTP_REFERER',None)
        return super(PaymentView,self).get_context_data(*args,**kwargs)

class PaymentCycleView(FormView):
    form_class = PaymentCycleForm
    template_name='admin/jarvis/payment/invoice_error.html'

    def form_valid(self,form,**kwargs):
        if self.request.user.is_superuser or self.request.user.is_staff:
            pay_cycle = PaymentCycle.objects.all().update(**form.cleaned_data)
            for each_user in User.objects.all():
                calculate_encashable_details(each_user)
            all_encash_details = EncashableDetail.objects.all().order_by('-bolo_score_earned')
            pay_cycle = PaymentCycle.objects.all().first()
            payement_cycle_form = PaymentCycleForm(initial=pay_cycle.__dict__)
            return render(request,'admin/jarvis/payment/encashable_detail.html',{'all_encash_details':all_encash_details,'payement_cycle_form':payement_cycle_form})


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
        user_kyc.is_kyc_additional_info_accepted and user_kyc.is_kyc_bank_details_accepted:
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
            obj = KYCBasicInfo.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        elif kyc_type == "kyc_document":
            user_kyc.is_kyc_document_info_accepted = False
            obj = KYCDocument.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        elif kyc_type == "kyc_pan":
            user_kyc.is_kyc_pan_info_accepted = False
            obj = KYCDocument.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        elif kyc_type == "kyc_profile_pic":
            user_kyc.is_kyc_selfie_info_accepted = False
            obj = KYCBasicInfo.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        elif kyc_type == "kyc_additional_info":
            user_kyc.is_kyc_additional_info_accepted = False
            obj = AdditionalInfo.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text      
        elif kyc_type == "kyc_bank_details":
            user_kyc.is_kyc_bank_details_accepted = False
            obj = BankDetail.objects.get(pk=kyc_id)
            obj.reject_reason = kyc_reject_reason
            obj.reject_text = kyc_reject_text
        obj.is_rejected = True
        obj.is_active = True
        obj.save()
        user_kyc.save()
        if not (user_kyc.is_kyc_basic_info_accepted and user_kyc.is_kyc_document_info_accepted and user_kyc.is_kyc_selfie_info_accepted and \
        user_kyc.is_kyc_additional_info_accepted and user_kyc.is_kyc_bank_details_accepted):
            user_kyc.is_kyc_accepted = False
            user_kyc.is_kyc_completed = False
            user_kyc.save()

        return HttpResponse(json.dumps({'success':'success','kyc_accepted':user_kyc.is_kyc_accepted}),content_type="application/json")





