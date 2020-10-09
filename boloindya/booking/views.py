# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import F

from rest_framework import status
from rest_framework.views import APIView

from .serializers import BookingSerializer
from .models import Booking, UserBooking, BookingSlot
from .utils import booking_options
# Create your views here.
import pandas as pd
import numpy as np

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
				booking_slot = list(BookingSlot.objects.filter(pk=booking_slot_id).values('start_time', 'id', 'end_time', 'booking_id'))
				if booking_slot:
					booking_id = booking_slot[0]['booking_id']
					UserBooking(user_id=request.user.id, booking_id=booking_id, booking_slot_id=booking_slot_id).save()
					Booking.objects.filter(id=booking_id).update(available_slots= F('available_slots')-1)
					booking_count = UserBooking.objects.filter(booking_id=booking_id).count()
					result = {}
					result['message'] = 'You have successfully booked this session'
					result['booked_slot'] = booking_slot[0]
					result['count'] = booking_count
					return JsonResponse(result, status=status.HTTP_200_OK)
				else:
					return JsonResponse({'message': "Invalid Slot Id",'data':[]}, status=status.HTTP_400_BAD_REQUEST)
			else:
				return JsonResponse({'message':'Unauthorised User', 'data':[]}, status=status.HTTP_401_UNAUTHORIZED)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)

	def get_booking_detail(self, booking_id, user_id):
		try:
			booking = Booking.objects.get(id=booking_id)
			booking_details = BookingSerializer(booking).data
			booking_details['is_slot_available'] = True if  booking_details['available_slots'] > 0 else False
			user_booking = list(UserBooking.objects.filter(user_id=user_id, booking_id=booking_details['id']).values_list('booking_slot_id', flat=True))
			
			booking_slots = list(BookingSlot.objects.filter(booking_id=booking_details['id']).values('id', 'start_time', 'end_time'))
			booking_details['is_booked'] = False
			booking_details['slots'] = booking_slots
			booking_details['booked_slot'] = None
			if user_booking:
				booking_details['is_booked'] = True
				booked_slot = [booking_slots.pop(index) for index,value in enumerate(booking_slots) if value['id'] in user_booking]
				booking_details['slots'] = booking_slots#[value['start_time'] for value in booking_slots]
				if booked_slot:
					booking_details['booked_slot'] = booked_slot[0]

			return JsonResponse({'message': 'success', 'data':  booking_details}, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)

	def get_booking_list(self, user_id, page_no):
		try:
			bookings = Booking.objects.all().values('id', 'creator_id', 'title', 'thumbnail_img_url','available_slots')
			user_bookings = UserBooking.objects.filter(user_id=user_id).values('booking_id')
			bookings_df = pd.DataFrame.from_records(bookings)
			user_bookings_df = pd.DataFrame.from_records(user_bookings)
			if not bookings_df.empty:
				bookings_df['is_slot_available'] = np.where(bookings_df['available_slots']>0,True, False)
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


class UserBookingList(APIView):
	def get(self, request, *args, **kwargs):
		try:
			if request.user.is_authenticated:
				page_no = request.GET.get('page',1)
				user_bookings = list(UserBooking.objects.filter(user_id=request.user.id).values('booking_id', 'booking_slot_id', 'booking_status'))
				user_booking_ids = [value['booking_id'] for value in user_bookings]
				user_booking_slot_ids = [value['booking_slot_id'] for value in user_bookings]
				bookings = Booking.objects.filter(id__in=user_booking_ids).values('id','title','thumbnail_img_url')
				booking_slots = BookingSlot.objects.filter(id__in=user_booking_slot_ids).values('start_time','end_time', 'id','booking_id')

				result = []
				if user_bookings:
					bookings_df = pd.DataFrame.from_records(bookings)
					booking_slot_df = pd.DataFrame.from_records(booking_slots).drop(['id'], axis=1)
					user_booking_df = pd.DataFrame.from_records(user_bookings)

					final_df = pd.merge(pd.merge(bookings_df,booking_slot_df,left_on='id',right_on='booking_id'),user_booking_df,on='booking_id')
					final_df.drop(['booking_id'], axis=1, inplace=True)
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