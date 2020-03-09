# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from forum.category.models import *


def run():
    all_category = ['Lifestyle and Travel','ਜੀਵਨਸ਼ੈਲੀ ਅਤੇ ਯਾਤਰਾ','ଜୀବନଶ yle ଳୀ ଏବଂ ଭ୍ରମଣ |'],['Fitness','ਤੰਦਰੁਸਤੀ','ଫିଟନେସ୍'],['Fashion and Beauty','ਫੈਸ਼ਨ ਅਤੇ ਸੁੰਦਰਤਾ','ଫ୍ୟାଶନ୍ ଏବଂ ସ Beauty ନ୍ଦର୍ଯ୍ୟ |'],['Shopping / Reviews','ਖਰੀਦਦਾਰੀ / ਸਮੀਖਿਆ','ସପିଂ / ସମୀକ୍ଷା'],['General Knowledge','ਆਮ ਗਿਆਨ','ସାଧାରଣ ଜ୍ଞାନ |'],['Food and Cooking','ਭੋਜਨ ਅਤੇ ਖਾਣਾ','ଖାଦ୍ୟ ଏବଂ ରାନ୍ଧିବା |'],['Finance Knowledge','ਵਿੱਤ ਗਿਆਨ','ଅର୍ଥ ଜ୍ଞାନ'],['Story Telling','ਕਹਾਣੀ ਦੱਸਣਾ','କାହାଣୀ କହିବା'],['Health','ਸਿਹਤ','ସ୍ୱାସ୍ଥ୍ୟ'],['Motivation','ਪ੍ਰੇਰਣਾ','ପ୍ରେରଣା'],['Technology','ਟੈਕਨੋਲੋਜੀ','ଟେକ୍ନୋଲୋଜି |'],['Entertainment','ਮਨੋਰੰਜਨ','ଚିତ୍ତବିନୋଦନ |'],['Sports','ਖੇਡਾਂ','କ୍ରୀଡା'],['Relationships','ਰਿਸ਼ਤੇ','ସମ୍ପର୍କ'],['English Learning','ਇੰਗਲਿਸ਼ ਲਰਨਿੰਗ','ଇଂରାଜୀ ଶିକ୍ଷା'],['Entrance Exams','ਦਾਖਲਾ ਪ੍ਰੀਖਿਆਵਾਂ','ପ୍ରବେଶିକା ପରୀକ୍ଷା'],['Career and Jobs','ਕਰੀਅਰ ਅਤੇ ਨੌਕਰੀਆਂ','ବୃତ୍ତି ଏବଂ ଚାକିରି |'],['Open Podcasts','ਪੋਡਕਾਸਟ ਖੋਲ੍ਹੋ','ପୋଡକଷ୍ଟ ଖୋଲନ୍ତୁ |'],['Astrology','ਜੋਤਿਸ਼','ଜ୍ୟୋତିଷ ଶାସ୍ତ୍ର'],['Religion','ਧਰਮ','ଧର୍ମ']
    for each_category in all_category:
        try:
            category = Category.objects.get(title=each_category[0])
            category.punjabi_title=each_category[1]
            category.odia_title = each_category[2]
            category.save()
        except Exception as e:
            print each_category
            print 'category not found'
            print e




