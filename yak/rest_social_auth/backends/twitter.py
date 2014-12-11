from social.backends.twitter import TwitterOAuth
from yak.rest_social_auth.backends.base import ExtraDataAbstractMixin


class Twitter(ExtraDataAbstractMixin, TwitterOAuth):
    @staticmethod
    def save_extra_data(response, user):
        return

    @staticmethod
    def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
        return response['profile_image_url']