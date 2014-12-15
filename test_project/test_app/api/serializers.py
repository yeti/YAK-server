from django.contrib.auth import get_user_model
from test_project.test_app.models import Post
from yak.rest_core.serializers import YAKModelSerializer
from yak.rest_user.serializers import AuthSerializerMixin


User = get_user_model()


class ProjectUserSerializer(AuthSerializerMixin, YAKModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'fullname', 'thumbnail', 'original_photo', 'small_photo', 'large_photo',
                  'about', 'user_following_count', 'user_followers_count')


class PostSerializer(YAKModelSerializer):
    class Meta:
        model = Post
