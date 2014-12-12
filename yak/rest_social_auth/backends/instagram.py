from social.backends.instagram import InstagramOAuth2
from yak.rest_social_auth.backends.base import ExtraDataAbstractMixin


class Instagram(ExtraDataAbstractMixin, InstagramOAuth2):
    @staticmethod
    def save_extra_data(response, user):
        if response['data']['bio']:
            user.about = response['bio']

        user.save()

    @staticmethod
    def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
        image_url = response['data']['profile_picture']
        return image_url