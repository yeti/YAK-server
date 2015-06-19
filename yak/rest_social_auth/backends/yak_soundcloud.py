import requests
from simplejson import JSONDecodeError
from social.backends.soundcloud import SoundcloudOAuth2
from yak.rest_social_auth.backends.base import ExtraDataAbstractMixin, ExtraActionsAbstractMixin


class Soundcloud(ExtraActionsAbstractMixin, ExtraDataAbstractMixin, SoundcloudOAuth2):
    @staticmethod
    def save_extra_data(response, user):
        if response['description']:
            user.about = response['description']

        user.save()

    @staticmethod
    def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
        # Currently Soundcloud's SSL certificate causes a SSLError with requests and python 2.7
        return response['avatar_url'].replace('https', 'http')

    @staticmethod
    def post(user_social_auth, social_obj):
        return

    @staticmethod
    def get_friends(user_social_auth):
        return

    @staticmethod
    def get_posts(user_social_auth, last_updated_time):
        formatted_time = last_updated_time.replace(microsecond=0) if last_updated_time else None
        params = {
            'oauth_token': user_social_auth.extra_data['access_token'],
            'created_at[from]': formatted_time,
            'filter': 'public'
        }
        try:
            activity_url = "https://api.soundcloud.com/me/activities.json"
            activities = requests.get(activity_url, params=params).json()['collection']
        except JSONDecodeError:
            activities = []

        try:
            favorite_track_url = "https://api.soundcloud.com/me/favorites.json"
            favorite_tracks = requests.get(favorite_track_url, params=params).json()
        except JSONDecodeError:
            favorite_tracks = []

        return {'activities': activities, 'favorites': favorite_tracks}
