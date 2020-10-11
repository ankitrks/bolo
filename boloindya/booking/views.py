# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView

from .serializers import BookingSerializer
from .models import Booking, UserBooking, BookingSlot
from .utils import booking_options
# Create your views here.
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class BookingDetails(APIView):
	def get(self, request, *args, **kwargs):
		try:
			if request.user.is_authenticated and str(request.user.id) in settings.ALLOW_BOOKINGS_FOR:
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
			if request.user.is_authenticated and str(request.user.id) in settings.ALLOW_BOOKINGS_FOR:
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
			booking_slots = list(BookingSlot.objects.filter(booking_id=booking_details['id'],end_time__gt=datetime.now()).exclude(id__in=already_booked_ids).values('id', 'start_time', 'end_time', 'channel_id'))
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
			if request.user.is_authenticated and str(request.user.id) in settings.ALLOW_BOOKINGS_FOR:
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
