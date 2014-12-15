from celery.task import task
from django.conf import settings
from social.backends.utils import get_backend


@task
def post_social_media(user_social_auth, social_obj):
    backend = get_backend(settings.AUTHENTICATION_BACKENDS, user_social_auth.provider)
    backend.post(user_social_auth, social_obj)
