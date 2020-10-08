from forum.comment.models import Comment
from forum.topic.models import Topic
from forum.user.models import UserProfile
from forum.comment.models import GiphyDetails
from forum.comment.utils import update_giphy_redis

from django.db.models import F
from django.utils import timezone

from redis_utils import *
import pandas as pd
import random
import decimal

TEST_USER_START_INDEX_POOL = 5000000
TEST_USER_POOL = 500000
class AddGiphyCommentsToVideo:
	def __init__(self, *args, **kwargs):
		self.topic_id = kwargs.get('topic_id', None)
		self.number_of_likes = kwargs.get('number_of_likes',0)

	def start(self):
		try:
			print("starting adding comment on topic_id "+str(self.topic_id)+" with like counts "+ str(self.number_of_likes))
			required_comments = int(decimal.Decimal(random.randrange(int(self.number_of_likes*0.13), int(self.number_of_likes*0.27))))
			print("required comments "+ str(required_comments))

			exisiting_comments = Topic.objects.get(pk=self.topic_id).topic_comment.all()
			exisiting_comments_user_ids = list(exisiting_comments.values_list('user_id',flat=True))
			start_index = random.randint(0,TEST_USER_START_INDEX_POOL)
			end_index = start_index + TEST_USER_POOL
			print(start_index, end_index)

			user_ids = list(UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=exisiting_comments_user_ids).values('user_id')[start_index:end_index])
			if len(user_ids)>=required_comments:
				user_ids = random.sample(user_ids, required_comments)
			else:
				user_ids = list(UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=exisiting_comments_user_ids).values('user_id')[:required_comments])
			user_df = pd.DataFrame(user_ids)

			#get giphy data
			giphy_df = self.get_giphy_data(required_comments)

			final_df = pd.concat([user_df, giphy_df], axis=1)
			final_df['topic_id'] = self.topic_id
			final_df.dropna(inplace=True)
			final_dict = final_df.to_dict('records')
			print("adding comments: "+str(len(final_dict)))

			comment_list = [Comment(**vals) for vals in final_dict]
			if comment_list:
				comment_obj = Comment.objects.bulk_create(comment_list, batch_size=10000)

				topic = Topic.objects.filter(id=self.topic_id)
				topic.update(comment_count = F('comment_count')+len(comment_list))
				topic.update(last_commented = timezone.now())
				print("comments added")

				print("done")
			else:
				print("empty comment data, please check")
		except Exception as e:
			print(e)

	def get_giphy_data(self, required_comments):
		giphy_data_list = list(get_smembers_redis("giphy_details:"))
		if not giphy_data_list:
			giphy_data_list = list(GiphyDetails.objects.values_list('giphy_id',flat=True))
			update_giphy_redis(giphy_data_list)
		giphy_data = giphy_data_list[:required_comments]
		if len(giphy_data_list)>required_comments:
			giphy_data = random.sample(giphy_data_list, required_comments)
		giphy_df = pd.DataFrame(list(giphy_data),columns=['gify_details'])
		giphy_df = giphy_df['gify_details'].apply(lambda x: json.dumps({"id": str(x)}))
		return giphy_df
