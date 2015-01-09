import base64
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from yak.rest_core.serializers import YAKModelSerializer
from yak.settings import yak_settings

__author__ = 'baylee'


User = get_user_model()


class AuthSerializerMixin(object):
    def create(self, validated_data):
        if validated_data.get("username", None):
            validated_data["username"] = validated_data["username"].lower()
        if validated_data.get("email", None):
            validated_data["email"] = validated_data["email"].lower()
        if validated_data.get("password", None):
            validated_data["password"] = make_password(base64.decodestring(validated_data["password"]))

        return super(AuthSerializerMixin, self).create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("username", None):
            validated_data["username"] = validated_data["username"].lower()
        if validated_data.get("email", None):
            validated_data["email"] = validated_data["email"].lower()
        if validated_data.get("password", None):
            validated_data["password"] = make_password(base64.decodestring(validated_data["password"]))

        return super(AuthSerializerMixin, self).update(instance, validated_data)

    def validate_username(self, value):
        username = self.context['request'].user.username if self.context['request'].user.is_authenticated() else None
        if value and value != username and User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("That username is taken")
        return value

    def validate_email(self, value):
        email = self.context['request'].user.email if self.context['request'].user.is_authenticated() else None
        if value and value != email and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account already exists with that email")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")
        return value


class LoginSerializer(AuthSerializerMixin, serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('client_id', 'client_secret')

    def get_client_id(self, obj):
        return obj.application_set.first().client_id

    def get_client_secret(self, obj):
        return obj.application_set.first().client_secret


class SignUpSerializer(LoginSerializer):
    class Meta(LoginSerializer.Meta):
        fields = ('fullname', 'username', 'email', 'password', 'client_id', 'client_secret')
        write_only_fields = ('password',)


class UserSerializer(AuthSerializerMixin, YAKModelSerializer):

    def __new__(cls, *args, **kwargs):
        """
        Can't just inherit in the class definition due to lots of import issues
        """
        return yak_settings.USER_SERIALIZER(*args, **kwargs)


class PasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")
        return value
