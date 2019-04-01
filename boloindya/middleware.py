# -*- coding: utf-8 -*-

from forum.core.middleware import XForwardedForMiddleware, PrivateForumMiddleware
from forum.user.middleware import TimezoneMiddleware, LastIPMiddleware,\
    LastSeenMiddleware, ActiveUserMiddleware

# TODO: remove in Spirit 0.5


__all__ = [
    'XForwardedForMiddleware',
    'PrivateForumMiddleware',
    'TimezoneMiddleware',
    'LastIPMiddleware',
    'LastSeenMiddleware',
    'ActiveUserMiddleware'
]