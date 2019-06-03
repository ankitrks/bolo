from forum.topic.models import *

def run():
	# print "mmazazaz"
	polls = Poll.objects.filter(is_evaluated = False,is_active = True)
	correct_choice_polls_list = Choice.objects.filter(poll__in = polls,is_active = True,is_correct_choice = True).values_list('poll_id',flat=True)
	voting = Voting.objects.filter(poll_id__in =correct_choice_polls_list)
	for each_voting in voting:
		poll = each_voting.poll
		try:
			correct_choice = Choice.objects.get(poll =poll,is_correct_choice = True)
			leader,is_created = Leaderboard.objects.get_or_create(user =each_voting.user)
			if each_voting.choice == correct_choice:
				leader.total_score+= poll.score
				leader.correct_prediction_count+=1
			leader.total_prediction_count+=1
			leader.save()

		except:
			pass
	## cacluate rank
	all_leaderborad_obj = Leaderboard.objects.all().order_by('-total_score')
	for rank, leader in enumerate(all_leaderborad_obj):
		if leader.current_rank:
			if not leader.current_rank==rank:
				leader.last_rank = leader.current_rank
				leader.current_rank = rank
		else:
			leader.current_rank = rank
		leader.save()