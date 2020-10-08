from django.conf import settings

from forum.comment.models import GiphyDetails
from forum.comment.utils import update_giphy_redis

import requests
import pandas as pd


class AddGiphyDetailsToDatabase:
	def __init__(self, *args, **kwargs):
		self.offset = int(kwargs.get('offset', 0))
		self.page_size = int(kwargs.get('page_size', 150))
		self.data_limit = int(kwargs.get('data_limit',settings.GIPHY_DATA_LIMIT))

	def start(self):
		try:
			end_index = int(self.offset) + int(self.data_limit)
			while(self.offset<end_index):
				EndPoint = settings.GIPHY_TRENDING_API_ENDPOINT+"&limit={}&offset={}".format(self.page_size, self.offset)
				response = requests.get(EndPoint)
				df = pd.DataFrame(response.json()['data'])
				if not df.empty:
					data = df['id'].unique()

					#remove exisitng ids
					exisiting_giphy_ids = GiphyDetails.objects.values_list('giphy_id',flat=True)
					remaining_ids = [id_ for id_ in data if id_ not in exisiting_giphy_ids]

					#store in database
					bulk_dict = [{"giphy_id": id_} for id_ in remaining_ids]
					giphy_list = [GiphyDetails(**vals) for vals in bulk_dict]
					GiphyDetails.objects.bulk_create(giphy_list, batch_size=10000)

					#update keys in redis
					update_giphy_redis(data)

					self.offset+=self.page_size
					print("completed occurence with offset "+str(self.offset))
				else:
					print("Empty response from giphy endpoint")
		except Exception as e:
			print(e)

def run(*args):
	offset, data_limit, page_size = 0, settings.GIPHY_DATA_LIMIT, 150
	for arg in args:
		key = arg.split("=")[0]
		value = arg.split("=")[1]
		if key=="offset":
			offset = value
		elif key=="data_limit":
			data_limit = value
		elif key=="page_size":
			page_size = value
	instance = AddGiphyDetailsToDatabase(offset=offset, data_limit=data_limit, page_size=page_size)
	instance.start()