from django.conf import settings
from django.contrib.auth import get_user_model
import facebook
from rest_framework import status, generics
from rest_framework.decorators import detail_route
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from social.apps.django_app import load_strategy
from social.apps.django_app.default.models import UserSocialAuth
from social.apps.django_app.utils import load_backend
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from twython import Twython
from yak.rest_social_auth.serializers import SocialSignUpSerializer
from yak.rest_social_auth.utils import post_social_media
from yak.rest_user.serializers import UserSerializer
from yak.rest_user.views import SignUp


User = get_user_model()


class SocialSignUp(SignUp):
    serializer_class = SocialSignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            provider = request.data['provider']

            # If this request was made with an authenticated user, try to associate this social account with it
            user = request.user if not request.user.is_anonymous() else None

            strategy = load_strategy(request)
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)

            if isinstance(backend, BaseOAuth1):
                token = {
                    'oauth_token': request.data['access_token'],
                    'oauth_token_secret': request.data['access_token_secret'],
                }
            elif isinstance(backend, BaseOAuth2):
                token = request.data['access_token']

            user = backend.do_auth(token, user=user)
            serializer.object = user

            if user and user.is_active:
                self.post_save(serializer.object, created=True)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"errors": "Error with social authentication"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialShareMixin(object):

    @detail_route(methods=['post'])
    def social_share(self, request, pk):
        try:
            user_social_auth = UserSocialAuth.objects.get(user=request.user, provider=request.data['provider'])
            social_obj = self.get_object()
            post_social_media(user_social_auth, social_obj)
            return Response({'status': 'success'})
        except UserSocialAuth.DoesNotExist:
            raise AuthenticationFailed("User is not authenticated with {}".format(request.data['provider']))


class SocialFriends(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        provider = self.request.query_params.get('provider', None)
        if provider == 'facebook':
            # TODO: what does it look like when a user has more than one social auth for a provider? Is this a thing
            # that can happen? How does it affect SocialShareMixin? The first one is the oldest--do we actually want
            # the last one?
            user_social_auth = self.request.user.social_auth.filter(provider='facebook').first()
            graph = facebook.GraphAPI(user_social_auth.extra_data['access_token'])
            facebook_friends = graph.request("v2.2/me/friends")["data"]
            friends = User.objects.filter(social_auth__provider='facebook',
                                          social_auth__uid__in=[user["id"] for user in facebook_friends])
            return friends
        elif provider == 'twitter':
            user_social_auth = self.request.user.social_auth.filter(provider='twitter').first()
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
        else:
            return Response({"errors": "{} is not a valid social provider".format(provider)},
                            status=status.HTTP_400_BAD_REQUEST)
