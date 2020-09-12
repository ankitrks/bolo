from settings import *

HAYSTACK_CONNECTIONS = {
      'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'https://search-boloindya-aehdn5vbnfmnhacekjpr433e4a.ap-south-1.es.amazonaws.com',
            'INDEX_NAME': 'boloindya',
      },
}


DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'boloindya',                 # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'boloindya_prod',
        'PASSWORD': 'boloadmin3011',
        'HOST': 'localhost',                 # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5435',                      # Set to empty string for default.
    },
    'read': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'boloindya',                 # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'boloindya_prod',
        'PASSWORD': 'boloadmin3011',
        'HOST': 'localhost',                 # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5435',                      # Set to empty string for default.
    }
}