from .models import *
from forum.topic.utils import get_redis_fcm_token
from oauth2client.service_account import ServiceAccountCredentials
import os
from django.conf import settings


def get_token_for_user_id(user_id):
	#it will return the list of tokens for user_id
	token_list = list(FCMDevice.objects.filter(user_id=user_id, is_uninstalled=False).values_list('reg_id', flat = True))
	token = get_redis_fcm_token(user_id)
	if token:
		token_list+=[token]
	token_list= set(token_list)
	return list(token_list)



def _get_access_token():
  """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(settings.BASE_DIR, 'boloindya-1ec98-firebase-adminsdk-ldrqh-27bdfce28b.json'), "https://www.googleapis.com/auth/firebase.messaging")
  access_token_info = credentials.get_access_token()
  request_url = settings.PUSH_NOTIFICATION_URL
  return access_token_info.access_token ,request_url
