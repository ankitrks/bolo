# -*- coding: utf-8 -*-
from forum.topic.models import *
from django.contrib.auth.models import User
from forum.user.models import UserProfile,Follower
import random
from datetime import datetime, timedelta, date
from drf_spirit.utils import add_bolo_score
from forum.comment.models import Comment

def run():
    print "Start Time Eng_Engagment: ",datetime.now()
    all_test_userprofile_id = UserProfile.objects.filter(is_test_user=True).values_list('user_id',flat=True)
    user_ids = list(all_test_userprofile_id)
    user_ids = random.sample(user_ids,5000)
    action_type =['comment','like','seen','follow','share','comment_like']
    opt_action = random.choice(action_type)
    now = datetime.now()
    topic_ids = Topic.objects.filter(is_vb=True,is_removed=False).values_list('id', flat=True)
    topic_ids = list(topic_ids)
    actionable_ids = random.sample(topic_ids,1000)
    last_n_days_post_ids = Topic.objects.filter(is_vb=True,is_removed=False,date__gte=now-timedelta(days=3)).order_by('-date').values_list('id',flat=True)
    last_n_days_post_ids = list(last_n_days_post_ids)
    
    for each_seen_id in last_n_days_post_ids:
        try:
            each_seen = Topic.objects.get(pk=each_seen_id)
            if each_seen.date +timedelta(minutes=10) > now:
                number_seen = random.randrange(6,100)
            elif each_seen.date +timedelta(minutes=10) < now and each_seen.date +timedelta(minutes=30) > now and each_seen.view_count < 1000:
                number_seen = random.randrange(100,1000-each_seen.view_count)
            elif each_seen.date +timedelta(minutes=30) < now and each_seen.date +timedelta(hours=2) > now and each_seen.view_count < 10000:
                number_seen = random.randrange(1,10000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=2) < now and each_seen.date +timedelta(hours=4) > now and each_seen.view_count < 12000:
                number_seen = random.randrange(1,12000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=4) < now and each_seen.date +timedelta(hours=6) > now and each_seen.view_count < 13000:
                number_seen = random.randrange(1,13000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=6) < now and each_seen.date +timedelta(hours=8) > now and each_seen.view_count < 14000:
                number_seen = random.randrange(1,14000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=10) < now and each_seen.date +timedelta(hours=12) > now and each_seen.view_count < 15000:
                number_seen = random.randrange(1,15000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=12) < now and each_seen.date +timedelta(hours=14) > now and each_seen.view_count < 16000:
                number_seen = random.randrange(1,16000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=14) < now and each_seen.date +timedelta(hours=16) > now and each_seen.view_count < 17000:
                number_seen = random.randrange(1,17000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=16) < now and each_seen.date +timedelta(hours=18) > now and each_seen.view_count < 18000:
                number_seen = random.randrange(1,18000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=18) < now and each_seen.date +timedelta(hours=19) > now and each_seen.view_count < 19000:
                number_seen = random.randrange(1,19000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=19) < now and each_seen.date +timedelta(hours=20) > now and each_seen.view_count < 20000:
                number_seen = random.randrange(1,20000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=20) < now and each_seen.date +timedelta(hours=21) > now and each_seen.view_count < 25000:
                number_seen = random.randrange(1,25000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=21) < now and each_seen.date +timedelta(hours=24) > now and each_seen.view_count < 30000:
                number_seen = random.randrange(1,30000-each_seen.view_count)
            elif each_seen.date +timedelta(hours=24) < now and each_seen.date +timedelta(hours=72) > now and each_seen.view_count < 200000:
                number_seen = random.randrange(1,200000-each_seen.view_count)
            else:
                number_seen = 1
            i = 0
            while i < number_seen:
                try:
                    seen_profile_user_id = random.choice(user_ids)
                    action_seen(seen_profile_user_id,each_seen_id)
                    check_like(each_seen_id,all_test_userprofile_id)
                    i += 1
                except Exception as e:
		    print e
                    pass
        except:
            pass

    for each_like_id in last_n_days_post_ids:
        try:
            each_like = Topic.objects.get(pk=each_like_id)
            if each_like.likes_count < each_like.view_count/random.randrange(10,21):
                if each_like.date +timedelta(minutes=10) > now and each_like.view_count/random.randrange(10,21) > 100 and each_like.likes_count < 100:
                    number_like = random.randrange(6,100)
                elif each_like.date +timedelta(minutes=10) < now and each_like.date +timedelta(minutes=30) > now and each_like.view_count/random.randrange(10,21) > 200 and each_like.likes_count < 200:
                    number_like = random.randrange(100,200-each_like.likes_count)
                elif each_like.date +timedelta(minutes=30) < now and each_like.date +timedelta(hours=2) > now and each_like.view_count/random.randrange(10,21) > 300 and each_like.likes_count < 300:
                    number_like = random.randrange(1,300-each_like.likes_count)
                elif each_like.date +timedelta(hours=2) < now and each_like.date +timedelta(hours=4) > now and each_like.view_count/random.randrange(10,21) > 400 and each_like.likes_count < 400:
                    number_like = random.randrange(1,400-each_like.likes_count)
                elif each_like.date +timedelta(hours=4) < now and each_like.date +timedelta(hours=6) > now and each_like.view_count/random.randrange(10,21) > 500 and each_like.likes_count < 500:
                    number_like = random.randrange(1,500-each_like.likes_count)
                elif each_like.date +timedelta(hours=6) < now and each_like.date +timedelta(hours=8) > now and each_like.view_count/random.randrange(10,21) > 600 and each_like.likes_count < 600:
                    number_like = random.randrange(1,600-each_like.likes_count)
                elif each_like.date +timedelta(hours=10) < now and each_like.date +timedelta(hours=12) > now and each_like.view_count/random.randrange(10,21) > 700 and each_like.likes_count < 700:
                    number_like = random.randrange(1,700-each_like.likes_count)
                elif each_like.date +timedelta(hours=12) < now and each_like.date +timedelta(hours=14) > now and each_like.view_count/random.randrange(10,21) > 800 and each_like.likes_count < 800:
                    number_like = random.randrange(1,800-each_like.likes_count)
                elif each_like.date +timedelta(hours=14) < now and each_like.date +timedelta(hours=16) > now and each_like.view_count/random.randrange(10,21) > 900 and each_like.likes_count < 900:
                    number_like = random.randrange(1,900-each_like.likes_count)
                elif each_like.date +timedelta(hours=16) < now and each_like.date +timedelta(hours=72) > now and each_like.view_count/random.randrange(10,21) > 1000 and each_like.likes_count < 1000:
                    number_like = random.randrange(1,1000-each_like.likes_count)
                else:
                    number_like = 1
                i = 0
                while i < number_like:
                    try:
                        opt_action_user_id = random.choice(user_ids)
                        action_like(opt_action_user_id,each_like_id)
                        i += 1
                    except:
                        pass
        except:
            pass

    for each_topic_id in last_n_days_post_ids:
        action_type =['comment', 'seen','comment','like', 'comment', 'follow','comment', 'share', 'comment' ,'comment_like', 'comment']
        opt_action = random.choice(action_type)
        opt_action_user_id = random.choice(user_ids)
        if opt_action =='comment':
            action_comment(opt_action_user_id,each_topic_id)
        elif opt_action == 'like':
            each_topic = Topic.objects.get(pk=each_topic_id)
            if each_topic.likes_count<each_topic.view_count/random.randrange(10,21) and each_topic.likes_count < each_topic.view_count:
                action_like(opt_action_user_id,each_topic_id)
        elif opt_action == 'follow':
            action_follow(opt_action_user_id,Topic.objects.get(pk=each_topic_id).user.id)
        elif opt_action == 'share':
            action_share(opt_action_user_id,each_topic_id)
        elif opt_action == 'comment_like':
            all_comment_list_id = Comment.objects.filter(is_removed=False).values_list('user_id',flat=True)
            comment_ids = list(all_comment_list_id)
            comment_ids = random.sample(comment_ids,50)
            all_comment = Comment.objects.filter(pk__in =user_ids)
            for each_comment in all_comment:
                action_comment_like(opt_action_user_id,each_comment)
        elif opt_action == 'seen':
            action_seen(opt_action_user_id,each_topic_id)


    for each_topic_id in actionable_ids:
        action_type =['seen','comment','like','follow','share','comment_like']
        opt_action = random.choice(action_type)
        opt_action_user_id = random.choice(user_ids)
        if opt_action =='comment':
            action_comment(opt_action_user_id,each_topic_id)
        elif opt_action == 'like':
            each_topic = Topic.objects.get(pk=each_topic_id)
            if each_topic.likes_count<each_topic.view_count/random.randrange(10,21) and each_topic.likes_count < each_topic.view_count:
                action_like(opt_action_user_id,each_topic_id)
        elif opt_action == 'follow':
            action_follow(opt_action_user_id,random.choice(User.objects.all()).id)
        elif opt_action == 'share':
            action_share(opt_action_user_id,each_topic_id)
        elif opt_action == 'comment_like':
            all_comment_list_id = Comment.objects.filter(is_removed=False).values_list('user_id',flat=True)
            comment_ids = list(all_comment_list_id)
            comment_ids = random.sample(comment_ids,50)
            all_comment = Comment.objects.filter(pk__in =user_ids)
            for each_comment in all_comment:
                action_comment_like(opt_action_user_id,each_comment)
        elif opt_action == 'seen':
            action_seen(opt_action_user_id,each_topic_id)

    print "End Time Eng_Engagment: ",datetime.now()


def check_like(topic_id,user_ids):
    now = datetime.now()
    each_like = Topic.objects.get(pk=topic_id)
    if each_like.likes_count < each_like.view_count/random.randrange(10,21):
        if each_like.date +timedelta(minutes=10) > now and each_like.view_count/random.randrange(10,21) > 100 and each_like.likes_count < 100:
            number_like = random.randrange(6,100)
        elif each_like.date +timedelta(minutes=10) < now and each_like.date +timedelta(minutes=30) > now and each_like.view_count/random.randrange(10,21) > 200 and each_like.likes_count < 200:
            number_like = random.randrange(100,200-each_like.likes_count)
        elif each_like.date +timedelta(minutes=30) < now and each_like.date +timedelta(hours=2) > now and each_like.view_count/random.randrange(10,21) > 300 and each_like.likes_count < 300:
            number_like = random.randrange(1,300-each_like.likes_count)
        elif each_like.date +timedelta(hours=2) < now and each_like.date +timedelta(hours=4) > now and each_like.view_count/random.randrange(10,21) > 400 and each_like.likes_count < 400:
            number_like = random.randrange(1,400-each_like.likes_count)
        elif each_like.date +timedelta(hours=4) < now and each_like.date +timedelta(hours=6) > now and each_like.view_count/random.randrange(10,21) > 500 and each_like.likes_count < 500:
            number_like = random.randrange(1,500-each_like.likes_count)
        elif each_like.date +timedelta(hours=6) < now and each_like.date +timedelta(hours=8) > now and each_like.view_count/random.randrange(10,21) > 600 and each_like.likes_count < 600:
            number_like = random.randrange(1,600-each_like.likes_count)
        elif each_like.date +timedelta(hours=10) < now and each_like.date +timedelta(hours=12) > now and each_like.view_count/random.randrange(10,21) > 700 and each_like.likes_count < 700:
            number_like = random.randrange(1,700-each_like.likes_count)
        elif each_like.date +timedelta(hours=12) < now and each_like.date +timedelta(hours=14) > now and each_like.view_count/random.randrange(10,21) > 800 and each_like.likes_count < 800:
            number_like = random.randrange(1,800-each_like.likes_count)
        elif each_like.date +timedelta(hours=14) < now and each_like.date +timedelta(hours=16) > now and each_like.view_count/random.randrange(10,21) > 900 and each_like.likes_count < 900:
            number_like = random.randrange(1,900-each_like.likes_count)
        elif each_like.date +timedelta(hours=16) < now and each_like.date +timedelta(hours=72) > now and each_like.view_count/random.randrange(10,21) > 1000 and each_like.likes_count < 1000:
            number_like = random.randrange(1,1000-each_like.likes_count)
        else:
            number_like = 1
        i = 0
        while i < number_like:
            try:
                opt_action_user_id = random.choice(user_ids)
                action_like(opt_action_user_id,topic_id)
                i += 1
            except:
                pass



#comment
def action_comment(user_id,topic_id):
    comment_list = ["Good way of making people understand","Your videos really help.","Your depth and understanding is commendable...you are doing a great job..stay blessed","Very very helpful, thank you","Thanks for the effort.","i really apperciate your wonderful explanation","thank you  for your research on topic.....respect....!!!!!!","Very informative ","Actually , your voice soothes mind","Thank you for your time on the research and explain on this topic. Impressive !","Thanks a lot to You !!","ur way of explaining issues is quiet different. So easy","Extremely good brief explanation","great explaination thank you for your efforts","Wow, it was an amazing explanation","Quite insightful","Thank you very much .. U gav me exactly what i was looking for","thanks fr making me understand so nicely.","These are so informative and clearing out all basic confusions","Hello... I am following all your videos","Thanks you so much  for creating my interest on studies","I am so thankful to you for providing such information","I appreciate your method to avail us such information.","you are just wonderful... thank you so much.","Thankyou so much for the great great great explanation ","Great job ...really I watched your video so carefully and honestly........ Thank you ","Well Done, very informative video with all details. keep it up brother","feeling blessed to see your videos. Love.","Very well explained, made easy to understand,, Thank you so much","This video is awesome and thanks for it.","One of the best content video available for this issue!","Thanks a tone for making such efforts.","Truly liked this","Nicely presented, this lecture made clear understanding !","Every concept explained in a very lucid way.Great great great video","u always make amazing videos","Thank you so much  ji","You are a good, knowledged person..... We have been learning from your brain, thank you for the efforts..","This is very interesting knowledge for me..I think all people. Thanks.","Very well explained, thank you","Thanks mate u have great knolwedge sharing skills","U make everything really easy to understand","u have cleared our whole concept regarding the issue thanks a lot for this","ur learning journey fruitful day by day","Excellent explaination and superb sequence selection.","No one can explain with this conviction , thank you","keep the work going","Very informative lecture","Awesome video... searching for such type of knowledgeable video","I really like your video very much","u r great I like so much this video","I am happy that your good knowledge","Very nice video. Very clear and detailed explanation. Thank you for this","The video is really explanatory. Very good work","Incredibly you shared the knowledge and view","Very informative and helpful video. Please keep it up","Could you please provide more of this type video","Very interesting and informative","Very interesting and informative","Your narrative version is imppecable...too good explaination","nice analysis keep it up","Thanks . Well explained","Point to point... thank you so much","This video is so good and easy to understand","Thank you ..... for giving this video","Superrrrrrrb. thanks for making this type of marvelous video.keep it up","Very good lecture,Thanks for sharing knowledge.","I salute your dedication .. great video...","You explain it very coherently thanks.","Your videos are very informative... Thanks","Very informative and neutral view good job","Excellent.Thankyou ","Explained very clear ...thank you.","I'm extremely thankful for these amazing videos that u make","Very informative..keep them going","Very informative & explained in a lucid manner.","very detailed explanation for a very complex topic","Fantastic video good knowledge provided by you hats off to you","nice video with full of information and understandable.","One of the best video of study","Thanxs  for giving such a nice knowledge.","wonderful explanation...","very nice explanation... doubts cleared","Well explained, most of the topics covered lucidly.","Interestingly ending the topic for peaceful resolution is appreciated.","Very beutifully explained .Hatts off....Great....","Fantastic,nicely explained.","Thanks for best Presentation.","Brilliant job dear","The video was very informative","Very well described . Thanks","Very nice video ....clear understanding of the topic..","Very informative video. Hats off to you.","You are doing a tremendous job.","appreciate your efforts your narrating is best","great source of information.","very good knowledge ","thanks for the video, very informative for all of us….","Excellent...cleared all the doubts","amazing course superb way of explaining things Impressive voice","nice love you all members please keep it up ????","very informative","fantastic explaining gestures u have!!!! made me fall for your content!!! bestie for future love to get in touch with ur positivity","really awesome","thank you ","Superb","Great!","so...nice","good knowledge","interesting","Thank you so much Ma'am","its very usefull","fine , it is good for gk","Thank you so much mam this is really great explain","Great job! thank you","Good work","It's very useful","it's a fantastic initiative......for learners.","realy it is more useful..","excellent teaching skill and the way is very interesting for understanding ,good job","beautiful presentation. enjoying the new approach to learning. thank you","it's always good to know this things thankyou please continue.","Thanks alot mam.... Unbelievable things I came to know","ur voice...wowwww","Very nice piece of information. Its Amazing !!","interesting .. good teaching...","awesome video, very interesting","wonderfully explained..!","Thanks good info","wow... amazing teaching","quite interesting","Mind blowing.....","interesting...","Gr8 JOB!","perfectly explained . very clear..👍","it's beneficial for us way it taught make good","Wonderful","Very nicely explained... Please keep enriching our knowledge with this daily trivia plan..!!!","cool...","interesting thank for the knowledge","Excellent....","awesome","knowledge is the door of the oppertunity to something get new","wow its really amazing","its so great","excellent!, ur pronunciation and teaching method are so good..... when watching this i really enjoyed.","it is wonderful....","thanks a lot","awesome graphics , awesome presentation.","Information as well as presentation both were superb. Thanks","Just wow..","love the the way u teach","I would like. please continue this course. thanks again.","amazing","Nice lactur","Excellent Explain.","I like the way u learn bcoz it's Very easy to understand nd interesting also thanks keep Guiding","Thank you so much","some point but describe easily all..best way I think it's lajawab..have. a good day..","I started today only. but I am like addicted I kept on going","Your voice made me to love the reading and learning the comoplex concepts in crystal clear .","I hv never commented till date, but must praise ur way of eliminating options n getting answers.... Superb man! N yes ur voice is the best i hv ever heard","What a voice !!!","Amazing explanation.thanks :-)","U r so talented., I just can't believe u know so many facts.. Are u a cimputed or an encyclopedia","Explanation is good","Believe me you are a genius......!!!","love ur explanation n you voice too","lovely, what an explanation.Boring things even become easier in this way","way you explain it's great and your voice so innocent..","Awesome explanation!!!","I like the sound of ur accent","Superb .. no words... Brilliant 😊","Ur voice !! And obviously very good video. Thumbs up to your dedication for helping us","thanks alot , it will really help me","great job","Bdw good explanation though..","What a voice 😍","Got to know how we have to look into a question and element the wrong one's.. thanks you","what are the points one must note or study","it's a great technique","Very informative video","wow ! thanks","great work ","thank you so much....","Your way of explaining is too good to leave","Nice ","Great, more helpful","really useful","very nice ","you really have a nice voice","Outstanding pure worth to watch this video","Good job ...","too good","Nice","Thank you so much  please aisi video or banaye","Nice explanation with logic ...","more usefull information","your voice sounds like experiance guy"," your voice is too good....","Voice 👌👌","Wonderful explanation...","Ur superb ","wow, I need these types of video more.","great analysis...waiting for next videos..thanks","brilliant!!👌","Nice explaination !","awesome video","u hav an amazing voice ....just makes me do study hard .","u explains amazingly amazing........","Nicely explained. ...........","Super teaching","Thank you very much.....","Pleasant voice 👍👍👍","It make lot of sense...","thank you ! please help with other sections also.","This was great , I mean seriously the best !","excellent clarification ","Great explanation with clear pronunciation.","good ","Awesome buddy","thnx .. keep up the good work","thankyou","Your voice very sweet and english is very perfect wao nice"," plz makes more videos on this... Plz..","Thank you very much  for a wonderful and clear explanation. Btw your voice is very pleasant. Everyone gets addicted to your voice.","Ur way of explaining things is really good..","pure explanation","Yeh !! Thanks ","Great Effort ... Thanku!!!","Plz bring more such types of analysation","Blessed with mesmerizing voice","thanks please upload some more videos of same","Gud job ya","It's easyyyyy","Thank you  more update","Nicely explained and Oh My God..the voice..amazing bro.... keep it up...need more videos","Superb  I'm speechless","THANK You! So much , helping us with your great idea, Now i understand!! Really helpful!","Shaandaar explanation Thanks ","Amazing..... :)","you are a gem... 😊😊","thank you . its really helpful","u r absolutely marvelous....","perfect","Your all videos are outstanding ","great explanation....... i learnt how to related different things to reach destinations........... thankyou ","this is brilliant keep it coming !","Gr8","One of the Best analysis I have ever seen .. n what a charismatic voice !! Too good","explaning it in less time.. is also beneficial for us thank for it....","gud job..appreciations...","I have seen all your videos. They are amazing. This is something that reached my expectations after a lot of ground work.","Excellent work . Thank you so much. Please do more videos covering all the subjects. Thank you :)","Awesome ...gr8 job ur1 hlping lot of students...","ur nailed it bro",", i wish i would be as knowledgeble as u r. U analysed it very well n ur voice made me to listen it."," Thank you so much for the great explanation and ideas that you are giving us. May God continue to bless you for your good work.","This is free therapy to me... Cheers - keep up","nice explanation... it's very clear","Excellent ","I think I have nothing to say about this vid bcoz people have already stolen all the words which I want to say Thanks for the wonderful explanation","Perfect explanations thank you ","Grt ","thanks for sharing such info as it helps students.","the way you speak... .....Simply awesome","plz u make more video bcz u analysis with all point","you're so smart.","What a voice.. Simply adorable... And very well explained ","Nice strategies to solve","Thank you so much  for your conspicuous video.. You have such a clarity of thought in handling the questions..","Impresive","nice work r","Ur voice dear so soothing. Thank you for the lesson","I was AMAZED by your Great Explanation and voice","Woahhhh....!!!!","thanks a lot","Muze bahot Pasand Aya video....Mai bhi Kuch banna chahti hu...","I liked the way , how you pronounced","You are very good ...thanks for putting enormous efforts for us","Wow.... I don't have words to explain your excellency ... Thank you so much","Very very very very nyc explanation","you are osssome.","Veryyyyy intelligent .......  plz make more videos like this ...very helpful.","There is something special in your voice... that's very motivating...☺","please make more video for other topics too...","osm approach.....","Very accurate explanations.!! We would like to see more papers solved. Thank you","👍👍👍👍 knowelegeble","thanks ","Dhnyawad 🙏","Excellent","Ghazab explanation.!","Very good explanation ..... Plz gve ur conct Nmbr","Good job ","wonderful.......Thanks","please upload other topics analysis","I m in love wd ur the way of communication","Very nicely explained ..Thank you","Soooooooooo gud....😘😍","Gud explanation.. Thank a lot ","your analysis is very much useful..actually, is paving path ...awesome","what a voice....","expecting more videos from you  ,thank u","Very Thankful to you , nice explanation to each and every question.......,......","Hi and thankss for uploading this video. Although I would request you to upload more video","thanks a lot !! thump up !!","Thanks a lot  g....","Thank you  this information..","fan ban gaya, thnq ","awesome  ji thank you so much","Very useful for future","mujhe to bhut help mili thnks wonderfull aise hi lecture provide kijiye","Please make for other topics also","Make similar video for other topics also","well explained bro","Thank you Guruji🙏🙏","Nice vdo ","thankyou for guidance","Good explanation keep rocking","thanks a lot for making ma'am","Thank you so much for this contribution and for your precious time.","thanx a lot","thanks so much","NICE ","👍😊 You're the best","Helpful","Mam you are just amazing","thank you very much! please do not stop making this in the mid way, try to continue","Very marvelous deed ","I hope this course doesn't end abruptly....","It's going to be a great approach .","pls continue it  for a life long","thank you  plzzzzz continue🙏","The great initiative","that's amazing :-)","good one","not bad...","awsum","thank u so much ..","mind blowing ","i honestly watched it out of plain curiosity.. loved it.. thankyou","👍","👍👍","👍👍👍","🙏","🙏🙏","🙏🙏🙏","👍😊","😘😍","😘😍😘😍","👌👌","👌","👌👌👌"]
    comment = Comment()
    userprofile = get_userprofile(user_id)
    comment.comment       = random.choice(comment_list)
    comment.comment_html  = random.choice(comment_list)
    comment.language_id   = userprofile.language
    comment.user_id       = user_id
    comment.topic_id      = topic_id
    comment.save()
    topic = Topic.objects.get(pk = topic_id)
    topic.comment_count = F('comment_count')+1
    topic.last_commented = timezone.now()
    topic.save()
    userprofile.answer_count = F('answer_count')+1
    userprofile.save()
    comment.save()
    add_bolo_score(user_id, 'reply_on_topic', comment)

#like
def action_like(user_id,topic_id):
    liked,is_created = Like.objects.get_or_create(topic_id = topic_id ,user_id = user_id)
    if is_created:
        topic = get_topic(topic_id)
        topic.likes_count = F('likes_count')+1
        topic.save()
        userprofile = get_userprofile(user_id)
        userprofile.like_count = F('like_count')+1
        userprofile.save()
        add_bolo_score(user_id, 'liked', topic)

#seen
def action_seen(user_id,topic_id):
    topic = get_topic(topic_id)
    vbseen = VBseen.objects.filter(user_id = user_id,topic_id = topic_id)
    if not vbseen:
        vbseen = VBseen.objects.create(user_id = user_id,topic_id = topic_id)
        add_bolo_score(topic.user.id, 'vb_view', vbseen)
    else:
       vbseen = VBseen.objects.create(user_id = user_id,topic_id = topic_id)
    topic.view_count = F('view_count')+1
    topic.save()
    userprofile = get_userprofile(topic.user.id)
    userprofile.view_count = F('view_count')+1
    userprofile.save()

#follow
def action_follow(test_user_id,any_user_id):
    follow,is_created = Follower.objects.get_or_create(user_follower_id = test_user_id,user_following_id=any_user_id)
    userprofile = get_userprofile(test_user_id)
    followed_user = get_userprofile(any_user_id)
    if is_created:
        add_bolo_score(test_user_id, 'follow', userprofile)
        add_bolo_score(any_user_id, 'followed', followed_user)
        userprofile.follow_count = F('follow_count')+1
        userprofile.save()
        followed_user.follower_count = F('follower_count')+1
        followed_user.save()
#share
def action_share(user_id, topic_id):
    share_type =['facebook_share','whatsapp_share','linkedin_share','twitter_share']
    share_on = random.choice(share_type)
    userprofile = get_userprofile(user_id)
    topic = get_topic(topic_id)
    if share_on == 'facebook_share':
        shared = SocialShare.objects.create(topic = topic,user_id = user_id,share_type = '0')
        topic.facebook_share_count = F('facebook_share_count')+1    
        topic.total_share_count = F('total_share_count')+1
        topic.save()
        add_bolo_score(user_id, 'facebook_share', topic)
        userprofile.share_count = F('share_count')+1
        userprofile.save()
    elif share_on == 'whatsapp_share':
        shared = SocialShare.objects.create(topic = topic,user_id = user_id,share_type = '1')
        topic.whatsapp_share_count = F('whatsapp_share_count')+1
        topic.total_share_count = F('total_share_count')+1
        topic.save()
        add_bolo_score(user_id, 'whatsapp_share', topic)
        userprofile.share_count = F('share_count')+1
        userprofile.save()
    elif share_on == 'linkedin_share':
        shared = SocialShare.objects.create(topic = topic,user_id = user_id,share_type = '2')
        topic.linkedin_share_count = F('linkedin_share_count')+1
        topic.total_share_count = F('total_share_count')+1
        topic.save()
        add_bolo_score(user_id, 'linkedin_share', topic)
        userprofile.share_count = F('share_count')+1
        userprofile.save()
    elif share_on == 'twitter_share':
        shared = SocialShare.objects.create(topic = topic,user_id = user_id,share_type = '3')
        topic.twitter_share_count = F('twitter_share_count')+1
        topic.total_share_count = F('total_share_count')+1
        topic.save()
        add_bolo_score(user_id, 'twitter_share', topic)
        userprofile.share_count = F('share_count')+1
        userprofile.save()

#comment like
def action_comment_like(user_id,comment):
    liked,is_created = Like.objects.get_or_create(comment = comment ,user_id = user_id)
    if is_created:
        comment.likes_count = F('likes_count')+1
        comment.save()
        add_bolo_score(user_id, 'liked', comment)
        userprofile = get_userprofile(user_id)
        userprofile.like_count = F('like_count')+1
        userprofile.save()

def get_topic(pk):
    return Topic.objects.get(pk=pk)

def get_user(pk):
    return User.objects.get(pk=pk)

def get_userprofile(user_id):
    return UserProfile.objects.get(user_id=user_id)
