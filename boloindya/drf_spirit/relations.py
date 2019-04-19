from collections import OrderedDict
from rest_framework.relations import SlugRelatedField


class PresentableSlugRelatedField(SlugRelatedField):
    """
    Based on :
    https://github.com/Hipo/drf-extra-fields/blob/462212c06f2f10113d7ab98a74c3aecc3deb26df/drf_extra_fields/relations.py
    Apache License 2.0
    Override SlugRelatedField to represent serializer data instead of a slug field of the object.
    """

    def __init__(self, slug_field, **kwargs):
        self.presentation_serializer = kwargs.pop('presentation_serializer', None)
        assert self.presentation_serializer is not None, (
            'PresentableSlugRelatedField must provide a `presentation_serializer` argument'
        )
        super(PresentableSlugRelatedField, self).__init__(slug_field, **kwargs)

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([(getattr(item, self.slug_field), self.display_value(item))
                            for item in queryset])

    def to_representation(self, data):
        return self.presentation_serializer(data, context=self.context).data
