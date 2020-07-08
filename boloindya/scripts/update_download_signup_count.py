from forum.user.models import ReferralCode, ReferralCodeUsed
from datetime import datetime, timedelta

def run():
    #delete duplicate
    dupes_referral_code = ReferralCodeUsed.objects.filter(created_at__gte = datetime.now() - timedelta(hours=6)).values('code').annotate(Count('id')) .order_by().filter(id__count__gt=1)
    for referral_code in dupes_referral_code:
      ReferralCodeUsed.objects.filter(code=referral_code['code']).order_by('pk')[1:].delete()

    for each_rec in ReferralCode.objects.filter(id__in = \
            ReferralCodeUsed.objects.filter(created_at__gte = datetime.now() - timedelta(hours=6)).values_list('code_id', flat=True)\
                .distinct('code_id')):
        # print each_rec
        each_rec.download_count = each_rec.downloads()
        each_rec.signup_count = each_rec.signup()
        each_rec.save()