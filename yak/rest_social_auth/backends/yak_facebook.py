from django.contrib.auth import get_user_model
import facebook
from social.backends.facebook import Facebook2OAuth2
from yak.rest_social_auth.backends.base import ExtraDataAbstractMixin, ExtraActionsAbstractMixin
from yak.settings import yak_settings

User = get_user_model()


class Facebook(ExtraActionsAbstractMixin, ExtraDataAbstractMixin, Facebook2OAuth2):
    @staticmethod
    def save_extra_data(response, user):
        if 'email' in response:
            user.email = response['email']

        # TODO: better placement of Location model. What do we do with Twitter or other locations?
        # if 'location' in response:
        #     if not user.location:
        #         Location.objects.create(name=response["location"]["name"], facebook_id=response["location"]["id"])
        #     else:
        #         location = user.location
        #         location.name = response['location']['name']
        #         location.facebook_id = response['location']['id']

        if 'bio' in response:
            user.about = response['bio']

        user.save()

    @staticmethod
    def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
        image_url = "https://graph.facebook.com/{}/picture?width=1000&height=1000".format(uid)
        return image_url

    @staticmethod
    def post(user_social_auth, social_obj):
        graph = facebook.GraphAPI(user_social_auth.extra_data['access_token'])

        if yak_settings.USE_FACEBOOK_OG:
            og_info = social_obj.facebook_og_info()
            action_name = "{}:{}".format(yak_settings.FACEBOOK_OG_NAMESPACE, og_info['action'])
            object_name = '{}'.format(og_info['object'])
            object_url = '{}'.format(og_info['url'])
            graph.put_object("me", action_name, **{object_name: object_url})
        else:
            message = social_obj.create_social_message(user_social_auth.provider)
            link = social_obj.url()
            graph.put_object("me", "feed", message=message, link=link)

    @staticmethod
    def get_friends(user_social_auth):
        graph = facebook.GraphAPI(user_social_auth.extra_data['access_token'])
        facebook_friends = graph.get_connections("me", "friends")
        friends = User.objects.filter(social_auth__provider='facebook',
                                      social_auth__uid__in=[user["id"] for user in facebook_friends['data']])
        return friends
