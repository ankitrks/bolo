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


def upload_tos3(file_name,bucket):
    client = boto3.client('s3',aws_access_key_id='AKIAJMOBRHDIXGKM6W6Q',aws_secret_access_key='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')
    transfer = S3Transfer(client)
    transfer.upload_file(file_name,'testingbucketvideos',file_name,extra_args={'ACL':'public-read'})
    file_url = '%s/%s/%s'%(client.meta.endpoint_url,'testingbucketvideos',file_name)
    print("Uploaded!")
    return file_url


def geturl(url):
    r = requests.get(url)
    txt = r.text
    html = BeautifulSoup(txt,'html.parser')
    video_url = html.find(property="og:video").get('content')
    video_title = html.find(property="og:title").get('content')
    video_image = html.find(property="og:image").get('content')
    r = requests.get(video_url,stream=True)
    file_name = video_url.split('/')[-1]
    file_name = file_name.split('?')[0]
    with open(file_name,'wb') as f:
        for chunk in r.iter_content(chunk_size = 1024*1024):
            if chunk:
                f.write(chunk)
    return upload_tos3(file_name,'testingbucketvideos')


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
        print(data)
    
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

def uploaddata(request):
    return HttpResponse()