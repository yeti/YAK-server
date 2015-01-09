from django.contrib.auth import get_user_model
from rest_framework import serializers
from yak.rest_user.serializers import SignUpSerializer

User = get_user_model()


class SocialSignUpSerializer(SignUpSerializer):
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('fullname', 'username', 'email', 'password', 'client_id', 'client_secret')
        write_only_fields = ('access_token', 'access_token_secret')
        read_only_fields = ('fullname', 'username', 'email', 'client_id', 'client_secret')