from django.contrib.auth import get_user_model
from rest_framework import serializers
from yak.rest_user.serializers import LoginSerializer, AuthSerializerMixin

User = get_user_model()


class SocialSignUpSerializer(AuthSerializerMixin, LoginSerializer):
    fullname = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ('fullname', 'username', 'email', 'client_id', 'client_secret')
        write_only_fields = ('access_token', 'access_token_secret')
