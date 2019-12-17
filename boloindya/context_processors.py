language_options = (
    ('en', "1"),
    ('hi', "2"),
    ('ta', "3"),
    ('te', "4"),
    ('bn', "5"),
    ('kn', "6"),
    ('ml', "7"),
    ('mr', "8"),

)

#return {'all_languages':dict(language_options)[request.COKIES['LANG_CODE']]}
#from django.conf.settings import LANGUAGE_CODE
from django.utils import translation
def all_languages(request):
    return {'all_languages':dict(language_options)}

def current_language_id(request):
    #currentLang=django.utils.translation.get_language()
    #print currentLang
    #get_current_language as LANGUAGE_CODE
    return {'current_language_id':request.LANGUAGE_CODE}

