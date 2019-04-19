from rest_framework.serializers import ReadOnlyField
from django.conf import settings


class UserReadOnlyField(ReadOnlyField):
    """Return user pk or slug depends on settings"""

    def to_representation(self, value):
        # If *SLUG_FIELD is provided in settings, we should return user slug
        # Otherwise return user pk
        USER_SLUG_FIELD = None
        drf_spirit_setting = getattr(settings, 'DRF_SPIRIT', None)
        if drf_spirit_setting:
            USER_SLUG_FIELD = drf_spirit_setting.get('USER_SLUG_FIELD')

        if USER_SLUG_FIELD:
            return getattr(value, USER_SLUG_FIELD)
        else:
            return getattr(value, 'pk')
