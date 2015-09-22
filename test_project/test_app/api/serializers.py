from django.contrib.auth import get_user_model
from rest_framework import serializers
from test_project.test_app.models import Post
from yak.rest_core.serializers import YAKModelSerializer
from yak.rest_social_network.serializers import LikedMixin, FollowedMixin
from yak.rest_user.serializers import AuthSerializerMixin


User = get_user_model()


class ProjectUserSerializer(FollowedMixin, AuthSerializerMixin, YAKModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'fullname', 'thumbnail', 'original_photo', 'small_photo', 'large_photo',
                  'about', 'user_following_count', 'user_followers_count', 'follow_id')

    follow_id = serializers.SerializerMethodField()


class PostSerializer(YAKModelSerializer, LikedMixin):
    user = ProjectUserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    liked_id = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'user', 'title', 'description', 'thumbnail', 'liked_id')


class ArticleSerializer(YAKModelSerializer, LikedMixin):
    liked_id = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'thumbnail', 'liked_id')
