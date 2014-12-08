from rest_framework import serializers
from yak.rest_notifications.models import NotificationSetting, Notification, PushwooshToken
from yak.rest_user.serializers import UserSerializer

__author__ = 'baylee'


class PushwooshTokenSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    hwid = serializers.CharField(write_only=True)
    language = serializers.CharField(write_only=True)

    class Meta:
        model = PushwooshToken


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = ('id', 'notification_type', 'allow_push', 'allow_email')
        read_only_fields = ('id', 'notification_type')


class NotificationSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    reporter = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('created', 'name', 'message', 'reporter')

    def get_message(self, obj):
        return obj.message(Notification.PUSH)
