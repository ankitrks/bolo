# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q
from haystack import indexes
from .models import UserProfile


# class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):

#     text = indexes.CharField(document=True, use_template=True)
#     title = indexes.CharField(model_attr='title')
#     title_auto = indexes.EdgeNgramField(model_attr='title')
#     suggestions = indexes.FacetCharField()

#     def get_model(self):
#         return UserProfile

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

#     def prepare(self, obj):
#         prepared_data = super(UserProfileIndex, self).prepare(obj)
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


class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True )
    is_test_user = BooleanField()
    name = indexes.CharField(model_attr='name', indexed=True)
    slug = indexes.CharField(model_attr='slug', indexed=True)
    user = indexes.CharField(model_attr='user', indexed=True)
    vb_count = indexes.CharField(model_attr='vb_count', indexed=True)
    own_vb_view_count = indexes.CharField(model_attr='own_vb_view_count', indexed=True)
    follow_count = indexes.CharField(model_attr='follow_count', indexed=True)
    follower_count = indexes.CharField(model_attr='follower_count', indexed=True)
    language = indexes.CharField(model_attr='language', indexed=True)

    # Overridden
    def get_model(self):
        return UserProfile

    # Overridden
    def index_queryset(self, using=None):
        return (self.get_model().objects.all())

    # Overridden
    def build_queryset(self, using=None, start_date=None, end_date=None):
        """
        This specify what UserProfiles should be indexed,\
        based on the last time they were updated.

        :return: UserProfile QuerySet filtered by active\
        time and ordered by pk
        """
        lookup_UserProfile = {}
        lookup_subcategory = {}

        if start_date:
            lookup_UserProfile['reindex_at__gte'] = start_date

        if end_date:
            lookup_UserProfile['reindex_at__lte'] = end_date

        return (self.index_queryset(using=using)
                .filter(
                    Q(**lookup_UserProfile))
                .order_by('pk'))

    def prepare_is_test_user(self, obj):
        """
        Populate the ``is_test_user`` index field

        :param obj: UserProfile
        :return: whether the UserProfile is removed or not
        """
        return (obj.is_test_user)
