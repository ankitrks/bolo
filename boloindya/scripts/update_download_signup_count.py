from forum.user.models import ReferralCode, ReferralCodeUsed
from datetime import datetime, timedelta

def run():
    #delete duplicate
    dupes_referral_code = ReferralCodeUsed.objects.exclude(by_user__isnull = True).filter(created_at__gte = datetime.now() - timedelta(hours=6)).values('code_id','by_user_id').annotate(Count('id')).filter(id__count__gt=1)
    for referral_code in dupes_referral_code:
        ReferralCodeUsed.objects.filter(code_id=referral_code['code_id'],by_user_id=referral_code['by_user_id']).order_by('pk')[1:].delete()

    for each_rec in ReferralCode.objects.filter(id__in = \
            ReferralCodeUsed.objects.filter(created_at__gte = datetime.now() - timedelta(hours=6)).values_list('code_id', flat=True)\
                .distinct('code_id')):
        # print each_rec
        each_rec.download_count = each_rec.downloads()
        each_rec.signup_count = each_rec.signup()
        each_rec.save()