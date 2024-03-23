# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q
from haystack import indexes
from .models import Topic,TongueTwister


# class TopicIndex(indexes.SearchIndex, indexes.Indexable):

#     text = indexes.CharField(document=True, use_template=True)
#     title = indexes.CharField(model_attr='title')
#     title_auto = indexes.EdgeNgramField(model_attr='title')
#     suggestions = indexes.FacetCharField()

#     def get_model(self):
#         return Topic

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

#     def prepare(self, obj):
#         prepared_data = super(TopicIndex, self).prepare(obj)
#         prepared_data['suggestions'] = prepared_data['text']
#         return prepared_data




# See: django-haystack issue #801
# convert() from search-engine
# stored value to python value,
# so it only matters when using
# search_result.get_stored_fields()
class BooleanField(indexes.BooleanField):

    bool_map = {'true': True, 'false': False}

    def convert(self, value):
        if value is None:
            return None

        if value in self.bool_map:
            return self.bool_map[value]

        return bool(value)


class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True )
    is_removed = BooleanField()
    title = indexes.EdgeNgramField(model_attr='title', indexed=True)
    slug = indexes.EdgeNgramField(model_attr='slug', indexed=True)
    language_id = indexes.CharField(model_attr='language_id', indexed=True)
    likes_count = indexes.IntegerField(model_attr='likes_count', indexed=True)
    total_share_count = indexes.IntegerField(model_attr='total_share_count', indexed=True)
    view_count = indexes.IntegerField(model_attr='view_count', indexed=True)
    vb_playtime = indexes.IntegerField(model_attr='vb_playtime', indexed=True)
    last_active = indexes.DateTimeField(model_attr='last_active', indexed=False)
    suggestions = indexes.FacetCharField()

    def prepare(self, obj):
        prepared_data = super(TopicIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    # Overridden
    def get_model(self):
        return Topic

    # Overridden
    def index_queryset(self, using=None):
        return (self.get_model().objects.filter(is_vb=True))

    # Overridden
    def build_queryset(self, using=None, start_date=None, end_date=None):
        """
        This specify what topics should be indexed,\
        based on the last time they were updated.

        :return: Topic QuerySet filtered by active\
        time and ordered by pk
        """
        lookup_topic = {}
        lookup_subcategory = {}

        if start_date:
            lookup_topic['date__gte'] = start_date

        if end_date:
            lookup_topic['date__lte'] = end_date

        return (self.index_queryset(using=using)
                .filter(
                    Q(**lookup_topic))
                .order_by('-pk'))

    def prepare_is_removed(self, obj):
        """
        Populate the ``is_removed`` index field

        :param obj: Topic
        :return: whether the topic is removed or not
        """
        return (obj.is_removed)

class TongueTwisterIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True )
    hash_tag = indexes.EdgeNgramField(model_attr='hash_tag', indexed=True)
    hash_counter = indexes.IntegerField(model_attr='hash_counter', indexed=True)
    total_views = indexes.IntegerField(model_attr='total_views', indexed=True)
    suggestions = indexes.FacetCharField()

    def prepare(self, obj):
        prepared_data = super(TongueTwisterIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    def get_model(self):
        return TongueTwister

    def index_queryset(self, using=None):
        return (self.get_model().objects.all())
