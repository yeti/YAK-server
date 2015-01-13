from rest_framework import serializers
from yak.rest_core.fields import GenericHyperlinkedRelatedField
from yak.rest_notifications.models import NotificationSetting, Notification, PushwooshToken, NotificationType
from yak.rest_user.serializers import UserSerializer

__author__ = 'baylee'


class PushwooshTokenSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    hwid = serializers.CharField(write_only=True)
    language = serializers.CharField(write_only=True)

    class Meta:
        model = PushwooshToken


class NotificationTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationType
        fields = ('id', 'name', 'description', 'is_active')


class NotificationSettingSerializer(serializers.ModelSerializer):
    notification_type = NotificationTypeSerializer(read_only=True)

    class Meta:
        model = NotificationSetting
        fields = ('id', 'notification_type', 'allow_push', 'allow_email')


class NotificationSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    reporter = UserSerializer(read_only=True)
    content_object = GenericHyperlinkedRelatedField(read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('created', 'name', 'message', 'reporter', 'content_object', 'thumbnail')

    def get_message(self, obj):
        return obj.message(Notification.PUSH)

    def get_thumbnail(self, obj):
        # `getattr` works strangely with file fields
        if getattr(obj.content_object, "thumbnail", None):
            return obj.content_object.thumbnail
        else:
            return None
