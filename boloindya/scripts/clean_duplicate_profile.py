from django.db.models import F,Q
from forum.user.models import UserProfile
from django.db.models import Count


def run():
    duplicate_profiles = UserProfile.objects.exclude(Q(social_identifier='')|Q(social_identifier=None)).values('social_identifier').annotate(social_identifier_count=Count('social_identifier')).filter(social_identifier_count__gt=1)      
    counter=0
    for each_duplicate in duplicate_profiles:
        print '###########',counter,'/',len(duplicate_profiles),"##############"
        counter+=1
        single_social_duplicate = UserProfile.objects.filter(social_identifier=each_duplicate['social_identifier']).order_by('-id')
        for b in  UserProfile.objects.filter(social_identifier=each_duplicate['social_identifier']).order_by('-id'):
            print  b.user.id,b.user.is_active,each_duplicate['social_identifier'],b.user.date_joined,UserProfile.objects.filter(social_identifier=each_duplicate['social_identifier']).count()
        deleteable_profile = single_social_duplicate[1:]
        for each_deleteable_profile in deleteable_profile:
            user =  each_deleteable_profile.user
            print user.id
            print user.delete()