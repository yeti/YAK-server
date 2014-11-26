"""
Modeled after Django REST Framework settings

This module provides the `api_setting` object, that is used to access
YAK settings, checking for user settings first, then falling
back to the defaults.
"""
from __future__ import unicode_literals
from django.conf import settings
from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, 'YAK', None)

DEFAULTS = {
    'USER_APP_LABEL': 'test_app',
    'USER_MODEL': 'user',
    'USER_SERIALIZER': "test_app.api.serializers.ProjectUserSerializer",
    'API_SCHEMA': 'api-schema-1.0.json',
    'SOCIAL_MODEL': "test_app.models.Post",
    'SOCIAL_MODEL_FACTORY': "test_app.tests.factories.PostFactory",
    'SOCIAL_FRIEND_ACTIONS': (
        (0, 'follow', 'is following'),
        (1, 'like', 'favorited a post'),
        (2, 'reply', 'replied to a post')
    ),
    'NOTIFICATION_TYPES': (
        (0, 'follow', 'follow.html'),
        (1, 'like', 'like.html'),
        (2, 'comment', 'comment.html'),
        (3, 'mention', 'mention.html'),
        (4, 'share', 'share.html'),
    ),
    'EMAIL_NOTIFICATION_SUBJECT': 'Test Project Notification',
    'PUSHWOOSH_AUTH_TOKEN': "",
    'PUSHWOOSH_APP_CODE': "",
    'SOCIAL_SHARE_DELAY': 60,
    'USE_FACEBOOK_OG': False,
    'FACEBOOK_OG_NAMESPACE': "",
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    "USER_SERIALIZER",
    "SOCIAL_MODEL",
    "SOCIAL_MODEL_FACTORY",
)

yak_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)