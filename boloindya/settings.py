# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE
# YOU MAY EXTEND/OVERWRITE THE DEFAULT VALUES IN YOUR settings.py FILE

from __future__ import unicode_literals
import os
from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _

# TODO: Remove this whole module in Spirit 0.6

import warnings

import os
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = 'boloindya'#PROJECT_PATH.split(os.sep)[-1]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PROJECT_PATH + '/cred.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PROJECT_PATH + '/boloindya-vision.json'

# warnings.simplefilter("default", RemovedInNextVersionWarning2)

# warnings.warn(
#     "`forum.settings` is deprecated and it will be removed in Spirit 0.6. "
#     "You are most likely seeing this because settings.base.py contains "
#     "`from forum.settings import *`. "
#     "The best way to procede is to create a clean project (run "
#     "`spirit startproject mysite`) and modify the settings as needed. "
#     "It's a straightforward procedure.",
#     category=RemovedInNextVersionWarning2,
#     stacklevel=2)

DEBUG = True
# TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'urls'

ST_TOPIC_PRIVATE_CATEGORY_PK = 1

ST_RATELIMIT_ENABLE = True
ST_RATELIMIT_CACHE_PREFIX = 'srl'
ST_RATELIMIT_CACHE = 'default'
ST_RATELIMIT_SKIP_TIMEOUT_CHECK = False

ST_NOTIFICATIONS_PER_PAGE = 20

ST_COMMENT_MAX_LEN = 3000
ST_MENTIONS_PER_COMMENT = 30
ST_DOUBLE_POST_THRESHOLD_MINUTES = 30

ST_YT_PAGINATOR_PAGE_RANGE = 3

ST_SEARCH_QUERY_MIN_LEN = 3

ST_USER_LAST_SEEN_THRESHOLD_MINUTES = 1

ST_PRIVATE_FORUM = False

# PNG is not allowed by default due to:
# An HTML file can be uploaded as an image
# if that file contains a valid PNG header
# followed by malicious HTML. See:
# https://docs.djangoproject.com/en/1.11/topics/security/#user-uploaded-content
ST_ALLOWED_UPLOAD_IMAGE_FORMAT = ('jpeg', 'jpg', 'gif')
ST_UPLOAD_IMAGE_ENABLED = True

# Only media types are allowed:
# https://www.iana.org/assignments/media-types/media-types.xhtml
ST_ALLOWED_UPLOAD_FILE_MEDIA_TYPE = {
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'pdf': 'application/pdf'}
ST_UPLOAD_FILE_ENABLED = True

ST_ALLOWED_URL_PROTOCOLS = {
    'http', 'https', 'mailto', 'ftp', 'ftps',
    'git', 'svn', 'magnet', 'irc', 'ircs'}

ST_UNICODE_SLUGS = True

ST_UNIQUE_EMAILS = True
ST_CASE_INSENSITIVE_EMAILS = True

# Tests helpers
ST_TESTS_RATELIMIT_NEVER_EXPIRE = False

ST_BASE_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(__file__)
BASE_DIR_TRANS = os.path.dirname(os.path.dirname(__file__))

BASE_URL='https://www.boloindya.com/'
ABSOLUTE_URL='https://www.boloindya.com'

#BASE_URL='https://www.boloindya.com/'
#
# Django & Spirit settings defined below...
#

INSTALLED_APPS = [
    # 'jet',
    'grappelli',
    'django.contrib.admin',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'django.contrib.humanize',
    'rest_framework',

    'forum.core',
    'forum.admin',
    'forum.search',

    'forum.user',
    'forum.userkyc',
    'forum.payment',
    'forum.user.admin',
    'forum.user.auth',

    'forum.category',
    'forum.category.admin',

    'forum.topic',
    'forum.topic.admin',
    'forum.topic.favorite',
    'forum.topic.moderate',
    'forum.topic.notification',
    'forum.topic.poll',  # todo: remove in Spirit v0.6
    'forum.topic.private',
    'forum.topic.unread',

    'forum.comment',
    'forum.comment.bookmark',
    'forum.comment.flag',
    'forum.comment.flag.admin',
    'forum.comment.history',
    'forum.comment.like',
    'forum.comment.poll',
    'drf_spirit',
    'rest_framework_swagger',
    'fcm',
    'rangefilter',
    'import_export',
    'django_extensions',
    'jarvis',
    'tinymce',
    'chartjs',
    
    # 'forum.core.tests'
]

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
    'METHOD': 'oauth2',
    'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
    'SCOPE': ['email', 'public_profile', 'user_friends'],
    'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
    'INIT_PARAMS': {'cookie': True},
    'FIELDS': [
        'id',
        'email',
        'name',
        'first_name',
        'last_name',
        'verified',
        'locale',
        'timezone',
        'link',
        'gender',
        'updated_time',
    ],
    'EXCHANGE_TOKEN': True,
    'LOCALE_FUNC': lambda request: 'en_US',
    'VERIFIED_EMAIL': False,
    'VERSION': 'v2.12',
    },
     'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS =1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400 # 1 day in seconds
ACCOUNT_LOGOUT_REDIRECT_URL ='/'
LOGIN_REDIRECT_URL = '/accounts/email/' 
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS=False
SOCIALACCOUNT_ADAPTER = 'forum.topic.views.AutoConnectSocialAccount'
#ACCOUNT_ADAPTER = 'forum.topic.views.NoNewUsersAccountAdapter'
#ACCOUNT_ADAPTER = 'forum.topic.views.MyAccountAdapter'

# redirects to /accounts/profile by default 

# python manage.py createcachetable
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'spirit_cache',
    },
}

CACHES.update({
    'st_rate_limit': {
        'BACKEND': CACHES['default']['BACKEND'],
        'LOCATION': 'spirit_rl_cache',
        'TIMEOUT': None
    }
})

FCM_APIKEY = "AIzaSyBMF3hxMosSjE-95inmJTcaR-rNEWn2zpQ"
FCM_DEVICE_MODEL = 'jarvis.FCMDevice'


AUTHENTICATION_BACKENDS = [
    'forum.user.auth.backends.UsernameAuthBackend',
    'forum.user.auth.backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',

]

LOGIN_URL = 'spirit:user:auth:login'
LOGIN_REDIRECT_URL = 'spirit:topic:discussion'

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'forum.core.middleware.XForwardedForMiddleware',
    'forum.user.middleware.TimezoneMiddleware',
    'forum.user.middleware.LastIPMiddleware',
    'forum.user.middleware.LastSeenMiddleware',
    'forum.user.middleware.ActiveUserMiddleware',
    'forum.core.middleware.PrivateForumMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            PROJECT_PATH + '/' + ENV + '/templates',
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'context_processors.all_languages',
                'context_processors.site_base_url',
                'forum.topic.context_processors.site_base_url',
            ],
        },
    },
]

INSTALLED_APPS += [
    'djconfig',
]

MIDDLEWARE_CLASSES += [
    'djconfig.middleware.DjConfigMiddleware',
]

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'djconfig.context_processors.config',
]

# django-haystack

INSTALLED_APPS += [
    'haystack',
]

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/boloindya',                 # Assuming you created a core named 'tester' as described in installing search engines.
        'ADMIN_URL': 'http://127.0.0.1:8983/solr/admin/cores'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'boloindya',                 # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'boloindya',
        'PASSWORD': 'bng321',
        'HOST': 'localhost',                 # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',                      # Set to empty string for default.
    }
}

SECRET_KEY = 'qh^ag%eobze^uylgvt2of3#t(3wze)2!-s=@_@zuua1$56mu41'

TIME_ZONE = 'Asia/Kolkata'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

LANGUAGES = [
    ('en', _('English')),
    ('hi', _('Hindi')),
    ('ta', _('Tamil')),
    ('te', _('Telgu')),
    ('bn', _('Bengali')),
    ('kn', _('Kannada')),
    ('ml', _('Malayalam')),
    ('mr', _('Marathi')),

]
#('gu', _('Gujarati')) 
LANGUAGES_WITH_ID = {
    'en' : '1',
    'hi' : '2',
    'ta' : '3',
    'te' : '4',
    'bn' : '5',
    'kn' : '6',
    'ml' : '7',
    'gu' : '8',
    'mr' : '9' 
}

LANGUAGE_CODE = 'en-us'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, ENV, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'
MEDIA_UPLOAD_DOC_PATH = 'media/documents/'
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, ENV, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # os.path.join(PROJECT_PATH, ENV, 'static'),
    # os.path.join(PROJECT_PATH, ENV, 'schedule', 'static'),
)

MEDIA_UPLOAD_PATH = os.path.join(PROJECT_PATH, ENV, 'media','media_upload')
TEMP_UPLOAD_FILE_PATH = os.path.join(PROJECT_PATH, ENV, 'media','tmp')

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
   'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SOCIALACCOUNT_QUERY_EMAIL=ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_EMAIL_REQUIRED=ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_STORE_TOKENS=False


# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.googlemail.com'
EMAIL_HOST_USER = 'support@careeranna.com'
EMAIL_HOST_PASSWORD = '$upp0rt@30!1'
EMAIL_PORT = 587

EMAIL_SENDER = EMAIL_HOST_USER
EMAIL_RECEIVERS = ['ankit@careeranna.com']

COMMENTS_PER_PAGE = 30
TOPICS_PER_PAGE = 30

TWO_FACTOR_SMS_API_KEY = "06a80ab1-6806-11e9-90e4-0200cd936042"
TWO_FACTOR_SMS_TEMPLATE = "BoloIndyaOTP" 

#### Rest Framework Settings ###
import datetime
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication',],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 15
}
# JWT_AUTH = {
#     # how long the original token is valid for
#     'JWT_EXPIRATION_DELTA': datetime.timedelta(days=90),
#     # allow refreshing of tokens
#     'JWT_ALLOW_REFRESH': True,
#     # this is the maximum time AFTER the token was issued that
#     # it can be refreshed.  exprired tokens can't be refreshed.
#     'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=90),
# }
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=999),
}
#### Rest Framework Settings ###
#import django
#django.setup()

#####Bolo Indya Prod ######
#### S3 bucket #####
BOLOINDYA_AWS_ACCESS_KEY_ID = 'AKIAZNK4CM5CV76OQQHQ'
BOLOINDYA_AWS_SECRET_ACCESS_KEY = '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'
BOLOINDYA_AWS_BUCKET_NAME = 'boloindyapp-prod'

#### Transcoder settings #####
BOLOINDYA_PIPELINE_ID_TS = '1545987947390-hpo4hx'
BOLOINDYA_AWS_ACCESS_KEY_ID_TS = 'AKIAZNK4CM5CW4W4VWP7'
BOLOINDYA_AWS_SECRET_ACCESS_KEY_TS = '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'
BOLOINDYA_AWS_BUCKET_NAME_TS = 'boloindya-et'
#### Transcoder settings #####

#####CareerAnna ######
#### S3 bucket #####
CAREERANNA_AWS_ACCESS_KEY_ID = 'AKIAZNK4CM5CV76OQQHQ'
CAREERANNA_AWS_SECRET_ACCESS_KEY = '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'
CAREERANNA_AWS_BUCKET_NAME = 'careeranna'

#### Transcoder settings #####
CAREERANNA_PIPELINE_ID_TS = '1545115329326-xs95pe'
CAREERANNA_AWS_ACCESS_KEY_ID_TS = 'AKIAZNK4CM5CW4W4VWP7'
CAREERANNA_AWS_SECRET_ACCESS_KEY_TS = 'Odl4xfZTJZM0mq89XtNXf95g2zY8NwRuhp5+zp87'
CAREERANNA_AWS_BUCKET_NAME_TS = 'elastictranscode.videos'
#### Transcoder settings #####

# The region of your bucket, more info:
# http://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region
REGION_HOST = 'us-east-1'

FCM_MAX_RECIPIENTS = 1000

PREDICTION_START_HOUR = 3

CAREERANNA_VIDEOFILE_UPDATE_URL = "https://www.careeranna.com/search/insertOrUpdateFreeVideo"
SITE_ID = 2

