from forum.user.models import UserProfile
from forum.topic.models import BoloActionHistory
from django.db.models import F,Q
from drf_spirit.utils import add_bolo_score,reduce_bolo_score,get_weight_object
from django.contrib.contenttypes.models import ContentType


def run():
    for each_profile in UserProfile.objects.all():
        if each_profile.is_popular:
            try:
                history_obj = BoloActionHistory.objects.get( user = each_profile.user, action_object_type=ContentType.objects.get_for_model(each_profile), action_object_id = each_profile.id, action = get_weight_object('is_popular') )
                print "popualr found"
            except Exception as e:
                print e
                add_bolo_score(each_profile.user_id,'is_popular',each_profile)
                print "popular created"
        if each_profile.is_superstar:
            try:
                history_obj = BoloActionHistory.objects.get( user = each_profile.user, action_object_type=ContentType.objects.get_for_model(each_profile), action_object_id = each_profile.id, action = get_weight_object('is_superstar') )
                print "superstar found"
            except Exception as e:
                print e
                add_bolo_score(each_profile.user_id,'is_superstar',each_profile)
                print "superstar created"
