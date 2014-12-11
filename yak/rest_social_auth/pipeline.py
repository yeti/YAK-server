from social.apps.django_app.default.models import UserSocialAuth
import urllib
from urllib2 import URLError
from django.core.files import File
from yak.rest_core.utils import retry_cloudfiles


def social_auth_user(strategy, uid, user=None, *args, **kwargs):
    """
    Allows user to create a new account and associate a social account,
    even if that social account is already connected to a different
    user. It effectively 'steals' the social association from the
    existing user. This can be a useful option during the testing phase
    of a project.

    Return UserSocialAuth account for backend/uid pair or None if it
    doesn't exist.

    Delete UserSocialAuth if UserSocialAuth entry belongs to another
    user.
    """
    social = UserSocialAuth.get_social_auth(kwargs['backend'].name, uid)
    if social:
        if user and social.user != user:
            # Delete UserSocialAuth pairing so this account can now connect
            social.delete()
            social = None
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}


def save_extra_data(strategy, details, response, uid, user, social, *args, **kwargs):
    """Attempt to get extra information from facebook about the User"""

    if user is None:
        return

    try:  # Basically, check the backend is one of ours
        kwargs['backend'].save_extra_data(response, user)
    except AttributeError:
        pass


def save_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
    """Attempt to get a profile image for the User"""

    if user is None:
        return

    try:  # Basically, check the backend is one of ours
        image_url = kwargs['backend'].get_profile_image(strategy, details, response, uid, user, social, is_new=False,
                                                        *args,
                                                        **kwargs)
    except AttributeError:
        return

    if image_url:
        try:
            result = urllib.urlretrieve(image_url)

            def save_image(user, uid, result):
                user.original_photo.save("{}.jpg".format(uid), File(open(result[0])))
                user.save(update_fields=['original_photo'])

            retry_cloudfiles(save_image, user, uid, result)
        except URLError:
            pass
