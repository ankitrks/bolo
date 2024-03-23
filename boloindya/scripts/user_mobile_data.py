from forum.user.models import AndroidLogs, ReferralCodeUsed, UserProfile
from drf_spirit.models import UserJarvisDump
import csv
def run():
    profile=UserProfile.objects.filter(is_test_user=False, mobile_no__isnull=False)
    user_dict = {}
    i = 0
    for each in profile:
        print('=====' + str(i) + ' / ' + str(profile.count()) +'=====')
        i += 1
        if each.user.st_topics.all().count() > 0:
            user_dict[each.user.username] = {'mobile_no': each.mobile_no, 'User Type': 'Creator'}
        else:
            user_dict[each.user.username] = {'mobile_no': each.mobile_no, 'User Type': 'Consumer'}
    from datetime import datetime
    i = 0
    with open('user_mobile_data.csv', 'w') as file:
        filewriter = csv.writer(file)
        filewriter.writerow(['Username', 'Mobile No', 'User Type', 'Active Days Ago'])
        for each in profile:
            print('=====' + str(i) + ' / ' + str(profile.count()) + '=====')
            i += 1
            log = AndroidLogs.objects.filter(user=each.user).order_by('-created_at').first()
            user_log = UserJarvisDump.objects.filter(user=each.user).order_by('-sync_time').first()
            if log and user_log:
                log_diff = (datetime.now()-log.created_at).days
                dump_diff = (datetime.now()-user_log.sync_time).days
                if log_diff < dump_diff:
                    filewriter.writerow([each.user.username, user_dict[each.user.username]['mobile_no'], user_dict[each.user.username]['User Type'], log_diff])
                else:
                    filewriter.writerow([each.user.username, user_dict[each.user.username]['mobile_no'], user_dict[each.user.username]['User Type'], dump_diff])
            elif log:
                log_diff = (datetime.now()-log.created_at).days
                filewriter.writerow([each.user.username, user_dict[each.user.username]['mobile_no'], user_dict[each.user.username]['User Type'], log_diff])
            elif user_log:
                dump_diff = (datetime.now()-user_log.sync_time).days
                filewriter.writerow([each.user.username, user_dict[each.user.username]['mobile_no'], user_dict[each.user.username]['User Type'], dump_diff])
            else:
                refer=ReferralCodeUsed.objects.filter(by_user=each.user).order_by('-created_at').first()
                if refer:
                    filewriter.writerow([each.user.username, user_dict[each.user.username]['mobile_no'], user_dict[each.user.username]['User Type'], (datetime.now()-refer.created_at).days])
                else:
                    filewriter.writerow([each.user.username, user_dict[each.user.username]['mobile_no'], user_dict[each.user.username]['User Type'], -1])
