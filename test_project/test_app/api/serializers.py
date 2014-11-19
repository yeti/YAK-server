from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_core.serializers import BaseModelSerializer
from rest_user.serializers import AuthSerializerMixin


User = get_user_model()


class ProjectUserSerializer(AuthSerializerMixin, BaseModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'fullname', 'thumbnail', 'original_photo', 'small_photo', 'large_photo',
                  'about', 'user_following_count', 'user_followers_count')

    user_following_count = serializers.Field(source='user_following_count')
    user_followers_count = serializers.Field(source='user_followers_count')
