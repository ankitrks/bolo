"""
This Api Response file will genrate a csv file at the same path where it runs which contains all the api name, path, time elapsed , size and status

The Flow for this scripts is:
1- Put a starting token of a test user.It will never expire as we put the expiration of a token 999 days through FB_LOGIN.
2- ALL_TEST_USER is manuly picked user which contains test user , our moderator and real user and set teh in list of dictionary with attribute they can craete the data or not, so onlyb test user can create teh data.
3 - Now in first api hit we all the auth token for each user using the STARTING TOKEN
4 - To perform any action on any post or comment I created the post and comments with checking whether user can craete(i.e test user)
5 - Divided the API in three parts CREATION_API, GET_API as OTHERS_API and DELETE API
6 - all the created api are hit by the test user on test user craeted data.
7 - GET_API as OTHERS_API is now hit by any user
8 - In this step teh craeted post is deleted so that all attached data to it will bw also loss
9 - a CSV will be genrarted at the same path
10 - it will emailed and the remove.

Note: 
1-To add any new api that be sure will it cause creation of data or as such data which affect the real user then add them in CREATION_API so that it will be craeted for test user.
if its only get data not real data will be affected from it the add it in GET_API known as OTHER_API
2 - Be sure about the HOST
3 - Also make sure that for media upload two sample video(SampleVideo_1280x720_10mb.mp4) and sample image(SampleJPGImage_500kbmb.jpg) is also stored at the same path


Running Mode:
activate boloindya enviroment.
run: python api_response_stats.py (Font, use the relative path as it have to select the file from the same folder,becuase it contains requests package, If its throwing error please update requests package.)
"""

import requests
import json
import random
import string
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from django.utils import timezone
from datetime import datetime,timedelta
import os

# HOST='https://www.boloindya.com'
HOST="https://engagement.boloindya.com"
# HOST='https://stage.boloindya.com'
# HOST="http://localhost:8000"

API_PREFIX="/api/v1/"

BASE_URL = HOST+API_PREFIX

STARTING_TOKEN=''
ALL_TEST_USER = [{'can_create': True, 'is_test_user': True, 'user_id': 68723},{'can_create': True, 'is_test_user': True, 'user_id': 48621},{'can_create': True, 'is_test_user': True, 'user_id': 68700},{'can_create': True, 'is_test_user': True, 'user_id': 76773},{'can_create': True, 'is_test_user': True, 'user_id': 89520},{'can_create': False, 'is_test_user': True, 'user_id': 60646},{'can_create': False, 'is_test_user': True, 'user_id': 49254},{'can_create': False, 'is_test_user': True, 'user_id': 69255},{'can_create': False, 'is_test_user': False, 'user_id': 98294},{'can_create': False, 'is_test_user': False, 'user_id': 1916},{'can_create': False, 'is_test_user': False, 'user_id': 1722},{'can_create': False, 'is_test_user': False, 'user_id': 5881},{'can_create': False, 'is_test_user': False, 'user_id': 103708}]
CAN_CREATE_USER = []
image_file = {'upload_file': open('SampleJPGImage_500kbmb.jpg','rb')}
video_file = {'upload_file': open('SampleVideo_1280x720_10mb.mp4','rb')}
csv_file =open('api_response_time.csv','wb+')
csv=''
csv+='api_name,type,url,time elapsed(milliseconds),size(kb),response\n'
csv_file.write(csv)
def send_request_to_server(name,request_type,url,auth_token,payload=None,files=None):
    try:
        url = BASE_URL+url
        if request_type =='GET' and payload:
            i=1
            no_of_keys = len(payload)
            for key,value in payload.items():
                if i==1:
                    url+='?'+str(key)+'='+str(value)
                else:
                    url+=str(key)+'='+str(value)
                if i<no_of_keys:
                    url+='&'
                i+=1

        if auth_token:
            headers = {
              'Authorization': 'Bearer '+str(auth_token)
              # 'Content-Type': 'multipart/form-data; boundary=--------------------------472110220587542779261723'
            }
        else:
            headers={

            }
        if not payload:
            payload = [

            ]
        if not files:
            files = [

            ]

        response = requests.request(request_type, url.strip(), headers=headers, data = payload, files = files)
        time_milliseconds= requests.request(request_type, url.strip(), headers=headers, data = payload, files = files).elapsed.total_seconds()*1000
        size = len(response.content)/8.0
        try:
            csv_elemnt = str(name)+','+str(request_type)+','+str(url)+','+str(time_milliseconds)+','+str(size)+','+str(response.status_code)+'\n'
        except Exception as e:
            csv_elemnt = str(name)+','+str(request_type)+','+str(url)+','+str(time_milliseconds)+','+str(size)+','+str(response.status_code)+'\n'
        csv_file.write(csv_elemnt)
        print url,"     ------->   ",str(response.status_code)
        print 'time_elapsd:  =>',time_milliseconds,"        ",'Size of repsonse:   =>',size
        if not response.status_code in [502,504,'502','504']:
            try:
                # print json.loads(response.text.encode('utf8')),csv_elemnt
                return json.loads(response.text.encode('utf8')),csv_elemnt
            except:
                # print response
                return False,csv_elemnt
        else:
            return False,csv_elemnt
    except Exception as e:
        print e
        csv_elemnt = str(name)+','+str(request_type)+','+str(url)+','+str(e)+','+str(e)+','+str(e)+'\n'
        csv_file.write(csv_elemnt)
        return False,csv_elemnt

#GET THE STARTING _TOKEN
FB_LOGIN_API ={'api_path':'fb_profile_settings/','api_name':'facebook n google login and signup with profile save','request_type':'POST','data_set':{'profile_pic': 'https://bansal.ac.in/images/logo.jpg','name': 'mohammad maaz','bio': 'aise hi','about': 'kuch bhi','username': 'abhi nai pata','refrence': 'facebook','extra_data': '{"first_name": "Abu", "last_name": "Salim", "verified": true, "name": "Abu Salim", "name_format": "{first} {last}", "locale": "en_US", "gender": "male", "friends": {"paging": {"cursors": {"after": "QVFIUktQbXhYclRQdXdFOHExOWV3MFBER3JXbDVGS1BkRXFiR0xya2gtbllyX1p4Ni1CeUlrR3pvOER2Q29jSGxydmEtb1RwSUQzd0NMTTdOZAUlhaGw1X1V3", "before": "QVFIUjFpclktbkl6WkpIOC1CZAW1rWUNSSUNfRUVRdlVjMDlBNXc5bm5HZAno3MkUyXzJSTXFZAbTFkWkVhWkgyWVkyVTN4TnB4dXYyZATB0TW5GYWlZAbXJLV29B"}}, "data": [{"name": "Asif Khan", "id": "1574950535888055"}, {"name": "Mobin Akhtar", "id": "1722572427803310"}, {"name": "Shahid Raza", "id": "1669566933137506"}, {"name": "Abid Khan", "id": "1534002520049746"}], "summary": {"total_count": 1402}}, "cover": {"source": "https://scontent.xx.fbcdn.net/v/t31.0-8/s720x720/10524245_832804866801127_3411102764525325767_o.jpg?oh=d7e90798694200bfd3a5556a1bb8b022&oe=5B0C2858", "offset_x": 0, "id": "832804866801127", "offset_y": 50}, "age_range": {"min": 21}, "email": "as.azmi21@yahoo.com", "currency": {"user_currency": "INR", "currency_offset": 100, "usd_exchange": 0.015206598, "usd_exchange_inverse": 65.7609282497}, "link": "https://www.facebook.com/app_scoped_user_id/1612763608805245/", "timezone": 5.5, "updated_time": "2018-02-21T07:44:28+0000", "can_review_measurement_request": false, "id": "1612763608805245"}','activity': 'facebook_login','categories': '16,17,19','language': '1'}}
response,csv_elemnt = send_request_to_server(FB_LOGIN_API['api_name'],FB_LOGIN_API['request_type'],FB_LOGIN_API['api_path'],None,payload=FB_LOGIN_API['data_set'])
if response:
    STARTING_TOKEN=response['access']


#1 Get the login Credentials
USER_LOGIN_API = {'api_path':'user/user_data/','api_name':'to get the token for user','request_type':'POST','data_set':ALL_TEST_USER}
for each_user in ALL_TEST_USER:
    response,csv_elemnt = send_request_to_server(USER_LOGIN_API['api_name'],USER_LOGIN_API['request_type'],USER_LOGIN_API['api_path'],STARTING_TOKEN,payload={'user_id':str(each_user['user_id'])})
    if response:
        for each in ALL_TEST_USER:
            if each['user_id']==each_user['user_id']:
                each['auth_token']=response['access_token']
        # each_user['auth_token']=response['access_token']
    csv+=csv_elemnt

for each in ALL_TEST_USER:
    # print each
    if each['can_create']:
        CAN_CREATE_USER.append(each)



CATEGORY_CHOICE = [71, 68, 70, 73, 63, 69, 75, 77, 67, 65, 72, 74, 60, 66, 76, 64, 62, 61, 58]
def get_single_category():
    return random.choice(CATEGORY_CHOICE)

LANGUGAE_CHOICE = [1,2,3,4,5,6,7,8,9]
def get_single_language():
    return random.choice(LANGUGAE_CHOICE)

TOPICS = []
def get_create_topic_data():
    return {'title':'testing_topic_boloindya','ids':get_single_language(),'category_id':get_single_category(),'media_duration':'02:00','is_vb':True,'vb_width':400,'vb_height':600,'question_video':'https://boloindyapp-prod.s3.amazonaws.com/media/SampleVideo_1280x720_10mb_158038922224.mp4','question_image':'https://www.sample-videos.com/img/Sample-jpg-image-500kb.jpg'}
MOBILE_NO={'mobile_no':9795774871}
COMMENT_ID = []
def get_single_comment():
    return random.choice(COMMENT_ID)

def get_random_user():
    return random.choice(ALL_TEST_USER)['user_id']

def get_single_topic_id():
    return random.choice(TOPICS)['id']

def random_string_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
random_string =random_string_generator()

# func for sending the csv created to the mail
def send_file_mail(HOST):
    emailfrom = "support@careeranna.com"
    emailto = ['maaz@careeranna.com','ankit@careeranna.com','akash.g@careeranna.com','gitesh@careeranna.com','abhishek@careeranna.com']
    filetosend = os.getcwd() + "/api_response_time.csv"
    username = "support@careeranna.com"
    password = "$upp0rt@30!1"               # please do not use this()

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = 'ankit@careeranna.com,maaz@careeranna.com,akash.g@careeranna.com,gitesh@careeranna.com,abhishek@careeranna.com'
    msg["Subject"] = "Bolo Indya: API Response Time and Status: " + str(datetime.now().date())+"  HOST:"+str(HOST)
    body = 'Please Find The Attachemnt. If your API is not present in the list please add them in the script api_response_time.py in scripts folder and re run.Please read the attach document before adding any api in the list.'
    body = MIMEText(body) # convert the body to a MIME compatible string
    msg.attach(body)
    msg.preamble = ""

    ctype, encoding = mimetypes.guess_type(filetosend)
    if(ctype is None or encoding is not None):
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)
    fp = open(filetosend, "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename = 'api-response-time-boloindya-' + str(datetime.now()))
    msg.attach(attachment)

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username, password)
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()
    os.remove(filetosend) #can be commented if you need file locally

RANDOM_NOTIFICATION_ACTION = ['click','GET']
AUTH_TOKEN_LIST = []
RANDOM_COMMENT_ID = []
comment_data = []
create_topic_data = []

#2 Create the topics to perform actions
for each_user in ALL_TEST_USER:
    TOPIC_CREATE_API = {'api_path':'create_topic','api_name':'For Creating Video Bytes','request_type':'POST','data_set':get_create_topic_data()}
    if each_user['can_create']:
        response,csv_elemnt = send_request_to_server(TOPIC_CREATE_API['api_name'],TOPIC_CREATE_API['request_type'],TOPIC_CREATE_API['api_path'],each_user['auth_token'],payload=get_create_topic_data(),files=None)
        csv+=csv_elemnt
        if response:
            TOPICS.append({'id':response['topic']['id'],'slug':response['topic']['slug'],'user_id':response['topic']['user']['id']})

#3 Create comments on those topics to perform actions
for each_user in ALL_TEST_USER:
    payload = {'topic_id':str(get_single_topic_id()),'comment':'testing_commnet_boloindya'}
    COMMENT_CREATE_API = {'api_path':'reply_on_topic','api_name':'For creating comment','request_type':'POST','data_set':comment_data}
    if each_user['can_create']:
        response,csv_elemnt = send_request_to_server(COMMENT_CREATE_API['api_name'],COMMENT_CREATE_API['request_type'],COMMENT_CREATE_API['api_path'],each_user['auth_token'],payload=payload,files=None)
        csv+=csv_elemnt
        # print response
        if response:
            COMMENT_ID.append(response['comment']['id'])

# #4 upload a media 
# MEDIA_UPLOAD_API={'api_path':'upload_video_to_s3/','api_name':'upload video to s3','request_type':'POST','data_set':[{'media':video_file}]}
# for each_user in ALL_TEST_USER[:1]:
#     response,csv_elemnt = send_request_to_server(MEDIA_UPLOAD_API['api_name'],MEDIA_UPLOAD_API['request_type'],MEDIA_UPLOAD_API['api_path'],each_user['auth_token'],payload=None,files={'media':video_file['upload_file']})
#     csv+=csv_elemnt

CREATE_API = [
    # {'api_path':'create_topic','api_name':'For Creating Video Bytes','request_type':'POST','data_set':create_topic_data},
    # {'api_path':'reply_on_topic','api_name':'For creating comment','request_type':'POST','data_set':comment_data},
    {'api_path':'follow_user/','api_name':'to follow user','request_type':'POST','data_set':[{'user_following_id':get_random_user()},{'user_following_id':get_random_user()},{'user_following_id':get_random_user()}]},
    {'api_path':'like/','api_name':'to like and dislike a post and a comment','request_type':'POST','data_set':[{'topic_id': get_single_topic_id() },{'comment_id': get_single_comment()}]},
    {'api_path':'sync/dump/','api_name':'dump user stats','request_type':'POST','data_set':[{'dump':'jbfdjkbajbjablablbalkbfla','dump_type':'user_dump'}]},
    {'api_path':'save_android_logs/','api_name':'to save the android logs','request_type':'POST','data_set':[{'error_log':random_string,'log_type':'click2play'}]},
    {'api_path':'register_device/','api_name':'to register device for firebase','request_type':'POST','data_set':[{'reg_id':random_string,'dev_id':random_string},{'reg_id':random_string,'dev_id':random_string}]},
    {'api_path':'unregister_device/','api_name':'to unregister device from firebase','request_type':'POST','data_set':[{'reg_id':random_string,'dev_id':random_string},{'reg_id':random_string,'dev_id':random_string}]},
    {'api_path':'vb_seen/','api_name':'when a user seen a video','request_type':'POST','data_set':[{'topic_id':get_single_topic_id()}]},
    {'api_path':'comment_view/','api_name':'topic view when user seen a comment','request_type':'GET','data_set':[{'topic_id':get_single_topic_id()},{'topic_id':get_single_topic_id()}]},
    {'api_path':'reply_delete/','api_name':'to delete the comment if owner of comment','request_type':'POST','data_set':[{'comment_id':get_single_comment()}]},
    {'api_path':'editTopic/','api_name':'edit topic','request_type':'POST','data_set':[{'topic_id':get_single_topic_id(),'title':'new testing_topic_boloindya'},{'topic_id':get_single_topic_id(),'title':'new testing_topic_boloindya'},{'topic_id':get_single_topic_id(),'title':'new testing_topic_boloindya'},{'topic_id':get_single_topic_id(),'title':'new testing_topic_boloindya'}]},
    {'api_path':'editComment/','api_name':'edit comment','request_type':'POST','data_set':[{'comment_id':get_single_comment(),'comment_text':'new testing_commnet_boloindya'},{'comment_id':get_single_comment(),'comment_text':'new testing_commnet_boloindya'},{'comment_id':get_single_comment(),'comment_text':'new testing_commnet_boloindya'},{'comment_id':get_single_comment(),'comment_text':'new testing_commnet_boloindya'},{'comment_id':get_single_comment(),'comment_text':'new testing_commnet_boloindya'},{'comment_id':get_single_comment(),'comment_text':'new testing_commnet_boloindya'}]},
    # {'api_path':'topic_delete/','api_name':'delet topic','request_type':'POST','data_set':[{'topic_id':get_single_topic_id()}]},
    {'api_path':'save_kyc_basic_info/','api_name':'To save the basic info in kYC','request_type':'POST','data_set':[{'first_name':'first_name','middle_name':'middle_name','last_name':'last_name','d_o_b':'d_o_b','mobile_no':'9795774871','email':'email'}]},
    {'api_path':'save_kyc_documents/','api_name':'To save kyc document','request_type':'POST','data_set':[{'kyc_document_type_id':'1','frontside_url':'https://www.sample-videos.com/img/Sample-jpg-image-100kb.jpg','backside_url':'https://www.sample-videos.com/img/Sample-jpg-image-500kb.jpg'}]},
    {'api_path':'save_kyc_selfie/','api_name':'to save the kyc selfie','request_type':'POST','data_set':[{'pic_selfie_url':'https://www.sample-videos.com/img/Sample-jpg-image-100kb.jpg'}]},
    {'api_path':'save_kyc_additional_info/','api_name':'to save the addinnal info of kyc','request_type':'POST','data_set':[{'father_firstname':'father_firstname','father_lastname':'father_lastname','mother_firstname':'mother_firstname','mother_lastname':'mother_lastname','profession':'1','status':'1'}]},
    {'api_path':'save_bank_details_info/','api_name':'to save the additinal info in kyc','request_type':'POST','data_set':[{'account_number':'account_number','account_name':'account_name','IFSC_code':'IFSC_code','mode_of_transaction':1},{'mode_of_transaction':2,'paytm_number':'paytm_number'}]},
    {'api_path':'fb_profile_settings/','api_name':'facebook n google login and signup with profile save','request_type':'POST','data_set':[{'profile_pic': 'https://www.sample-videos.com/img/Sample-jpg-image-100kb.jpg','cover_pic': 'https://www.sample-videos.com/img/Sample-jpg-image-500kb.jpg','name': 'my_name','bio': 'my_bio','about': 'my_about','username': 'testing_username','refrence': 'facebook','activity': 'facebook_login','language': '1','d_o_b' : 'my_date','gender' : '1','sub_category_prefrences' : '36,38,39','is_dark_mode_enabled' : True,'extra_data':'{"id":"facebook_id"}'},{'profile_pic': 'https://www.sample-videos.com/img/Sample-jpg-image-100kb.jpg','cover_pic': 'https://www.sample-videos.com/img/Sample-jpg-image-500kb.jpg','name': 'my_name','bio': 'my_bio','about': 'my_about','username': 'testing_username','refrence': 'google','activity': 'google_login','language': '1','d_o_b' : 'my_date','gender' : '1','sub_category_prefrences' : '36,38,39','is_dark_mode_enabled' : True,'extra_data':'{"google_id":"google_id"}'},{'profile_pic': 'https://www.sample-videos.com/img/Sample-jpg-image-100kb.jpg','cover_pic': 'https://www.sample-videos.com/img/Sample-jpg-image-500kb.jpg','name': 'my_name','bio': 'my_bio','about': 'my_about','username': 'testing_username','activity': 'profile_save','language': '1','d_o_b' : 'my_date','gender' : '1','sub_category_prefrences' : '36,38,39','is_dark_mode_enabled' : True}]},
    {'api_path':'predict/','api_name':'to predict a poll(OLD API/Using Nowhere)','request_type':'POST','data_set':[{'poll_id':12,'choice_id':230}]},
    {'api_path':'submit_user_feedback/','api_name':'dummy_test','request_type':'POST','data_set':[{'contact_email':'contact_email','contact_number':'contact_number','description':'description','feedback_image':'feedback_image'}]},
    {'api_path':'password/set/','api_name':'to set the password (OLD API/Using Nowhere)','request_type':'POST','data_set':[{'password':'1234567890'}]},
    {'api_path':'upload_profile_image','api_name':'To Upload the Profile Image','request_type':'POST','data_set':[{'file':image_file['upload_file']}]},
    {'api_path':'follow_sub_category/','api_name':'to follow su category','request_type':'POST','data_set':[{'sub_category_id':get_single_category()},{'sub_category_id':get_single_category()},{'sub_category_id':get_single_category()}]}

]

OTHER_API_LIST = [
    {'api_path':'topics/','api_name':'ALL TOPIC LIST (OLD API/Using Nowhere)','request_type':'GET','data_set':[{'language_id':get_single_language()},{'category':get_single_category()},{'language_id':get_single_language(),'category':get_single_category()}]},
    {'api_path':'timeline/','api_name':'GET USERPROFILE (OLD API/Using Nowhere)','request_type':'GET','data_set':[{'user_id':get_random_user()},{'category':'sports'},{'user_id':get_random_user()},{'category':'sports'}]},
    {'api_path':'search/','api_name':'Using For Searching Topic','request_type':'GET','data_set':[{'language_id':get_single_language(),'term':'love'},{'language_id':get_single_language(),'term':'the'},{'language_id':get_single_language(),'term':'what'},{'language_id':get_single_language(),'term':'mount'}]},
    {'api_path':'solr/search/','api_name':'Using For Searching Topic via SOLR','request_type':'GET','data_set':[{'language_id':get_single_language(),'term':'love'},{'language_id':get_single_language(),'term':'the'},{'language_id':get_single_language(),'term':'what'},{'language_id':get_single_language(),'term':'mount'}]},
    {'api_path':'search/users/','api_name':'Using For Searching User','request_type':'GET','data_set':[{'term':'nishachar'},{'term':'vk'},{'term':'subhas'},{'term':'gitesh'}]},
    {'api_path':'solr/search/users/','api_name':'Using For Searching User via SOLR','request_type':'GET','data_set':[{'term':'nishachar'},{'term':'vk'},{'term':'subhas'},{'term':'gitesh'}]},
    {'api_path':'solr/search/top/','api_name':'Using For Searching Top via SOLR','request_type':'GET','data_set':[{'language_id':get_single_language(),'term':'love'},{'language_id':get_single_language(),'term':'the'},{'language_id':get_single_language(),'term':'varun saxena'},{'language_id':get_single_language(),'term':'mount'}]},
    {'api_path':'comments/','api_name':'Get Comment List all (OLD API/Using Nowhere)','request_type':'GET','data_set':None},
    {'api_path':'categories/','api_name':'GET Category List','request_type':'GET','data_set':None},
    {'api_path':'get_topic/','api_name':'GET Single Topic','request_type':'GET','data_set':[{'topic_id':get_single_topic_id()},{'topic_id':get_single_topic_id()},{'topic_id':get_single_topic_id()}]},
    {'api_path':'get_question/','api_name':'Get single user topic (OLD API/Using Nowhere)','request_type':'GET','data_set':[{'user_id':get_random_user()},{'user_id':get_random_user()},{'user_id':get_random_user()}]},
    {'api_path':'get_home_answer/','api_name':'Get topic non commented by user (OLD API/Using Nowhere)','request_type':'GET','data_set':[{'language_id':get_single_language()},{'language_id':get_single_language()},{'language_id':get_single_language()}]},
    {'api_path':'get_answers/','api_name':'Get topic commented by user (OLD API/Using Nowhere)','request_type':'GET','data_set':[{'user_id':get_random_user()},{'user_id':get_random_user()},{'user_id':get_random_user()}]},
    {'api_path':'search/hash_tag/','api_name':'seacrh hash tag','request_type':'GET','data_set':[{'term':'nishachar'},{'term':'vk'},{'term':'subhas'},{'term':'gitesh'}]},
    {'api_path':'kyc_document_types','api_name':'to get the kyc document list','request_type':'GET','data_set':None},
    {'api_path':'kyc_profession_status','api_name':'to get the options profession n payment and status','request_type':'POST','data_set':None},
    {'api_path':'my_app_version/','api_name':'To get the version of app','request_type':'POST','data_set':None},
    {'api_path':'token/','api_name':'to get the token for a user','request_type':'POST','data_set':[]},
    {'api_path':'token/refresh/','api_name':'to refresh the token of a user','request_type':'POST','data_set':[]},
    # {'api_path':'otp/send/','api_name':'Send OTP for signup or signin','request_type':'POST','data_set':[{'mobile_no':MOBILE_NO['mobile_no']},{'mobile_no':MOBILE_NO['mobile_no']}]},
    {'api_path':'otp/verify/','api_name':'To verify OTP and create user or signin','request_type':'POST','data_set':[{'mobile_no':MOBILE_NO['mobile_no'],'lanagage':1,'otp':632432}]},
    {'api_path':'get_kyc_status/','api_name':'to get the kyc status','request_type':'POST','data_set':None},
    {'api_path':'get_bolo_details/','api_name':'tom get the bolo details (Using Nowhere)','request_type':'POST','data_set':[{'username':'nishachar5555'}]},
    # {'api_path':'get_encash_details/','api_name':'get all enchash details','request_type':'GET','data_set':[{'username':'nishachar5555'},{'username':'9795774871'}]},
    {'api_path':'get_follow_user/','api_name':'get follow user list','request_type':'POST','data_set':[None,{'language':'1'}]},
    {'api_path':'get_following_list/','api_name':'get following list of user','request_type':'GET','data_set':[{'user_id':get_random_user()},{'user_id':get_random_user()},{'user_id':get_random_user()}]},
    {'api_path':'get_follower_list/','api_name':'get follower list of a user','request_type':'GET','data_set':[{'user_id':get_random_user()},{'user_id':get_random_user()},{'user_id':get_random_user()}]},
    {'api_path':'shareontimeline/','api_name':'share  apost on social media','request_type':'POST','data_set':[{'topic_id':get_single_topic_id(),'share_on':'facebook_share'},{'topic_id':get_single_topic_id(),'share_on':'twitter_share'},{'topic_id':get_single_topic_id(),'share_on':'whatsapp_share'},{'topic_id':get_single_topic_id(),'share_on':'linkedin_share'}]},
    {'api_path':'mention_suggestion/','api_name':'to get suggestion for mention','request_type':'POST','data_set':[{'term':'nishachar'},{'term':'vk'},{'term':'subhas'},{'term':'gitesh'}]},
    {'api_path':'get_challenge/','api_name':'to get the challenge (OLD API/Using Nowhere)','request_type':'GET','data_set':[{'challengehash':'toungetwister'}]},
    # {'api_path':'get_user_pay_datatbale/','api_name':'dummy_test','request_type':'POST','data_set':[]},
    {'api_path':'get_challenge_details/','api_name':'to get the challenge page(OLD API/Using Nowhere) ','request_type':'POST','data_set':[{'ChallengeHash':'toungetwister'}]},
    {'api_path':'get_profile/','api_name':'to get the self profile','request_type':'GET','data_set':None},
    {'api_path':'get_sub_category/','api_name':'to get the subcategory_list','request_type':'GET','data_set':[None,{'category_id':get_single_category()}]},
    # {'api_path':'upload_audio_to_s3/','api_name':'dummy_test','request_type':'POST','data_set':[]},
    {'api_path':'follow_like_list/','api_name':'to get the follow like list to store in mobile chache','request_type':'POST','data_set':None},
    {'api_path':'notification_topic/','api_name':'to get the singel topic for notification ','request_type':'GET','data_set':[{'topic_id':get_single_topic_id()}]},
    {'api_path':'experts/','api_name':'to get the experts list','request_type':'GET','data_set':None},
    {'api_path':'get_userprofile/','api_name':'get single user profile','request_type':'POST','data_set':[{'user_id':get_random_user()}]},
    {'api_path':'get_bolo_score/','api_name':'to get ths user bolo score only','request_type':'POST','data_set':None},
    {'api_path':'get_match_list/','api_name':'to get match list(OLD API/Using Nowhere)','request_type':'GET','data_set':None},
    {'api_path':'get_single_match/','api_name':'to get single match details(OLD API/Using Nowhere)','request_type':'POST','data_set':[{'match_id':13}]},
    {'api_path':'get_single_poll/','api_name':'to get singel poll(OLD API/Using Nowhere)','request_type':'POST','data_set':[{'poll_id':12}]},
    {'api_path':'get_ip_to_language/','api_name':'to get language from IP','request_type':'GET','data_set':[{'user_ip':'127.0.0.1'}]},
    # {'api_path':'transcoder_notification/','api_name':'dummy_test','request_type':'POST','data_set':[]},
    {'api_path':'vb_transcode_status/','api_name':'get transcoding status of file','request_type':'POST','data_set':[{'topic_id':get_single_topic_id()}]},
    {'api_path':'get_vb_list/','api_name':'get list of vb','request_type':'GET','data_set':[{'category':'sports','is_popular':True,'language_id':get_single_language()},{'category':'sports','language_id':get_single_language()},{'category':'sports','language_id':get_single_language()},{'user_id':get_random_user()},{'category':'sports','language_id':get_single_language(),'is_expand':'yes'}]},
    {'api_path':'leaderboard_view/','api_name':'to get the leader board(OLD API/Using Nowhere) ','request_type':'GET','data_set':None},
    # {'api_path':'get_hash_list/','api_name':'to get the all hash tag with 3 video','request_type':'POST','data_set':None},
    {'api_path':'get_user_bolo_info/','api_name':'to get the bolo info on click bolo info ','request_type':'POST','data_set':[{'start_date':'20-08-2019','end_date':'13-05-2020'},{'month':'11','year':'2019'},None]},
    {'api_path':'hashtag_suggestion/','api_name':'sugest hashtag','request_type':'POST','data_set':[{'term':'nishachar'},{'term':'vk'},{'term':'subhas'},{'term':'gitesh'}]},
    {'api_path':'solr/hashtag_suggestion/','api_name':'sugest hashtag via SOLR','request_type':'POST','data_set':[{'term':'nishachar'},{'term':'vk'},{'term':'subhas'},{'term':'gitesh'}]},
    # {'api_path':'user/statistics/','api_name':'dummy_test','request_type':'POST','data_set':[]},
    {'api_path':'get_category_detail/','api_name':'get singel cateogry detail','request_type':'POST','data_set':[{'category_id':get_single_category()},{'category_id':get_single_category()}]},
    {'api_path':'get_category_detail_with_views/','api_name':'get single category page','request_type':'POST','data_set':[{'category_id':get_single_category(),'language_id':get_single_language()},{'category_id':get_single_category(),'language_id':get_single_language()}]},
    {'api_path':'get_category_video_bytes/','api_name':'get single category paginated video bytes','request_type':'POST','data_set':[{'category_id':get_single_category(),'language_id':get_single_language()},{'category_id':get_single_category(),'language_id':get_single_language()}]},
    {'api_path':'get_popular_video_bytes/','api_name':'get only popular video bytes','request_type':'GET','data_set':[{'language_id':get_single_language()},{'language_id':get_single_language()}]},
    # {'api_path':'pubsub/popular/','api_name':'dummy_test','request_type':'POST','data_set':[]},
    {'api_path':'get_user_follow_and_like_list/','api_name':'to get user folow comment and like list when aapp initalize','request_type':'POST','data_set':None},
    {'api_path':'get_recent_videos/','api_name':'to get trending video','request_type':'GET','data_set':[{'language_id':get_single_language()},{'language_id':get_single_language()},{'language_id':get_single_language(),'is_expand':'yes'}]},
    {'api_path':'get_landing_page_video/','api_name':'get popup video when app opens','request_type':'POST','data_set':[{'language_id':get_single_language()},{'language_id':get_single_language()},{'language_id':get_single_language(),'is_expand':'yes'}]},
    {'api_path':'get_popular_bolo/','api_name':'get popular boloindyans list','request_type':'GET','data_set':[{'language_id':get_single_language()},{'language_id':get_single_language()},{'language_id':get_single_language(),'is_expand':'yes'}]},
    {'api_path':'get_category_with_video_bytes/','api_name':'get homepage videos with category','request_type':'GET','data_set':[{'language_id':get_single_language(),'is_discover':True},{'language_id':get_single_language()},{'language_id':get_single_language(),'is_expand':'yes'}]},
    {'api_path':'notification/get','api_name':'get notificationo the user','request_type':'POST','data_set':None},
    {'api_path':'get_hash_discover/','api_name':'DISCOVER HASHTAG','request_type':'GET','data_set':[{'language_id':get_single_language()},{'language_id':get_single_language()},{'language_id':get_single_language(),'is_expand':'yes'}]},
    {'api_path':'get_hash_discover_topics/','api_name':'DISCOVER HASHTAG  TOPICS','request_type':'GET','data_set':[{'ids':get_single_topic_id()},{'ids':get_single_topic_id()},{'ids':get_single_topic_id(),'is_expand':'yes'}]},
    # {'api_path':'notification/click','api_name':'set notifiacation as seen','request_type':'POST','data_set':None}
]

for each_id in TOPICS:
    OTHER_API_LIST = OTHER_API_LIST +[{'api_path':'topics/'+each_id['slug']+'/'+str(each_id['id'])+'/comments/','api_name':'get tpic list  (OLD API/Using Nowhere)','request_type':'POST','data_set':None}]
    OTHER_API_LIST = OTHER_API_LIST +[{'api_path':'topics/'+each_id['slug']+'','api_name':'get single topic filter by slug (OLD API/Using Nowhere)','request_type':'POST','data_set':None}]
for each_comment_id in COMMENT_ID:
    OTHER_API_LIST = OTHER_API_LIST +[{'api_path':'comments/'+str(each_comment_id)+'','api_name':'if some one commented click on notifiction it will open to same comment','request_type':'GET','data_set':None}]

for each_api in CREATE_API:
    each_user = random.choice(CAN_CREATE_USER)
    if each_api['data_set']:
        for each_data_set in each_api['data_set']:
            if each_data_set:
                if 'file' in each_api['data_set']:
                    response,csv_elemnt = send_request_to_server(each_api['api_name'],each_api['request_type'],each_api['api_path'],each_user['auth_token'],payload=None,files=each_data_set)
                else:
                    response,csv_elemnt = send_request_to_server(each_api['api_name'],each_api['request_type'],each_api['api_path'],each_user['auth_token'],payload=each_data_set,files=None)
            else:
                response,csv_elemnt = send_request_to_server(each_api['api_name'],each_api['request_type'],each_api['api_path'],each_user['auth_token'],payload=None,files=None)
            
            csv+=csv_elemnt
    else:
        response,csv_elemnt = send_request_to_server(each_api['api_name'],each_api['request_type'],each_api['api_path'],each_user['auth_token'],payload=None,files=None)
        csv+=csv_elemnt

for each_api in OTHER_API_LIST:
    each_user = random.choice(ALL_TEST_USER)
    if each_api['data_set']:
        for each_data_set in each_api['data_set']:
            if each_data_set:
                if 'file' in each_api['data_set']:
                    response,csv_elemnt = send_request_to_server(each_api['api_name'],each_api['request_type'],each_api['api_path'],each_user['auth_token'],payload=None,files=each_data_set)
                else:
                    response,csv_elemnt = send_request_to_server(each_api['api_name'],each_api['request_type'],each_api['api_path'],each_user['auth_token'],payload=each_data_set,files=None)
            else:
                response,csv_elemnt = send_request_to_server(each_api['api_name'],each_api['request_type'],each_api['api_path'],each_user['auth_token'],payload=None,files=None)
            
            csv+=csv_elemnt
    else:
        response,csv_elemnt = send_request_to_server(each_api['api_name'],each_api['request_type'],each_api['api_path'],each_user['auth_token'],payload=None,files=None)
        csv+=csv_elemnt

#
for each_user in ALL_TEST_USER:
    for each_topic in TOPICS:
        TOPIC_DELETE_API = {'api_path':'topic_delete/','api_name':'delet topic','request_type':'POST','data_set':[{'topic_id':each_topic['id']}]}
        if str(each_user['user_id'])==str(each_topic['user_id']):
            response,csv_elemnt = send_request_to_server(TOPIC_DELETE_API['api_name'],TOPIC_DELETE_API['request_type'],TOPIC_DELETE_API['api_path'],each_user['auth_token'],payload={'topic_id':each_topic['id']},files=None)
            csv+=csv_elemnt

csv_file.close()
send_file_mail(HOST)


# Will change to function later by removing same code multiple time above
# def serve_api_request(api_dict,user):
#     if api_dict['data_set']:
#         for each_data_set in api_dict['data_set']:
#             if each_data_set:
#                 if 'file' in api_dict['data_set']:
#                     response,csv_elemnt = send_request_to_server(api_dict['api_name'],api_dict['request_type'],api_dict['api_path'],user['auth_token'],payload=None,files=each_data_set)
#                 else:
#                     response,csv_elemnt = send_request_to_server(api_dict['api_name'],api_dict['request_type'],api_dict['api_path'],user['auth_token'],payload=each_data_set,files=None)
#             else:
#                 response,csv_elemnt = send_request_to_server(api_dict['api_name'],api_dict['request_type'],api_dict['api_path'],user['auth_token'],payload=None,files=None)
            
#             csv+=csv_elemnt
#     else:
#         response,csv_elemnt = send_request_to_server(api_dict['api_name'],api_dict['request_type'],api_dict['api_path'],user['auth_token'],payload=None,files=None)
#         csv+=csv_elemnt
