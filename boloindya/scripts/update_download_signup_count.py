from forum.user.models import ReferralCode

def run():
    for each_rec in ReferralCode.objects.filter(id__in = \
            ReferralCodeUsed.objects.filter(created_at__gte = datetime.now() - timedelta(hours=6)).values_list('code_id', flat=True)\
                .distinct('code_id')):
        # print each_rec
        each_rec.download_count = each_rec.downloads()
        each_rec.signup_count = each_rec.signup()
        each_rec.save()