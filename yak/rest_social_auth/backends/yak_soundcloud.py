import requests
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
        return response['avatar_url']

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
        track_url = "https://api.soundcloud.com/me/tracks.json"
        tracks = requests.get(track_url, params=params).json()

        playlist_url = "https://api.soundcloud.com/me/tracks.json"
        playlists = requests.get(playlist_url, params=params).json()
        return tracks + playlists
