=================
``yak.rest_core``
=================

The ``rest_core`` module holds some utility classes that are used by the other yak-server modules, or which you may
find useful in development.

``rest_core`` also holds custom test cases that allow you to test your API endpoints against a contract. You do this by
describing your API endpoints in a JSON schema. Then, the custom test cases allow you to easily test that your endpoints
accept requests and format responses the way you have described. The test cases also provide helper functionality around
making authenticated requests, sending up files, etc.

The format of the JSON schema is compatible with the `signals library <https://github.com/yeti/signals>`_, though there
is no dependency between yak-server and ``signals``. See yak-server's `test project <https://github.com/yeti/YAK-server/blob/master/test_project/api-schema-1.0.json>`_
for an example schema file.

To use yak's schema testing features, add your yak settings to ``settings.py``.::

    YAK = {
        'API_SCHEMA': 'api-schema-1.0.json',
    }

Where ``API_SCHEMA`` is the path to your API schema file.
