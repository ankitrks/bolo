from forum.user.models import UserProfile, ReferralCode, ReferralCodeUsed, AndroidLogs,VideoPlaytime
from jarvis.models import FCMDevice
from forum.topic.models import VBseen
from django.db.models import Sum
from drf_spirit.utils import short_time
from datetime import datetime

def run():
    all_user_profile = UserProfile.objects.filter(is_test_user=False).order_by('id')
    all_profile_count = len(all_user_profile)
    counter = 1
    csv=''
    csv+='Username,Name,Install date,Signup Date,City and State,Language,Currently Active?,Last Active,Watch Time, Play Time,\n'
    for each_user_profile in all_user_profile:
        try:
            print "###############   ",counter," / ",all_profile_count,"   ################"
            counter+=1
            username = each_user_profile.user.username
            name = each_user_profile.name
            all_referal_code = ReferralCodeUsed.objects.filter(by_user = each_user_profile.user).order_by('id')
            install_date = False
            if all_referal_code:
                install_date_obj = all_referal_code[0]
                install_date = str(install_date_obj.created_at.date())
                if install_date_obj.android_id:
                    signed_up= ReferralCodeUsed.objects.filter(android_id=install_date_obj.android_id,by_user__isnull=True).order_by('id')
                    if signed_up:
                        signed_up_date = str(signed_up[0].created_at.date())
                    else:
                        signed_up_date = str(signup_obj.created_at.date())
                else:
                    signed_up_date = install_date
            else:
                signed_up_date = str(each_user_profile.user.date_joined.date())
                install_date = str(each_user_profile.user.date_joined.date())
            city = str(each_user_profile.city_name).encode('utf-8') +" - "+str(each_user_profile.state_name).encode('utf-8')
            language = each_user_profile.get_language_display()
            active = FCMDevice.objects.filter(user=each_user_profile.user).order_by('-id')
            if active and active[0].is_uninstalled:
                active_status = 'No'
            else:
                active_status = 'Yes'
            vb_seen = VBseen.objects.filter(user=each_user_profile.user).order_by('-id')
            if vb_seen:
                last_active = str(vb_seen[0].created_at.date())
            else:
                all_logs = AndroidLogs.objects.filter(user = each_user_profile.user).order_by('-id')
                if all_logs:
                    last_active = str(all_logs[0].created_at.date())
                else:
                    last_active =str(each_user_profile.user.date_joined.date())
            watch_time = VideoPlaytime.objects.filter(user = each_user_profile.user.id).aggregate(Sum('playtime'))
            if watch_time.has_key('playtime__sum') and watch_time['playtime__sum']:
                print 'vb_playtime:',watch_time['playtime__sum']
                watch_time = short_time(watch_time['playtime__sum'])
            else:
                watch_time = short_time(0)
            playtime = short_time(each_user_profile.total_vb_playtime)
            try:
                print username+','+name+','+install_date+','+signed_up_date+','+city+','+language+','+active_status+','+last_active+','+watch_time+','+playtime+',\n'
                csv+=username+','+name+','+install_date+','+signed_up_date+','+city+','+language+','+active_status+','+last_active+','+watch_time+','+playtime+',\n'
            except Exception as e:
                print e
        except Exception as e:
            print e

    file = open("user_signed_up_data_"+str(datetime.now().date())+".csv","w")
    file.write(csv.encode('utf-8'))
    file.close()

    all_device = FCMDevice.objects.filter(user__isnull=True).distinct('dev_id')
    device_count = len(all_device)
    device_counter = 1
    second_csv='Install Date,Still Install, Uninstall Date,\n'
    for each_device in all_device:
        try:
            print "###############   ",device_counter," / ",device_count,"   ################"
            device_counter+=1
            one_device = FCMDevice.objects.filter(user__isnull=True,dev_id=each_device.dev_id).order_by('-id')
            if one_device and one_device[0].is_uninstalled:
                status= 'No'
            else:
                status = 'Yes'
            if status == 'No':
                uninstall_date = str(one_device[0].uninstalled_date.date())
            else:
                uninstall_date = 'None'
            print str(each_device.created_at.date())+','+status+','+str(uninstall_date)+',\n'
            second_csv+=str(each_device.created_at.date())+','+status+','+str(uninstall_date)+',\n'
        except Exception as e:
            print e
    file = open("user_installed_data_"+str(datetime.now().date())+".csv","w")
    file.write(second_csv.encode('utf-8'))
    file.close()


