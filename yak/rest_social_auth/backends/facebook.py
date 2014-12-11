from social.backends.facebook import Facebook2OAuth2
from yak.rest_social_auth.backends.base import ExtraDataAbstractMixin


class Facebook(ExtraDataAbstractMixin, Facebook2OAuth2):
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
        image_url = "https://graph.facebook.com/{}/picture?type=large".format(uid)
        return image_url