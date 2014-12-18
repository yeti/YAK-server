from instagram import InstagramAPI, helper
from social.backends.instagram import InstagramOAuth2
from yak.rest_social_auth.backends.base import ExtraDataAbstractMixin, ExtraActionsAbstractMixin


class Instagram(ExtraActionsAbstractMixin, ExtraDataAbstractMixin, InstagramOAuth2):
    @staticmethod
    def save_extra_data(response, user):
        if response['data']['bio']:
            user.about = response['data']['bio']

        user.save()

    @staticmethod
    def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
        image_url = response['data']['profile_picture']
        return image_url

    @staticmethod
    def post(user_social_auth, social_obj):
        return

    @staticmethod
    def get_friends(user_social_auth):
        return

    @staticmethod
    def get_posts(user_social_auth, last_updated_time):
        api = InstagramAPI(access_token=user_social_auth.extra_data['access_token'])
        formatted_time = helper.datetime_to_timestamp(last_updated_time) if last_updated_time else None
        recent_media, next_ = api.user_recent_media(user_id=user_social_auth.uid, min_timestamp=formatted_time)
        return recent_media
