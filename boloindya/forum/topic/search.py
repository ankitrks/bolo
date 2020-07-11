from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Document, Text, Boolean, Integer, Completion, analyzer, tokenizer
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
import models as models
# from .models import *
# from .models import Topic
connections.create_connection(hosts = ['localhost'])


my_analyzer = analyzer('my_analyzer',
    tokenizer=tokenizer('trigram', 'edge_ngram', min_gram=3, max_gram=20),
    filter=['lowercase']
)

class TopicIndex(Document):
    title = Text(analyzer=my_analyzer)
    slug = Text(analyzer=my_analyzer)
    is_removed = Boolean()
    language_id = Text()
    
    class Meta:
        index = 'topic-index'

class TongueTwisterIndex(Document):
    hash_tag = Text(analyzer=my_analyzer)
    # hash_tag = Text()
    
    class Meta:
        index = 'hashtag-index'


def bulk_indexing_topic():
    TopicIndex.init(index = 'topic-index')
    es = Elasticsearch()
    bulk(client=es, actions=(b.indexing() for b in models.Topic.objects.all().iterator()))

    

def bulk_indexing_tonguetwister():
    TongueTwisterIndex.init(index = 'hashtag-index')
    es = Elasticsearch()
    bulk(client=es, actions=(b.indexing() for b in models.TongueTwister.objects.all().iterator()))

