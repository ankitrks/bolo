# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import http
from django.shortcuts import render
import boto3
from django.views.generic.base import View
bucketName = "Your S3 BucketName"
Key = "Original Name and type of the file you want to upload into s3"
outPutname = "Output file name(The name you want to give to the file after we upload to s3)"


class AudioFileCreateViewMixin(View):
    model = None
    create_field = None

    def create_object(self, audio_file):
        return self.model.objects.create(**{self.create_field: audio_file})

    def post(self, request):
        audio_file = request.FILES.get('audio_file', None)

        if audio_file is None:
            return http.HttpResponseBadRequest()

        result = self.create_object(audio_file)
        print result.audio_file.url
        return http.JsonResponse({
            'id': result.pk,
            'url': result.audio_file.url,
        }, status=201)

# s3 = boto3.resource('s3')
# s3.meta.client.upload_file('/tmp/hello.txt', 'mybucket', 'hello.txt') 

# s3 = boto3.client('s3')
# s3.upload_file(Key,bucketName,outPutname)       