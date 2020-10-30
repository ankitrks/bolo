from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from django.conf import settings
import json
import boto3
import os

def get_firebase_remote_config():
	SCOPES = ['https://www.googleapis.com/auth/firebase.remoteconfig']
	SERVICE_ACCOUNT_FILE = settings.FIREBASE_SERVICE_ACCOUNT_FILE_PATH
	if not os.path.exists(SERVICE_ACCOUNT_FILE):
		SERVICE_ACCOUNT_FILE = get_service_account_file()
	credentials = service_account.Credentials.from_service_account_file(
		SERVICE_ACCOUNT_FILE, scopes=SCOPES)
	authed_session = AuthorizedSession(credentials)
	data = authed_session.get(settings.FIREBASE_REMOTE_CONFIG_URL)
	return json.loads(data.text)

def get_service_account_file():
	client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
	file_name = 'boloindya_firebase_remote_config.json'
	client.download_file(settings.BOLOINDYA_EVENT_INVOICE_BUCKET_NAME, file_name, settings.FIREBASE_SERVICE_ACCOUNT_FILE_PATH)