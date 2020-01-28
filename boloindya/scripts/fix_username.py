# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
import re
import random, string
from datetime import datetime


def run():
    user_name_fixed = 0
    slug_fixed = 0
    mobile_no_fixed = 0
    invalid_number = 0
    non_indian_number = 0
    for each_user in User.objects.all():
        if not check_username_valid(each_user.username):
            old_username = each_user.username
            new_username = validate_username(each_user.username)
            print "username not valid: ",old_username,new_username
            # each_user.username = new_username
            # each_user.save()

        try:
            if not each_user.username.lower() == each_user.username:
                user = User.objects.filter(username = each_user.username.lower()).exclude(pk__in=[each_user.id])
                if user:
                    old_username = each_user.username
                    new_username = change_username(old_username)
                    print "same_username_exist: ",old_username,new_username
                    each_user.username = new_username
                    # each_user.save()
                    userprofile = each_user.st
                    userprofile.slug = new_username
                    # userprofile.save()
                else:
                    old_username = each_user.username
                    new_username = old_username.lower()
                    print "capital_username exist: ".old_username,new_username
                    each_user.username = new_username
                    # each_user.save()
                    userprofile = each_user.st
                    userprofile.slug = new_username
                    # userprofile.save()
                user_name_fixed+=1
            elif not each_user.username == each_user.st.slug:
                old_slug = each_user.st.slug
                new_slug = each_user.username
                print "diffrent slug exist",old_slug,new_slug
                userprofile = each_user.st
                userprofile.slug = each_user.username
                # userprofile.save()
                slug_fixed+=1
            if each_user.st and each_user.st.mobile_no:
                if not check_mobile_valid(each_user.st.mobile_no):
                    invalid_number+=1
                    print "Invalid mobile no ",each_user.st.mobile_no
                else:
                    userprofile = each_user.st
                    length_of_mobile_no = len(userprofile.mobile_no)
                    if length_of_mobile_no>10 and length_of_mobile_no<=13:
                        old_mobile_no = userprofile.mobile_no
                        new_mobile_no = old_mobile_no[-10:]
                        print old_mobile_no,new_mobile_no
                        mobile_no_fixed+=1
                    elif length_of_mobile_no>13:
                        non_indian_number+=1
                        print "non indain number: ",userprofile.mobile_no
        except Exception as e:
            print e
    print "user_name_fixed: ",user_name_fixed
    print 'slug_fixed: ', slug_fixed
    print 'mobile_no_fixed:',mobile_no_fixed
    print 'invalid_number: ', invalid_number
    print 'non_indian_number: ', non_indian_number

def check_username_valid(username):
    if re.match(r"^[A-Za-z0-9_.-]+$", username):
        return True
    else:
        return False

def check_mobile_valid(mobile_no):
    if re.match(r"^[0-9+]+$", mobile_no):
        return True
    else:
        return False

def validate_username(username):
    return re.sub('[^A-Za-z0-9_.-]+', '_', username)

 
def change_username(old_username,i=0):
    if not i:
        new_username = old_username.lower()+str(1)
    else:
        new_username = old_username.lower()+str(i+1)
    try:
        user = User.objects.get(username=new_username)
        print "i am found"
        new_username = change_username(old_username,i+1)
    except:
        return new_username
    return new_username

def get_random_username():
    today_datetime = datetime.now()
    year = str(today_datetime.year%100)
    month = today_datetime.month
    if month <10:
        month = '0'+str(month)
    else:
        month = str(month)
    x = 'bi'+year+month+''.join(random.choice(string.digits) for _ in range(5))
    x = x.lower()
    # x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    try:
        user = User.objects.get(username=x)
        get_random_username()
    except:
        return x


