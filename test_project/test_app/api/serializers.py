from django.contrib.auth import get_user_model
from rest_framework import serializers
from test_project.test_app.models import Post
from yak.rest_core.serializers import YAKModelSerializer
from yak.rest_social_network.serializers import LikedMixin
from yak.rest_user.serializers import AuthSerializerMixin


User = get_user_model()


class ProjectUserSerializer(AuthSerializerMixin, YAKModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'fullname', 'thumbnail', 'original_photo', 'small_photo', 'large_photo',
                  'about', 'user_following_count', 'user_followers_count', 'followed')

    followed = serializers.SerializerMethodField()

    def get_followed(self, obj):
        # Adding this helps verify that `request` is passed along in the context for serializers that use YAK's
        # `UserSerializer` nested
        followed = False
        request = self.context['request']

        if request.user.is_authenticated():
            user_content_type = self.get_content_type(obj)
            followed = request.user.following.filter(content_type=user_content_type, object_id=obj.pk).exists()

        return followed


class PostSerializer(YAKModelSerializer, LikedMixin):
    user = ProjectUserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    liked_id = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'user', 'title', 'description', 'thumbnail', 'liked_id')
