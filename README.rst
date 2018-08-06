.. image:: https://travis-ci.org/yeti/YAK-server.svg?branch=master 
    :target: https://travis-ci.org/yeti/YAK-server

.. image:: https://readthedocs.org/projects/yak-server/badge/?version=stable
    :target: https://yak-server.readthedocs.io/en/latest/index.html

YAK-server
=======================

Server-side implementation of Yeti App Kit built on Django. Includes:

- ``rest_core``: Base features to support other REST libraries, including test cases and permissions.
- ``rest_user``: User relevant API resources for creating and authenticating users with OAuth2.0
- ``rest_social_auth``: Implements social sign up with python social auth
- ``rest_social_network``: Models and APIs for social functionality (hashtags, likes, following, comments, @mentions, flagging / reporting)
- ``rest_notifications``: Models and APIs for notifications. Includes support for push notifications with Pushwoosh.

Find documentation on `Read the Docs <https://yak-server.readthedocs.io/en/latest/index.html>`_.

View the `Test Project <https://github.com/yeti/YAK-server/tree/master/test_project>`_ associated with this library for examples.