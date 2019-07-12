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


def upload_tos3(file_name,bucket):
    client = boto3.client('s3',aws_access_key_id='AKIAJMOBRHDIXGKM6W6Q',aws_secret_access_key='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')
    transfer = S3Transfer(client)
    transfer.upload_file(file_name,bucket,'instagram/'+file_name,extra_args={'ACL':'public-read'})
    file_url = 'https://'+bucket+'buckets3.amazonaws.com/%s'%('instagram/'+file_name)
    transcode = transcode_media_file('instagram/'+file_name,('instagram/'+file_name).split('/')[-1].split('.')[0])
    return file_url,transcode


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def geturl(request):
    try:
        print request.POST.get('url',None)
        url = requests.get(request.POST.get('url',None))
        description = request.POST.get('description',None)
        username = request.POST.get('username',None)
        print username,description
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
        return HttpResponse(json.dumps({'message':'success','url':request.POST.get('url',None)}),content_type="application/json")
    except Exception as e:
        print e
        return HttpResponse(json.dumps({'message':'fail','url':request.POST.get('url',None)}),content_type="application/json")
    


def home(request):
    return render(request,'admin/jarvis/base.html')


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