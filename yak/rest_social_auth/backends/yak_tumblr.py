from social_core.backends.tumblr import TumblrOAuth
from yak.rest_social_auth.backends.base import ExtraDataAbstractMixin, ExtraActionsAbstractMixin


class Tumblr(ExtraActionsAbstractMixin, ExtraDataAbstractMixin, TumblrOAuth):
    @staticmethod
    def save_extra_data(response, user):
        return

    @staticmethod
    def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
        return response['avatar_url']

    @staticmethod
    def post(user_social_auth, social_obj):
        return

    @staticmethod
    def get_friends(user_social_auth):
        return

    @staticmethod
    def get_posts(user_social_auth, last_updated_time):
        return
