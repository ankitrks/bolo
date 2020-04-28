# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from forum.user.models import UserProfile
from forum.comment.models import Comment
import re
import random, string
from datetime import datetime
from django.db.models import Q


def run():
    user_name_fixed = 0
    slug_fixed = 0
    mobile_no_fixed = 0
    invalid_number = 0
    non_indian_number = 0
    try:

        ## this loop will check if the username is valid or not and change to valid by removing unneccsry character with _
        total_user = User.objects.all().count()
        validation_counter=1
        for each_user in User.objects.all():
            print "Username Validation: ###########     ",validation_counter,"/",total_user,"        ################"
            validation_counter+=1
            try:
                user_update_obj = User.objects.filter(pk=each_user.id)
                print check_username_valid(each_user.username),each_user.username
                if not check_username_valid(each_user.username):
                    old_username = each_user.username
                    new_username = change_username(validate_username(each_user.username))
                    print "username not valid: ",old_username,new_username
                    if not old_username == new_username:
                        user_update_obj.update(username = new_username)
                        check_comment_mention(old_username,new_username)
            except Exception as e:
                print e
        ## this loop will check for capital username and if already lower then validate them by removing unnecry character with _
        lower_counter = 1
        for each_user in User.objects.all():
            print "username lower: ###########     ",lower_counter,"/",total_user,"        ################"
            lower_counter+=1
            try:
                user_update_obj = User.objects.filter(pk=each_user.id)
                if not each_user.username.lower() == each_user.username:
                    user = User.objects.filter(username = each_user.username.lower()).exclude(pk__in=[each_user.id])
                    if user:
                        old_username = each_user.username
                        new_username = change_username(old_username)
                        print "same_username_exist: ",old_username,new_username
                        if not old_username == new_username:
                            user_update_obj.update(username = new_username)
                            check_comment_mention(old_username,new_username)
                    else:
                        old_username = each_user.username
                        new_username = old_username.lower()
                        print "capital_username exist: ",old_username,new_username
                        if not old_username == new_username:
                            user_update_obj.update(username = new_username)
                            check_comment_mention(old_username,new_username)
                    user_name_fixed+=1
                else:
                    if not check_username_valid(each_user.username) and not check_mobile_valid(each_user.username):
                        old_username = each_user.username
                        new_username = change_username(validate_username(each_user.username))
                        print "lower fix: ",old_username,new_username
                        if not old_username == new_username:
                            user_update_obj.update(username = new_username)
                            check_comment_mention(old_username,new_username)
                            user_name_fixed+=1

            except Exception as e:
                print e

        ## this loop will check if username contains mobile no if mobile no replaced with name or random string
        mobile_counter=1
        for each_user in User.objects.all():
            print "username mobile remove : ###########     ",mobile_counter,"/",total_user,"        ################"
            mobile_counter+=1
            try:
                user_update_obj = User.objects.filter(pk=each_user.id)
                if check_mobile_valid(each_user.username):
                    print each_user.username
                    if is_valid_indian_number(each_user.username):
                        if each_user.st.name:
                            old_username = each_user.username
                            new_username = change_username(validate_username(each_user.st.name))
                            print "mobile found in username", each_user.st.name,old_username,new_username
                            if not old_username == new_username:
                                user_update_obj.update(username = new_username)
                                check_comment_mention(old_username,new_username)
                        else:
                            new_username = get_random_username()
                            old_username = each_user.username
                            print "mobile found in username", each_user.st.name,old_username,new_username
                            if not old_username == new_username:
                                user_update_obj.update(username = new_username)
                                check_comment_mention(old_username,new_username)
                    else:
                        print " not indian mobile no"
                else:
                    print "not mobile_no"

            except Exception as e:
                print e

        ## this will remove multiple underscore
        underscore_counter = 1
        for each_user in User.objects.all():
            print "underscore remove : ###########     ",underscore_counter,"/",total_user,"        ################"
            underscore_counter+=1
            try:
                user_update_obj = User.objects.filter(pk=each_user.id)
                if each_user.username.startswith('_') or each_user.username.endswith('_'):
                    old_username = each_user.username
                    new_username = change_username(remove_underscore(each_user.username))
                    print "remove_underscore:   ", each_user.username, new_username
                    if not old_username == new_username:
                        user_update_obj.update(username = new_username)
                        check_comment_mention(old_username,new_username)
            except Exception as e:
                print e

        ## this will fix the slug
        slug_counter=1
        for each_user in User.objects.all():
            print "slug fix : ###########     ",slug_counter,"/",total_user,"        ################"
            slug_counter+=1
            try:
                userprofile_update_obj = UserProfile.objects.filter(user_id=each_user.id)
                if not each_user.username == each_user.st.slug:
                    old_slug = each_user.st.slug
                    new_slug = each_user.username
                    print "diffrent slug exist",old_slug,new_slug
                    userprofile = each_user.st
                    userprofile_update_obj.update(slug = each_user.username)
                    slug_fixed+=1
            except Exception as e:
                print e

        ## this will fix the indian mobile no left other no
        validate_mobile_counter = 1
        for each_user in User.objects.all():
            print "mobile_validation : ###########     ",validate_mobile_counter,"/",total_user,"        ################"
            validate_mobile_counter+=1
            try:
                userprofile_update_obj = UserProfile.objects.filter(user_id=each_user.id)
                if each_user.st and each_user.st.mobile_no:
                    if not check_mobile_valid(each_user.st.mobile_no):
                        invalid_number+=1
                        print "Invalid mobile no ",each_user.st.mobile_no
                    else:
                        userprofile = each_user.st
                        length_of_mobile_no = len(userprofile.mobile_no)
                        if length_of_mobile_no<8:
                            print userprofile.mobile_no
                            print "Invalid number cant change"
                        elif length_of_mobile_no>8 and length_of_mobile_no<=14:
                            old_mobile_no = userprofile.mobile_no
                            new_mobile_no = validate_indian_number(old_mobile_no,each_user.id)
                            #print "new mobile_no ",old_mobile_no,new_mobile_no
                            if not old_mobile_no == new_mobile_no:
                                userprofile_update_obj.update(mobile_no = new_mobile_no)
                                mobile_no_fixed+=1
                        elif length_of_mobile_no>14:
                            non_indian_number+=1
                            print "non indain number: ",userprofile.mobile_no
            except Exception as e:
                print e
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

def validate_indian_number(mobile_no,user_id,orignal_mobile_no=None):
    if len(mobile_no)>8 and len(mobile_no)<=14:
        if mobile_no.startswith('091'):
            mobile_no = validate_indian_number(mobile_no[3:],user_id,mobile_no)
        elif mobile_no.startswith('+91'):
            mobile_no = validate_indian_number(mobile_no[3:],user_id,mobile_no)
        elif mobile_no.startswith('0'):
            mobile_no = validate_indian_number(mobile_no[1:],user_id,mobile_no)
        elif mobile_no.startswith('91') and len(mobile_no)==12:
            mobile_no = validate_indian_number(mobile_no[2:],user_id,mobile_no)


        does_user_exist = UserProfile.objects.filter(mobile_no=mobile_no).exclude(user_id=user_id)
        if not does_user_exist:
            return mobile_no
        else:
            return orignal_mobile_no
    else:
        return mobile_no

def is_valid_indian_number(mobile_no):
    if len(mobile_no)>=8 and len(mobile_no)<=14:
        return True
    else:
        return False


def validate_username(username):
    if re.sub('[^A-Za-z0-9_.-]+', '_', username) == '_':
        return get_random_username()
    return re.sub('[^A-Za-z0-9_.-]+', '_', username)

 
def change_username(old_username,i=0):
    if not i:
        new_username = old_username.lower()
    else:
        new_username = old_username.lower()+str(i)
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

def remove_underscore(username):
    if username.startswith('_'):
        username = remove_underscore(username[1:])
    elif username.endswith('_'):
        username = remove_underscore(username[:-1])
    elif '__' in username:
        username = remove_underscore(username.replace('__','_'))
    return username

def check_comment_mention(old_username,new_username):
    all_comment = Comment.objects.filter(Q(comment__contains='@'+old_username)|Q(comment_html__contains='@'+old_username))
    if all_comment:
        for each_comment in all_comment:
            print "comment_found :   ", old_username,new_username,each_comment.comment,
            each_comment.comment = each_comment.comment.replace(old_username,new_username)
            each_comment.comment_html = each_comment.comment_html.replace(old_username,new_username)
            each_comment.save()
