from django.conf import settings
from django.contrib.auth import get_user_model
from social.backends.twitter import TwitterOAuth
from twython import Twython
from yak.rest_social_auth.backends.base import ExtraDataAbstractMixin, ExtraActionsAbstractMixin
import re

User = get_user_model()


class Twitter(ExtraActionsAbstractMixin, ExtraDataAbstractMixin, TwitterOAuth):
    @staticmethod
    def save_extra_data(response, user):
        return

    @staticmethod
    def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
        # Remove the `_normal` affix to get the highest resolution / original photo from twitter
        return re.sub("_normal", "", response['profile_image_url'])

    @staticmethod
    def post(user_social_auth, social_obj):
        twitter = Twython(
            app_key=settings.SOCIAL_AUTH_TWITTER_KEY,
            app_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
            oauth_token=user_social_auth.tokens['oauth_token'],
            oauth_token_secret=user_social_auth.tokens['oauth_token_secret']
        )

        message = social_obj.create_social_message(user_social_auth.provider)
        link = social_obj.url()

        full_message_url = "{0} {1}".format(message, link)

        # 140 characters minus the length of the link minus the space minus 3 characters for the ellipsis
        message_trunc = 140 - len(link) - 1 - 3

        # Truncate the message if the message + url is over 140
        if len(full_message_url) > 140:
            safe_message = "{0}... {1}".format(message[:message_trunc], link)
        else:
            safe_message = full_message_url

        twitter.update_status(status=safe_message, wrap_links=True)

    @staticmethod
    def get_friends(user_social_auth):
        twitter = Twython(
            app_key=settings.SOCIAL_AUTH_TWITTER_KEY,
            app_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
            oauth_token=user_social_auth.tokens['oauth_token'],
            oauth_token_secret=user_social_auth.tokens['oauth_token_secret']
        )
        twitter_friends = twitter.get_friends_ids()["ids"]
        friends = User.objects.filter(social_auth__provider='twitter',
                                      social_auth__uid__in=twitter_friends)
        return friends
