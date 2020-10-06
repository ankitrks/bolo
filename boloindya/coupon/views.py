# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import F

from rest_framework.decorators import api_view
from rest_framework import status, generics

from .models import Coupon, UserCoupon
from forum.user.models import UserProfile
from drf_spirit.utils import shorcountertopic

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import requests
import json
import pytz
from .models import Coupon, UserCoupon

# Create your views here.
@api_view(['GET','POST'])
def get_coupons(request):
    try:
        if request.user.is_authenticated:
            user_id = request.user.id
            user_coins = request.user.st.bolo_score
            #get request
            if request.method == 'GET':
                page_no = request.GET.get('page',1)
                #todo get user current timezone
                timezone = pytz.timezone('Asia/Calcutta')
                today = datetime.now(timezone).date()
                all_coupons = Coupon.objects.filter(is_active=True, is_draft=False).order_by('coins_required')
                exclude_ids = list(UserCoupon.objects.filter(user_id=user_id).values_list('coupon_id',flat=True))
                df1 = pd.DataFrame.from_records(all_coupons.values('id', 'active_banner_img_url', 'inactive_banner_img_url','brand_name','coins_required','coupon_code','discount_given','active_till','active_from'))
                result = []
                if not df1.empty:
                    df1['is_active'] = np.where(df1['coins_required']>user_coins, False, True)
                    df1['coupon_code'] = np.where(df1['id'].isin(exclude_ids), df1['coupon_code'],'')
                    df1['is_used'] = np.where(df1['id'].isin(exclude_ids), True, False)
                    df1['active_till'] = df1['active_till'].dt.date
                    df1['active_from'] = df1['active_from'].dt.date
                    df1 = df1[(df1['active_from']<=today) & (df1['active_till']>=today)]
                    result = df1.to_dict('records')
                    paginator = Paginator(result, settings.GET_COUPONS_API_PAGE_SIZE)
                    try:
                        result = paginator.page(page_no).object_list
                    except:
                        result = []
                return JsonResponse({'message': 'success', 'user_coins': user_coins, 'video_url': settings.ANIMATED_VIDEO_URL, 'user_coins_formatted': shorcountertopic(user_coins),'data':  result}, status=status.HTTP_200_OK)
            #post request
            elif request.method == 'POST':
                coupon_id = request.POST.get('coupon_id',None)
                if coupon_id:
                    coupon_obj = Coupon.objects.get(id=coupon_id, is_active=True, is_draft=False)
                    user_coupon_history = list(UserCoupon.objects.filter(coupon=coupon_obj, user_id=user_id).values_list('coupon_id', flat=True))
                    if coupon_obj.coins_required<=user_coins and coupon_obj.id not in user_coupon_history:
                        #update user coins
                        updated_user_details = reduce_user_bolo_score(request.user.id, coupon_obj.coins_required)
                        if 'bolo_score' in updated_user_details['result']:
                            UserCoupon(user_id=user_id, coupon=coupon_obj).save()
                            updated_user_coins = updated_user_details['result']['bolo_score']
                            result = {"coupon_code": coupon_obj.coupon_code,"user_coins": updated_user_coins, "user_coins_formatted": shorcountertopic(updated_user_coins)}
                            return JsonResponse({'status': 'success', 'data':  result}, status=status.HTTP_200_OK)
                        else:
                            return JsonResponse({'message':'Service temporarily unavailable, try again later.', 'data':[]}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    else:
                        return JsonResponse({'message': "You cannot redeemed this coupon as you don't have enough coins or you have already redeemed", 'data':[]}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return JsonResponse({'message':"Coupon id is required", 'data':[]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'message':'Service temporarily unavailable, try again later.', 'data':[]}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        print(e)
        return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)


def reduce_user_bolo_score(user_id, score):
    try:
        userprofile = UserProfile.objects.filter(user_id = user_id)
        updated_score = userprofile[0].bolo_score - int(score)
        if updated_score>=0 and score:
            userprofile.update(bolo_score= F('bolo_score')-int(score))
            result = {'user_id': user_id, 'bolo_score': updated_score}
            return {'message':'success', 'result': result}
        else:
            return {'message': 'Cannor update score', 'result': {}}
    except Exception as e:
        print(e)
        return {'message': 'Something went wrong! Please try again later.','error':str(e), 'result': {}}

@api_view(['GET'])
def get_user_coupons(request):
    try:
        if request.user.is_authenticated:
            page_no = request.GET.get('page',1)
            user_coupons = UserCoupon.objects.filter(user=request.user)
            all_coupons = Coupon.objects.all()
            df2 = pd.DataFrame.from_records(user_coupons.values('coupon_id'))
            df1 = pd.DataFrame.from_records(all_coupons.values('id','brand_name','coupon_code','discount_given','active_till'))
            timezone = pytz.timezone('Asia/Calcutta')
            today = datetime.now(timezone).date()
            df1['active_till'] = df1['active_till'].dt.date
            df1['is_expired'] = np.where(df1['active_till']<today, True, False)
            final_df=pd.merge(df1,df2, how='inner',left_on=['id'],right_on=['coupon_id'])
            result = final_df.to_dict('records')
            paginator = Paginator(result, settings.GET_USER_COUPONS_API_PAGE_SIZE)
            try:
                result = paginator.page(page_no).object_list
            except:
                result = []
            return JsonResponse({'message': 'success', 'page_size': settings.GET_USER_COUPONS_API_PAGE_SIZE,'data':  result}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message':'Unauthorised User', 'data':[]}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return JsonResponse({'message': str(e),'data':[]}, status=status.HTTP_400_BAD_REQUEST)