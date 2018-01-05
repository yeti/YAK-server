from django.contrib.auth import get_user_model
from rest_framework import serializers
from yak.rest_social_network.models import Tag, Comment, Follow, Flag, Share, Like
from yak.rest_user.serializers import UserSerializer


User = get_user_model()


class LikedMixin(object):
    def get_liked_id(self, obj):
        request = self.context['request']
        if request.user.is_authenticated:
            try:
                content_type = self.get_content_type(obj)
                return Like.objects.get(content_type=content_type, user=request.user, object_id=obj.pk).pk
            except Like.DoesNotExist:
                pass
        return None


class FollowedMixin(object):
    def get_follow_id(self, obj):
        # Indicate whether or not the logged in user is following a given object (e.g., another user)
        # Provide the id of the follow object so it can be deleted to unfollow the object
        if self.context['request'].user.is_authenticated:
            try:
                content_type = self.get_content_type(obj)
                return self.context['request'].user.following.get(content_type=content_type, object_id=obj.pk).pk
            except Follow.DoesNotExist:
                pass
        return None


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'id')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ('related_tags',)

    def __init__(self, *args, **kwargs):
        """
        The `user` field is added here to help with recursive import issues mentioned in rest_user.serializers
        """
        super(CommentSerializer, self).__init__(*args, **kwargs)
        self.fields["user"] = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True, source="user")
    following = serializers.SerializerMethodField('get_user_follow')

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created', 'content_type', 'object_id']

    def get_user_follow(self, obj):
        user = User.objects.get(pk=obj.object_id)
        serializer = UserSerializer(user, context={'request': self.context.get('request')})
        return serializer.data


class ShareSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Share
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Like
        fields = '__all__'


class FlagSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Flag
        fields = '__all__'
