from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Document, Text, Boolean, Integer, field, Completion, analyzer, tokenizer
from elasticsearch.helpers import bulk
from django.conf import settings
from elasticsearch import Elasticsearch
import models as models
connections.create_connection(hosts = [settings.ELASTIC_HOST])

my_analyzer = analyzer('my_analyzer',
    tokenizer=tokenizer('trigram', 'edge_ngram', min_gram=3, max_gram=20),
    filter=['lowercase']
)
class UserProfileIndex(Document):
    name = Text(analyzer=my_analyzer)
    is_test_user = Boolean()
    slug = Text(analyzer=my_analyzer)
    language = Text()

    class Meta:
        index = 'user-index'

def bulk_indexing_user():
    UserProfileIndex.init(index = 'user-index')
    es = Elasticsearch()
    bulk(client=es, actions=(b.indexing() for b in models.UserProfile.objects.all().iterator()))






