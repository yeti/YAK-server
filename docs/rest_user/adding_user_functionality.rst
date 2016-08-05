Adding user functionality
=========================

#. Create (or update) your user model to inherit from ``yak.rest_user.models.AbstractYeti``. Not strictly required,
but will make it easier if you decide to use ``yak.rest_user.backends.CaseInsensitiveBackend`` or
``rest_social_auth`` features.
#. Create a DRF serializer for your User model::

    from yak.rest_core.serializers import YAKModelSerializer
    from yak.rest_user.serializers import AuthSerializerMixin


    class ProjectUserSerializer(AuthSerializerMixin, YAKModelSerializer):
        class Meta:
            model = User
            fields = (...)

#. In ``settings.py``:

    * Add ``oauth2_provider`` and ``yak.rest_user`` to your ``INSTALLED_APPS``
    * Add your yak settings::

        YAK = {
            # name of the Django app which holds your user model
            'USER_APP_LABEL': 'test_app',

            # lowercased name of your user model
            'USER_MODEL': 'user',

            # path to a DRF serializer that represents your user model
            'USER_SERIALIZER': "test_app.api.serializers.ProjectUserSerializer",
        }

    * ``AUTH_USER_MODEL = "{}.{}".format(YAK['USER_APP_LABEL'], YAK['USER_MODEL'].capitalize())``
    * Add ``django-oauth-toolkit`` as an authentication backend for DRF::

        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'oauth2_provider.ext.rest_framework.OAuth2Authentication',
            )
        }

    * Add settings for ``django-oauth-toolkit``::

        OAUTH2_PROVIDER = {
            # this is the list of available scopes
            'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'}
        }

    * Optionally, add yak's ``CaseInsensitiveBackend`` as an authentication backend. ``CaseInsensitiveBackend`` allows
case-insensitive login with email or username::

        AUTHENTICATION_BACKENDS = (
            "yak.rest_user.backends.CaseInsensitiveBackend",
        )

#. ``python manage.py migrate``