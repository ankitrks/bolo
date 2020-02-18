from forum.user.models import *
from django.contrib.auth.models import User
import json

def run():
    all_data = []
    counter =1
    all_user = User.objects.all()
    for each_user in all_user:
        print "###########",counter,"/",len(all_user),"##########"
        counter+=1
        temp={}
        temp["user_id"] = str(each_user.id)
        temp["username"] = str(each_user.username)
        try:
            temp["profile_id"] = str(each_user.st.id)
            if each_user.st.mobile_no:
                temp["mobile_no"] = str(each_user.st.mobile_no)
            else:
                temp["mobile_no"] = ""
            if each_user.st.slug:
                temp["slug"] = str(each_user.st.slug)
            else:
                temp["slug"] = ""
        except Exception as e:
            print e
            temp["profile_id"] = ""
            temp["mobile_no"] = ""
            temp["slug"] = ""
        all_data.append(temp)
    with open('user_data_backup.json', 'w') as file:
        json.dump(all_data, file)
    file.close
