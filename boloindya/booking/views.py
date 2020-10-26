# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.generic import RedirectView

from rest_framework import status
from rest_framework.views import APIView

from forum.user.models import UserProfile
from forum.topic.models import TongueTwister
from forum.user.utils.bolo_redis import get_userprofile_counter
from .serializers import BookingSerializer, PayOutConfigSerializer
from .models import *
from .utils import booking_options
# Create your views here.
from datetime import datetime, timedelta
from drf_spirit.views import remove_extra_char
from tasks import upload_event_media
import pandas as pd
import numpy as np
import time
import boto3
import json
import os

from payment.razorpay import create_order

class BookingDetails(APIView):
	def get(self, request, *args, **kwargs):
		try:
			if request.user.is_authenticated:
				booking_id = request.GET.get('booking_id',None)
				if booking_id:
					return self.get_booking_detail(booking_id, request.user.id)

				else:
					page_no = request.GET.get('page',1)
					return self.get_booking_list(request.user.id, page_no)
			else:
				return JsonResponse({'message':'Unauthorised User', 'data':[]}, status=status.HTTP_401_UNAUTHORIZED)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)

	def post(self, request, *args, **kwargs):
		try:
			if request.user.is_authenticated:
				# booking_id = request.POST.get('booking_id', None)
				booking_slot_id = request.POST.get('booking_slot_id', None)
				booking_slot = list(BookingSlot.objects.filter(pk=booking_slot_id).values('start_time', 'id', 'end_time', 'booking_id','channel_id'))
				if booking_slot:
					booking_id = booking_slot[0]['booking_id']
					already_booked = UserBooking.objects.filter(Q(user_id=request.user.id, booking_id=booking_id) | Q(booking_slot_id=booking_slot_id))
					if not already_booked:
						UserBooking(user_id=request.user.id, booking_id=booking_id, booking_slot_id=booking_slot_id).save()
						booking_count = UserBooking.objects.filter(booking_id=booking_id).count()
						result = {}
						result['message'] = 'You have successfully booked this session'
						booking_slot[0]['channel_url'] = settings.BOOKING_SLOT_URL+booking_slot[0]['channel_id']
						result['data'] = booking_slot[0]
						result['count'] = booking_count
						return JsonResponse(result, status=status.HTTP_200_OK)
					else:
						return JsonResponse({'message': "Already Booked",'data':{}}, status=status.HTTP_200_OK)
				else:
					return JsonResponse({'message': "Invalid Slot Id",'data':{}}, status=status.HTTP_400_BAD_REQUEST)
			else:
				return JsonResponse({'message':'Unauthorised User', 'data':{}}, status=status.HTTP_401_UNAUTHORIZED)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)

	def get_booking_detail(self, booking_id, user_id):
		try:
			booking = Booking.objects.get(id=booking_id)
			booking_details = BookingSerializer(booking).data
			user_booking = list(UserBooking.objects.filter(user_id=user_id, booking_id=booking_details['id']).values_list('booking_slot_id', flat=True))
			
			already_booked_ids = UserBooking.objects.filter(booking_id=booking_id).values('booking_slot_id')
			booking_slots = list(BookingSlot.objects.filter(booking_id=booking_details['id'],end_time__gt=datetime.now()).exclude(id__in=already_booked_ids).order_by('start_time').values('id', 'start_time', 'end_time', 'channel_id'))
			booking_details['is_slot_available'] = True if len(booking_slots) else False
			booking_details['is_booked'] = False

			booking_details['slots'] = self.get_slots_data(booking_slots)#booking_slots
			booking_details['booked_slot'] = None

			if user_booking:
				user_booking_slot = list(BookingSlot.objects.filter(id__in=user_booking, end_time__gt=datetime.now()).values('id', 'start_time', 'end_time', 'channel_id'))
				if user_booking_slot:
					booking_details['booked_slot'] = self.get_slots_data(user_booking_slot)[0]
					booking_details['is_booked'] = True


			return JsonResponse({'message': 'success', 'data':  booking_details}, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)

	def get_booking_list(self, user_id, page_no):
		try:
			bookings = Booking.objects.all().order_by('id').values('id', 'creator_id', 'title', 'thumbnail_img_url')
			user_bookings = UserBooking.objects.filter(user_id=user_id).values('booking_id')
			bookings_df = pd.DataFrame.from_records(bookings)
			user_bookings_df = pd.DataFrame.from_records(user_bookings)
			bookings_df['is_slot_available'] = False
			if not bookings_df.empty:
				booking_slots_df = pd.DataFrame.from_records(BookingSlot.objects.filter(end_time__gt=datetime.now()).values('end_time','booking_id'))
				if not booking_slots_df.empty:
					bookings_df['is_slot_available'] = np.where(bookings_df['id'].isin(booking_slots_df['booking_id'].unique()),True, False)
			if not user_bookings_df.empty:
				bookings_df['is_booked'] = np.where(bookings_df['id'].isin(user_bookings_df['booking_id'].unique()), True, False)
			result = bookings_df.to_dict('records')
			paginator = Paginator(result, settings.GET_BOOKINGS_API_PAGE_SIZE)
			try:
				result = paginator.page(page_no).object_list
			except:
				result = []
			return JsonResponse({'message': 'success', 'data':  result}, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)

	def get_slots_data(self,booking_slots):
		booking_slots_df = pd.DataFrame.from_records(booking_slots)
		slots = []
		if not booking_slots_df.empty:
			booking_slots_df['date'] = booking_slots_df['start_time'].dt.date
			unique_dates = booking_slots_df['date'].unique()
			booking_slots_df['start_time'] = booking_slots_df['start_time'].dt.strftime('%H:%M:%S').astype(str)
			booking_slots_df['end_time'] = booking_slots_df['end_time'].dt.strftime('%H:%M:%S').astype(str)
			booking_slots_df['channel_url'] = settings.BOOKING_SLOT_URL+booking_slots_df['channel_id']
			for date in unique_dates:
				new_slots = {}
				temp = booking_slots_df[booking_slots_df['date']==date]
				temp.drop(['date'], axis=1, inplace=True)
				new_slots['date'] = date
				new_slots['time'] = temp.to_dict('records')
				slots.append(new_slots)
		return slots

class UserBookingList(APIView):
	def get(self, request, *args, **kwargs):
		try:
			if request.user.is_authenticated:
				page_no = request.GET.get('page',1)
				user_bookings = list(UserBooking.objects.filter(user_id=request.user.id).values('booking_id', 'booking_slot_id', 'booking_status'))
				user_booking_ids = [value['booking_id'] for value in user_bookings]
				user_booking_slot_ids = [value['booking_slot_id'] for value in user_bookings]
				bookings = Booking.objects.filter(id__in=user_booking_ids).values('id','title','thumbnail_img_url')
				booking_slots = BookingSlot.objects.filter(id__in=user_booking_slot_ids).values('start_time','end_time', 'id','booking_id','channel_id')

				result = []
				if user_bookings:
					bookings_df = pd.DataFrame.from_records(bookings)
					booking_slot_df = pd.DataFrame.from_records(booking_slots).drop(['id'], axis=1)
					user_booking_df = pd.DataFrame.from_records(user_bookings)

					final_df = pd.merge(pd.merge(bookings_df,booking_slot_df,left_on='id',right_on='booking_id'),user_booking_df,on='booking_id')
					final_df = update_slot_status(final_df)
					final_df.drop(['booking_id'], axis=1, inplace=True)
					final_df['channel_url'] = settings.BOOKING_SLOT_URL+final_df['channel_id']
					final_df = final_df.replace({"booking_status": booking_options})
					result = final_df.to_dict('records')
					paginator = Paginator(result, settings.GET_BOOKINGS_API_PAGE_SIZE)
					try:
						result = paginator.page(page_no).object_list
					except:
						result = []
				return JsonResponse({'message': 'success', 'data':  result}, status=status.HTTP_200_OK)

			else:
				return JsonResponse({'message':'Unauthorised User', 'data':[]}, status=status.HTTP_401_UNAUTHORIZED)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)

class MySlotsList(APIView):
	def get(self, request, *args, **kwargs):
		try:
			if request.user.is_authenticated:
				page_no = request.GET.get('page',1)
				booking_ids = Booking.objects.filter(creator_id=request.user.id).values('id')
				booking_slots = BookingSlot.objects.filter(booking_id__in=booking_ids).values('start_time','end_time','channel_id','id')
				booking_slots_df = pd.DataFrame.from_records(booking_slots)
				result = []
				if not booking_slots_df.empty:
					booked_slots = UserBooking.objects.filter(booking_slot_id__in=booking_slots_df['id'].unique()).values('booking_slot_id', 'booking_status', 'user_id')
					booked_slots_df = pd.DataFrame.from_records(booked_slots)
					final_df = booking_slots_df
					if not booked_slots_df.empty:
						final_df = pd.merge(booking_slots_df, booked_slots_df,left_on='id',right_on='booking_slot_id')
						final_df = update_slot_status(final_df)
						if not final_df.empty:
							users = User.objects.filter(id__in=final_df['user_id'].unique()).values('username','id')
							user_df = pd.DataFrame.from_records(users)
							final_df = pd.merge(final_df,user_df,left_on='user_id',right_on='id')
							final_df = final_df.rename(columns={'username': 'booked_by', 'id_x': 'slot_id'})
							final_df.drop(['booking_slot_id', 'id_y', 'user_id'], axis=1,inplace=True)
							final_df = final_df.replace({"booking_status": booking_options})
							final_df['channel_url'] = settings.BOOKING_SLOT_URL+final_df['channel_id']
							result = final_df.to_dict('records')
							paginator = Paginator(result, settings.GET_BOOKINGS_API_PAGE_SIZE)
							try:
								result = paginator.page(page_no).object_list
							except:
								result = []
				return JsonResponse({'message': 'success', 'data':  result}, status=status.HTTP_200_OK)
			else:
				return JsonResponse({'message':'Unauthorised User', 'data':[]}, status=status.HTTP_401_UNAUTHORIZED)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)


def update_slot_status(slots_df):
	slots_df['booking_status'] = np.where(slots_df['end_time']<datetime.now(), '2', slots_df.booking_status)
	slots_df['booking_status'] = np.where((slots_df['start_time']<=datetime.now())&(slots_df['end_time']>=datetime.now()), '1', slots_df.booking_status)
	return slots_df

def get_time(time):
	"""
		This function takes string time in format HH:MM
		and return a time object
	"""
	import datetime
	time_list = list(map(int, time.split(":")))
	return datetime.time(hour=time_list[0], minute=time_list[1])

def get_thumbnail_url(banner_img_url, key):
	try:
		final_file_name = key+banner_img_url.split('/')[-1]
		thumbnail_img_url = "http://in-boloindya.s3-website.ap-south-1.amazonaws.com/180x240/"+final_file_name
		return thumbnail_img_url
	except:
		return ''

def upload_media(media_file, file_name, key):
	try:
		from jarvis.views import urlify
		client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
		ts = time.time()
		created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		media_file_name = remove_extra_char(str(file_name))
		filenameNext= media_file_name.split('.')
		final_filename = str(urlify(filenameNext[0]))+"_"+ str(ts).replace(".", "")+"."+str(filenameNext[1])
		response = client.upload_file(media_file, settings.BOLOINDYA_AWS_IN_BUCKET_NAME,key + final_filename)
		filepath = 'https://s3.ap-south-1.amazonaws.com/' + settings.BOLOINDYA_AWS_IN_BUCKET_NAME + "/"+ key + final_filename
		return filepath
	except Exception as e:
		print(e)
		return ''

class PayOutConfigDetails(APIView):
	def get(self, request, *args, **kwargs):
		try:
			payout_obj = PayOutConfig.objects.last()
			return JsonResponse({'message': 'success', 'data': PayOutConfigSerializer(payout_obj).data}, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e), 'data':{}}, status=status.HTTP_400_BAD_REQUEST)

class EventDetails(APIView):
	def get(self, request, *args, **kwargs):
		try:
			event_id = request.GET.get('event_id',None)
			if event_id:
				return self.get_event_detail(event_id)
			else:
				page_no = request.GET.get('page',1)
				return self.get_event_list(page_no)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e), 'data':{}}, status=status.HTTP_400_BAD_REQUEST)

	def post(self, request, *args, **kwargs):
		import datetime
		try:
			if request.user.is_authenticated:
				title = request.POST.get('title','')
				description = request.POST.get('description','')
				promo_profile_pic = request.FILES.get('promo_profile_pic','')
				promo_banner = request.FILES.get('promo_banner','')
				slots = request.POST.get('slots','')
				price_per_user = request.POST.get('price_per_user',0)
				language_ids = request.POST.get('language_selected',[])
				hash_tags = request.POST.get('hashtags', None)
				category_id = request.POST.get('category_selected',None)

				if promo_profile_pic and not promo_profile_pic.name.endswith(('.jpg','.png', '.jpeg')):
					return JsonResponse({'message':'fail','reason':'This is not a jpg/png file'}, status=status.HTTP_200_OK)
				if promo_banner and not promo_banner.name.endswith(('.jpg','.png', '.jpeg')):
					return JsonResponse({'message':'fail','reason':'This is not a jpg/png file'}, status=status.HTTP_200_OK)

				if language_ids:
					language_ids = json.loads(language_ids)
				event = Event(creator_id = request.user.id, title=title,description=description,price=price_per_user,category_id = category_id, language_ids = language_ids)
				event.save()

				#upload image
				self.download_and_upload_events(event.id, promo_profile_pic, promo_banner)

				hash_tags_to_add = []
				if hash_tags:
					hash_tags = json.loads(hash_tags)
					for index, value in enumerate(hash_tags):
						if value.startswith("#"):
							try:
								tag = TongueTwister.objects.using('default').get(hash_tag__iexact=value.strip('#'))
							except :
								tag = TongueTwister.objects.create(hash_tag=value.strip('#'))
							hash_tags_to_add.append(tag)
				if hash_tags_to_add:
					event.hash_tags.add(*hash_tags_to_add)

				#slots create
				event_slots = []
				event_id = event.id
				if slots:
					slots = json.loads(slots)
					start_date = datetime.datetime.strptime(slots['start_date'], "%Y-%m-%d").date()
					end_date = datetime.datetime.strptime(slots['end_date'], "%Y-%m-%d").date()
					while(start_date<=end_date):
						for value in slots['time']:
							start_time = get_time(value['start_time'])
							end_time = get_time(value['end_time'])

							event_slot_start_time = datetime.datetime.combine(start_date,start_time)
							event_slot_end_time = datetime.datetime.combine(start_date,end_time)
							event_slots.append({"start_time": event_slot_start_time, "end_time": event_slot_end_time, "event_id": event_id})
						start_date+=datetime.timedelta(days=1)
					slot_list = [EventSlot(**vals) for vals in event_slots]
					EventSlot.objects.bulk_create(slot_list)
				return JsonResponse({'message': 'success'}, status=status.HTTP_200_OK)
			else:
				return JsonResponse({'message':'Unauthorised User'}, status=status.HTTP_401_UNAUTHORIZED)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

	def get_event_detail(self, event_id):
		event = Event.objects.filter(id=event_id)#.values('id', 'title', 'thumbnail_img_url', 'banner_img_url', 'profile_pic_img_url','price', 'description')
		event_slots = []
		result = {}
		if event:
			event_slots = event[0].event_slot.all()
		event = event.values('id', 'title', 'thumbnail_img_url', 'banner_img_url', 'profile_pic_img_url','price', 'description')
		event_df = pd.DataFrame.from_records(event)
		event_slots_df = pd.DataFrame.from_records(event_slots.values('start_time','end_time','event_id'))
		if not event_slots_df.empty:
			event_slots_df = event_slots_df.groupby(by=["event_id"]).agg({'start_time': 'min', 'end_time': 'max'})[['start_time','end_time']].reset_index()
			event_slots_df['start_time'] = event_slots_df['start_time'].dt.date
			event_slots_df['end_time'] = event_slots_df['end_time'].dt.date
			final_df = pd.merge(event_df, event_slots_df, left_on='id', right_on='event_id')
			final_df.drop(['event_id'], axis=1, inplace=True)

			result = final_df.to_dict('records')
			if result:
				[value.update({"slots":[{"start_time": value['start_time'], "end_time": value['end_time']}]}) for value in result]
			for value in result:
				value.pop('start_time',None)
				value.pop('end_time',None)
			if result:
				result = result[0]
		return JsonResponse({'message': 'success', 'data':  result}, status=status.HTTP_200_OK)

	def get_event_list(self, page_no):
		events = Event.objects.filter(is_approved=True, is_active = True).values('id', 'title', 'thumbnail_img_url', 'banner_img_url', 'profile_pic_img_url','price', 'description', 'creator_id')
		events_df = pd.DataFrame.from_records(events)
		result = []
		if not events_df.empty:
			events_df['followers_count'] = events_df['creator_id'].apply(lambda user_id: get_userprofile_counter(user_id)['follower_count'])
			event_slots_df = pd.DataFrame.from_records(EventSlot.objects.all().values('start_time','end_time','event_id','state'))
			events_df = events_df.sort_values(by=['followers_count'], ascending=False)
			if not event_slots_df.empty:
				#fetch available slots event only
				available_slots_event_df = event_slots_df[(event_slots_df['end_time']>=datetime.now()) & (event_slots_df['state']=="available")]
				available_events_ids = []
				if not available_slots_event_df.empty:
					available_events_ids = available_slots_event_df['event_id'].unique()
				event_slots_df = event_slots_df.groupby(by=["event_id"]).agg({'start_time': 'min', 'end_time': 'max'})[['start_time','end_time']].reset_index()
				event_slots_df = event_slots_df[(event_slots_df['end_time']>=datetime.now()) & (event_slots_df['event_id'].isin(available_events_ids))]
				event_slots_df['start_time'] = event_slots_df['start_time'].dt.date
				event_slots_df['end_time'] = event_slots_df['end_time'].dt.date
				final_df = pd.merge(events_df, event_slots_df, left_on='id', right_on='event_id')
				final_df.drop(['event_id'], axis=1, inplace=True)
				result = final_df.to_dict('records')
				if result:
					[value.update({"slots":[{"start_time": value['start_time'], "end_time": value['end_time']}]}) for value in result]
				for value in result:
					value.pop('start_time',None)
					value.pop('end_time',None)
		paginator = Paginator(result, settings.GET_BOOKINGS_API_PAGE_SIZE)
		try:
			result = paginator.page(page_no).object_list
		except:
			result = []
		return JsonResponse({'message': 'success', 'data':  result}, status=status.HTTP_200_OK)

	def download_and_upload_events(self, event_id, promo_profile_pic, promo_banner):
		try:
			from jarvis.views import urlify
			#upload images async
			promo_profile_pic_path, promo_profile_pic_name, banner_file_path, promo_banner_name = None, None, None, None
			if promo_profile_pic:
				ts1 = time.time()
				promo_profile_pic_name_temp= promo_profile_pic.name.split('.')
				promo_profile_pic_name = str(urlify(promo_profile_pic_name_temp[0]))+"_"+ str(ts1).replace(".", "")+"."+str(promo_profile_pic_name_temp[1])
				promo_profile_pic_path = '/tmp/'+promo_profile_pic_name
				with open(promo_profile_pic_path,'wb') as f:
					for chunk in promo_profile_pic.chunks():
						if chunk:
							f.write(chunk)
			if promo_banner:
				ts2 = time.time()
				promo_banner_temp= promo_banner.name.split('.')
				promo_banner_name = str(urlify(promo_banner_temp[0]))+"_"+ str(ts2).replace(".", "")+"."+str(promo_banner_temp[1])
				banner_file_path = '/tmp/'+promo_banner_name
				with open(banner_file_path,'wb') as f:
					for chunk in promo_banner.chunks():
						if chunk:
							f.write(chunk)
			upload_event_media.delay(event_id, promo_profile_pic_path, banner_file_path, promo_profile_pic_name, promo_banner_name)
		except Exception as e:
			print(e)

class EventSlotsDetails(APIView):
	def get(self, request, *args, **kwargs):
		try:
			if request.user.is_authenticated:
				page_no = request.GET.get('page',1)
				event_id = request.GET.get('event_id',None)
				if event_id:
					return self.get_event_slots(event_id, page_no)
				else:
					return self.get_creator_slots(request.user.id, page_no)
			else:
				return JsonResponse({'message':'Unauthorised User'}, status=status.HTTP_401_UNAUTHORIZED)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

	def get_event_slots(self, event_id, page_no):
		available_event_slots = list(EventSlot.objects.filter(event_id=event_id, state="available", end_time__gt=datetime.now()).order_by('start_time').values('start_time', 'end_time', 'channel_id','id'))
		try:
			result = get_slots_date_and_time_payload(available_event_slots, page_no)
		except:
			result = []
		return JsonResponse({'message': 'success', 'data': result}, status=status.HTTP_200_OK)

	def get_creator_slots(self, user_id, page_no):
		event_ids = Event.objects.filter(creator_id=user_id).values('id')
		event_slots = EventSlot.objects.filter(event_id__in=event_ids).values('start_time','end_time','channel_id','id')
		event_slots_df = pd.DataFrame.from_records(event_slots)
		result = []
		if not event_slots_df.empty:
			event_booked_slots = EventBooking.objects.filter(event_slot_id__in=event_slots_df['id'].unique(),state="booked",payment_status="success").values('event_slot_id', 'user_id')
			event_booked_slots_df = pd.DataFrame.from_records(event_booked_slots)
			final_df = event_slots_df
			if not event_booked_slots_df.empty:
				final_df = pd.merge(event_slots_df, event_booked_slots_df,left_on='id',right_on='event_slot_id')
				final_df = update_event_slot_status(final_df)
				if not final_df.empty:
					users = User.objects.filter(id__in=final_df['user_id'].unique()).values('username','id')
					user_df = pd.DataFrame.from_records(users)
					final_df = pd.merge(final_df,user_df,left_on='user_id',right_on='id')
					final_df = final_df.rename(columns={'username': 'booked_by', 'id_x': 'slot_id'})
					final_df.drop(['event_slot_id', 'id_y', 'user_id'], axis=1,inplace=True)
					final_df = final_df.replace({"event_status": booking_options})
					final_df['channel_url'] = settings.BOOKING_SLOT_URL+final_df['channel_id']
					result = final_df.to_dict('records')
					paginator = Paginator(result, settings.GET_BOOKINGS_API_PAGE_SIZE)
					try:
						result = paginator.page(page_no).object_list
					except:
						result = []
		return JsonResponse({'message': 'success', 'data':  result}, status=status.HTTP_200_OK)

def get_slots_date_and_time_payload(booking_slots,page_no):
		start_index = (int(page_no)-1)*settings.GET_EVENT_SLOT_API_PAGE_SIZE
		end_index = start_index + settings.GET_EVENT_SLOT_API_PAGE_SIZE - 1
		booking_slots_df = pd.DataFrame.from_records(booking_slots)
		slots = []
		if not booking_slots_df.empty:
			booking_slots_df['date'] = booking_slots_df['start_time'].dt.date
			unique_dates = booking_slots_df['date'].unique()
			booking_slots_df['start_time'] = booking_slots_df['start_time'].dt.strftime('%H:%M:%S').astype(str)
			booking_slots_df['end_time'] = booking_slots_df['end_time'].dt.strftime('%H:%M:%S').astype(str)
			booking_slots_df['channel_url'] = settings.BOOKING_SLOT_URL+booking_slots_df['channel_id']
		booking_slots_df_group = booking_slots_df.groupby('date')
		for date in unique_dates[start_index:end_index+1]:
			new_slots = {}
			new_slots['time'] = booking_slots_df_group.get_group(date).to_dict('records')
			new_slots['date'] = date
			slots.append(new_slots)
		return slots


class BookingPaymentRedirectView(RedirectView):

	def get_redirect_url(self, *args, **kawrgs):
		print "request data", self.request.resolver_match.kwargs
		booking_id = self.request.resolver_match.kwargs.get('booking_id')
		booking = EventBooking.objects.select_related('event').get(id=booking_id)

		if booking.state=="cancelled" and booking.payment_status=="failed":
			return '/payment/payment_failed'

		booking.payment_status = 'initiated'
		booking.event_slot.state = 'hold'
		booking.event_slot.save()

		if not booking.payment_gateway_order_id:
			order = create_order(booking.event.price, "INR", receipt=booking.booking_number, notes={})
			booking.payment_gateway_order_id = order.get('id')

		booking.save()
		return '/payment/razorpay/%s/pay?type=booking&booking_id=%s'%(booking.payment_gateway_order_id,booking.id)

		
class EventBookingDetails(APIView):
	def get(self, request, *args, **kwargs):
		try:
			if request.user.is_authenticated:
				page_no = request.GET.get('page',1)
				event_bookings = list(EventBooking.objects.filter(user_id=request.user.id).values('event_id', 'event_slot_id','payment_status','state', 'id'))
				event_booking_ids = [value['event_id'] for value in event_bookings]
				user_booking_slot_ids = [value['event_slot_id'] for value in event_bookings]
				events = Event.objects.filter(id__in=event_booking_ids).values('id','title','thumbnail_img_url')
				event_slots = EventSlot.objects.filter(id__in=user_booking_slot_ids).values('start_time','end_time', 'id','event_id','channel_id','state')

				result = []
				if event_bookings:
					events_df = pd.DataFrame.from_records(events)
					event_slot_df = pd.DataFrame.from_records(event_slots)#.drop(['id'], axis=1)
					event_booking_df = pd.DataFrame.from_records(event_bookings)
					event_bookings_merged_df = pd.merge(event_booking_df,events_df,left_on="event_id",right_on="id",how="left")
					event_bookings_merged_df = event_bookings_merged_df.drop(['id_y'], axis=1)
					final_df = pd.merge(event_bookings_merged_df, event_slot_df, left_on="event_slot_id", right_on="id",how="left")
					final_df = update_event_slot_status(final_df)
					final_df.drop(['event_id_y','id'], axis=1, inplace=True)
					final_df['channel_url'] = settings.BOOKING_SLOT_URL+final_df['channel_id']
					final_df = final_df.replace({"event_status": booking_options})
					final_df = final_df.rename(columns={'state_x': 'event_booking_status', 'state_y': 'event_slot_status', 'event_status': 'session_state', 'id_x': 'id', 'event_id_x':'event_id'})
					result = final_df.to_dict('records')
					paginator = Paginator(result, settings.GET_BOOKINGS_API_PAGE_SIZE)
					try:
						result = paginator.page(page_no).object_list
					except:
						result = []
				return JsonResponse({'message': 'success', 'data':  result}, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
	def post(self, request, *args, **kwargs):
		try:
			if request.user.is_authenticated:
				event_slot_id = request.POST.get('event_slot_id', None)
				name = request.POST.get('name',None)
				if name:
					UserProfile.objects.filter(user_id=request.user.id).update(name=name)
				event_slot = list(EventSlot.objects.filter(pk=event_slot_id).values('start_time', 'end_time', 'event_id','channel_id'))
				if event_slot:
					event_id = event_slot[0]['event_id']
					already_booked = EventBooking.objects.filter(user_id=request.user.id, event_slot_id=event_slot_id, state="booked",payment_status="success")
					if not already_booked:
						event_booking = EventBooking(user_id=request.user.id, event_id=event_id, event_slot_id=event_slot_id)
						event_booking.save()
						event_count = EventBooking.objects.filter(event_id=event_id).count()
						result = {}
						result['message'] = 'You have successfully booked this session'
						event_slot[0]['channel_url'] = settings.BOOKING_SLOT_URL+event_slot[0]['channel_id']
						result['data'] = event_slot[0]
						result['data']['id'] = event_booking.id
						result['count'] = event_count
						return JsonResponse(result, status=status.HTTP_200_OK)
					else:
						return JsonResponse({'message': "Already Booked",'data':{}}, status=status.HTTP_200_OK)
				else:
					return JsonResponse({'message': "Invalid Slot Id",'data':{}}, status=status.HTTP_400_BAD_REQUEST)
			else:
				return JsonResponse({'message':'Unauthorised User', 'data':{}}, status=status.HTTP_401_UNAUTHORIZED)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)



def update_event_slot_status(slots_df):
	slots_df['event_status'] = np.where((slots_df['start_time']<=datetime.now())&(slots_df['end_time']>=datetime.now()), '1', '0')
	slots_df['event_status'] = np.where(slots_df['end_time']<datetime.now(), '2', slots_df.event_status)
	return slots_df