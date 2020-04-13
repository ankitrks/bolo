from forum.user.models import ReferralCode

def run():
    for each_rec in ReferralCode.objects.all():
        # print each_rec
        each_rec.download_count = each_rec.downloads()
        each_rec.signup_count = each_rec.signup()
        each_rec.save()