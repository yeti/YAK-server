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
from social.backends.utils import get_backend
from twython import Twython
from yak.rest_social_auth.serializers import SocialSignUpSerializer
from yak.rest_social_auth.utils import post_social_media
from yak.rest_user.serializers import UserSerializer
from yak.rest_user.views import SignUp


User = get_user_model()


class SocialSignUp(SignUp):
    serializer_class = SocialSignUpSerializer

    def create(self, request, *args, **kwargs):
        """
        Override `create` instead of `perform_create` to access request
        request is necessary for `load_strategy`
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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

        if user and user.is_active:
            # if the access token was set to an empty string, then save the access token from the request
            auth_created = user.social_auth.get(provider=provider)
            if not auth_created.extra_data['access_token']:
                auth_created.extra_data['access_token'] = token
                auth_created.save()

            # Set instance since we are not calling `serializer.save()`
            serializer.instance = user
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"errors": "Error with social authentication"}, status=status.HTTP_400_BAD_REQUEST)


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
        # TODO: what does it look like when a user has more than one social auth for a provider? Is this a thing
        # that can happen? How does it affect SocialShareMixin? The first one is the oldest--do we actually want
        # the last one?
        try:
            user_social_auth = self.request.user.social_auth.filter(provider=provider).first()
            backend = get_backend(settings.AUTHENTICATION_BACKENDS, provider)
            friends = backend.get_friends(user_social_auth)
            return friends
        except UserSocialAuth.DoesNotExist:
            raise AuthenticationFailed("User is not authenticated with {}".format(provider))
