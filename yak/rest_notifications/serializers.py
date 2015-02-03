from rest_framework import serializers
from yak.rest_notifications.models import NotificationSetting, Notification, PushwooshToken, NotificationType
from yak.rest_user.serializers import UserSerializer
from yak.settings import yak_settings

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
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('created', 'name', 'message', 'reporter', 'content_object')

    def get_message(self, obj):
        return obj.message(Notification.PUSH)

    def get_content_object(self, obj):
        serializer_class = yak_settings.SERIALIZER_MAPPING[type(obj.content_object)]
        serializer = serializer_class(instance=obj.content_object, context=self.context)
        return serializer.data

    def to_representation(self, instance):
        ret = super(NotificationSerializer, self).to_representation(instance)
        ret[instance.content_object._meta.model_name] = ret.pop('content_object')
        return ret
