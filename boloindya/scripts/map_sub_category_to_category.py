from forum.topic.models import *
from forum.category.models import *
from forum.user.models import *


new_category = [{'category':'Sports','sub_category':['Cricket','Football','Hockey','Tennis','Games']},{'category':'Open Podcasts','sub_category':[]},{'category':'Career and Jobs','sub_category':['Entrepreneurs','Startups','Certifications','Jobs','Analytics']},{'category':'General Knowledge','sub_category':['Liberals','Nationalism','Politics','Books','Bollywood','Tollywood','Hollywood','TV Series','Mobile','Cars','Comedy','News','Gadgets']},{'category':'Entrance Exams','sub_category':['UPSC','MBA','Banking','SSC CGL','RBI','IIT JEE','NEET']},{'category':'Motivation','sub_category':['Motivation','Inspiration','Success Stories']},{'category':'Relationships','sub_category':['Marriage','Sex','Breakups']},{'category':'Women health','sub_category':[]},{'category':'Fitness','sub_category':[]},{'category':'Food and Cooking','sub_category':['Food']},{'category':'Fashion and Beauty','sub_category':['Make Up','Fashion','Make up']},{'category':'Lifestyle and Travel','sub_category':['Travel','Culture','Religion']}]
new_category_with_lang =[['Sports','स्पोर्ट्स','ஸ்போர்ட்ஸ் ','స్పోర్ట్స్'],['Open Podcasts','ओपन पॉडकास्ट','ஓபன் போட்காஸ்ட் ','ఓపెన్ పాడ్కాస్ట్స్'],['Career and Jobs','करियर ऐंड जॉब्स','கரியர் அண்ட் ஜாப்ஸ்','కెరీర్ అండ్ జాబ్స్'],['General Knowledge','जनरल नॉलेज','ஜெனரல் நாலெட்ஜ்','జనరల్ కనౌలెడ్జి'],['Entrance Exams','एंंट्रेस एग्जाम','என்ட்ரன்ஸ் எக்ஸாம்ஸ்','ఎంట్రన్స్ ఎగ్జామ్స్'],['Motivation','मोटिवेशन','மோட்டிவேஷன் ','మోటివేషన్'],['Relationships','रिलेशनशिप','ரிலேஷன்ஷிப்','రిలేషన్షిప్స్'],['Women Health ','वूमन हेल्थ','வுமன் ஹெல்த்','విమెన్ హెల్త్'],['Fitness','फिटनेस','பிட்னெஸ்','ఫిట్నెస్'],['Food and Cooking','फूड ऐंड कूकिंग','போவ்ட் அண்ட் குக்கிங் ','ఫుడ్ అండ్ కుకింగ్'],['Fashion and Beauty','फैशन ऐंड ब्यूटी','பேஷன் அண்ட் பியூட்டி','ఫాషన్ అండ్ బ్యూటీ'],['Lifestyle and Travel','लाइफस्टाइल ऐंड ट्रैवल','லைப்ஸ்டைல் அண்ட் ட்ராவல் ','లైఫ్స్టైల్ అండ్ ట్రావెల్']] 
new_parent_category,is_created  = Category.objects.create(title="new_category")
print new_parent_category,is_created
for each in new_category_with_lang:
	a,b = Category.objects.create(title=each[0],hindi_title = each[1],tamil_title=each[2],telgu_title=each[3],parent=new_parent_category)
	print a,b
for each_topic in Topic.objects.all():
	for each_category in new_category:
		if str(each_topic.category.title) in each_category['sub_category']:
			print str(each_category['category']),new_parent_category,each_topic.category.title,each_category['sub_category']
			each_topic.category=Category.objects.get(title=str(each_category['category']),parent=new_parent_category)
			each_topic.save()

for each_profile in UserProfile.objects.all():
	all_followed_category = each_profile.sub_category.all()
	if all_followed_category:
		for each_follow_category in all_followed_category:
			for each_category in new_category:
				print str(each_follow_category.title), each_category['sub_category']
				if str(each_follow_category.title) in each_category['sub_category']:
					each_profile.sub_category.add(Category.objects.get(title=str(each_category['category']),parent=new_parent_category))
					each_profile.sub_category.remove(each_follow_category)

### remove duplicates in profile

for each_profile in UserProfile.objects.all():
	all_followed_category = each_profile.sub_category.all()
	exist = []
	for each_category in all_followed_category:
		if each_category in exist:
			each_profile.sub_category.remove(each_category)
		else:
			exist.append(each_category)