import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from django.utils import timezone
from datetime import datetime,timedelta
import calendar
import json
from django.core.serializers.json import DjangoJSONEncoder
from forum.user.models import ReferralCode,ReferralCodeUsed
import os

def run():
    my_csv=''
    my_csv+='username,paytm number,Date,Download Count,Signin Count,Sign in username--date_joined,\n'
    for each_refercode in ReferralCode.objects.filter(is_refer_earn_code=True,purpose='refer_n_earn'):
        if each_refercode.signup():
            my_csv+=get_refer_earn(each_refercode,str((datetime.now()-timedelta(days=1)).date().strftime("%d-%m-%Y")))
    file = open("refer_earn_"+str((datetime.now()-timedelta(days=1)).date().strftime("%d-%m-%Y"))+".csv","w")
    file.write(my_csv)
    file.close()
    send_file_mail("refer_earn_"+str((datetime.now()-timedelta(days=1)).date().strftime("%d-%m-%Y"))+".csv")

def get_refer_earn(each_refercode,start_date='09-04-2020'):
    csv=''
    # print start_date
    start_date = datetime.strptime(start_date, "%d-%m-%Y")
    days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
    end_date = datetime.strptime(str(start_date.day)+'-'+str(start_date.month)+'-'+str(start_date.year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
    current_datetime = datetime.now()-timedelta(days=1)

    #delete duplicate
    dupes_referral_code = ReferralCodeUsed.objects.filter(created_at__gte = datetime.now() - timedelta(hours=6)).values('code').annotate(Count('id')) .order_by().filter(id__count__gt=1)
    for referral_code in dupes_referral_code:
        ReferralCodeUsed.objects.filter(code=referral_code['code']).order_by('pk')[1:].delete()

    downloaded =ReferralCodeUsed.objects.filter(code = each_refercode, is_download = True, by_user__isnull = True,created_at__gte=start_date,created_at__lte=end_date).distinct('android_id')
    signedup = ReferralCodeUsed.objects.filter(code = each_refercode, is_download = True, by_user__isnull = False,created_at__gte=start_date,created_at__lte=end_date).distinct('by_user_id')
    download_count = downloaded.count()
    signedup_count = signedup.count()
    signned_in_user = ''
    if signedup:
        for each_user in signedup:
            signned_in_user +=str(each_user.by_user.username)+'---'+str(each_user.by_user.date_joined)+' & '
        csv+=str(each_refercode.for_user.username)+','+str(each_refercode.for_user.st.paytm_number)+','+str(start_date.date())+','+str(download_count)+','+str(signedup_count)+','+signned_in_user+',\n'

    if current_datetime > end_date:
        days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
        if end_date.day+1 <= days:
            day = str(end_date.day+1)
            csv+=get_refer_earn(each_refercode,str(day)+'-'+str(end_date.month)+'-'+str(end_date.year))
        else:
            if end_date.month+1<=12:
                csv+=get_refer_earn(each_refercode,str(day)+'-'+str(end_date.month+1)+'-'+str(end_date.year))
            else:
                year = str(end_date.year+1)
                csv+=get_refer_earn(each_refercode,'01-01-'+year)
                
    return csv


def send_file_mail(file_name):
    emailfrom = "support@careeranna.com"
    emailto = "ankit@careeranna.com"
    # emailto = "maaz@careeranna.com"
    filetosend = os.getcwd() + "/"+file_name
    username = "support@careeranna.com"
    password = "$upp0rt@30!1"               # please do not use this()

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Subject"] = "Refer N Earn Stats: " + str((datetime.now()-timedelta(days=1)).date().strftime("%d-%m-%Y"))
    msg.preamble = ""

    ctype, encoding = mimetypes.guess_type(filetosend)
    if(ctype is None or encoding is not None):
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)
    fp = open(filetosend, "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename = 'Refer N Earn Stats - ' + str((datetime.now()-timedelta(days=1)).date().strftime("%d-%m-%Y")))
    msg.attach(attachment)

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username, password)
    server.sendmail(emailfrom, [emailto, 'tanmai@careeranna.com','anshika@boloindya.com', 'varun@boloindya.com','maaz@careeranna.com'], msg.as_string())
    # server.sendmail(emailfrom, [emailto], msg.as_string())
    server.quit()
    os.remove(os.getcwd() + "/"+file_name)


