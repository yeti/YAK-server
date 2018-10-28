"""
Modeled after Django REST Framework settings

This module provides the `api_setting` object, that is used to access
YAK settings, checking for user settings first, then falling
back to the defaults.
"""

from django.conf import settings
from django.utils import six
from rest_framework.settings import APISettings, import_from_string


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    elif isinstance(val, dict):
        return {import_from_string(k, setting_name): import_from_string(v, setting_name) for k, v in val.items()}
    return val


class YAKAPISettings(APISettings):
    """
    Adds the ability to import strings in dictionaries
    """

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        setattr(self, attr, val)
        return val


USER_SETTINGS = getattr(settings, 'YAK', None)

DEFAULTS = {
    'USER_APP_LABEL': 'test_app',
    'USER_MODEL': 'user',
    'USER_SERIALIZER': "test_app.api.serializers.UserSerializer",
    'API_SCHEMA': 'api-schema-1.0.json',
    'SOCIAL_MODEL': "test_app.models.Post",
    'ALLOW_EMAIL': True,
    'ALLOW_PUSH': True,
    'EMAIL_NOTIFICATION_SUBJECT': 'Test Project Notification',
    'PUSHWOOSH_AUTH_TOKEN': "",
    'PUSHWOOSH_APP_CODE': "",
    'PUSH_NOTIFICATION_HANDLER': "yak.rest_notifications.utils.send_pushwoosh_notification",
    'SOCIAL_SHARE_DELAY': 60,
    'USE_FACEBOOK_OG': False,
    'FACEBOOK_OG_NAMESPACE': "",
    'SERIALIZER_MAPPING': {},
    'FLAKE8_CONFIG': None,
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    "USER_SERIALIZER",
    "SOCIAL_MODEL",
    "SERIALIZER_MAPPING",
)

yak_settings = YAKAPISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
