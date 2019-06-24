import hashlib
import json
import boto3
from django.conf import settings

def transcode_media_file(input_key):
    data_dump = ''
    # HLS Presets that will be used to create an adaptive bitrate playlist.
    hls_64k_audio_preset_id = '1351620000001-200071';
    hls_0400k_preset_id     = '1351620000001-200050';
    hls_0600k_preset_id     = '1351620000001-200040';
    hls_1000k_preset_id     = '1351620000001-200030';
    hls_1500k_preset_id     = '1351620000001-200020';
    hls_2000k_preset_id     = '1351620000001-200010';

    # HLS Segment duration that will be targeted.
    segment_duration = '2'

    #All outputs will have this prefix prepended to their output key.
    output_key_prefix = 'elastic-transcoder/output/hls/'

    # Creating client for accessing elastic transcoder 
    transcoder_client = boto3.elastictranscoder.connect_to_region(settings.REGION_HOST, \
            aws_access_key_id = settings.AWS_ACCESS_KEY_ID_TS, \
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY_TS)

    # Setup the job input using the provided input key.
    job_input = { 'Key': input_key }

    # Setup the job outputs using the HLS presets.
    output_key = hashlib.sha256(input_key.encode('utf-8')).hexdigest()
    hls_audio = {
        'Key' : 'hlsAudio/' + output_key,
        'PresetId' : hls_64k_audio_preset_id,
        'SegmentDuration' : segment_duration
    }
    hls_400k = {
        'Key' : 'hls0400k/' + output_key,
        'PresetId' : hls_0400k_preset_id,
        'SegmentDuration' : segment_duration
    }
    hls_600k = {
        'Key' : 'hls0600k/' + output_key,
        'PresetId' : hls_0600k_preset_id,
        'SegmentDuration' : segment_duration
    }
    hls_1000k = {
        'Key' : 'hls1000k/' + output_key,
        'PresetId' : hls_1000k_preset_id,
        'SegmentDuration' : segment_duration
    }
    hls_1500k = {
        'Key' : 'hls1500k/' + output_key,
        'PresetId' : hls_1500k_preset_id,
        'SegmentDuration' : segment_duration
    }
    hls_2000k = {
        'Key' : 'hls2000k/' + output_key,
        'PresetId' : hls_2000k_preset_id,
        'SegmentDuration' : segment_duration
    }
    job_outputs = [ hls_audio, hls_400k, hls_600k, hls_1000k, hls_1500k, hls_2000k ]

    # Setup master playlist which can be used to play using adaptive bitrate.
    playlist = {
        'Name' : 'hls_' + output_key,
        'Format' : 'HLSv3',
        'OutputKeys' : map(lambda x: x['Key'], job_outputs)
    }

    # Creating the job.
    create_job_request = {
        'pipeline_id' : settings.PIPELINE_ID_TS,
        'input_name' : job_input,
        'output_key_prefix' : output_key_prefix + output_key +'/',
        'outputs' : job_outputs,
        'playlists' : [ playlist ]
    }
    data_dump += json.dumps(create_job_request)
    create_job_result=transcoder_client.create_job(**create_job_request)
    data_dump += 'HLS job has been created: ', json.dumps(create_job_result['Job'], indent=4, sort_keys=True)
    return data_dump
