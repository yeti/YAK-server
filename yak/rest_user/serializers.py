import base64
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
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
            validated_data["password"] = make_password(validated_data["password"])

        return super(AuthSerializerMixin, self).create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("username", None):
            validated_data["username"] = validated_data["username"].lower()
        if validated_data.get("email", None):
            validated_data["email"] = validated_data["email"].lower()
        if validated_data.get("password", None):
            validated_data["password"] = make_password(validated_data["password"])

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
        value = base64.decodestring(value)
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")
        return value


class LoginSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('client_id', 'client_secret')

    def get_client_id(self, obj):
        return obj.oauth2_provider_application.first().client_id

    def get_client_secret(self, obj):
        return obj.oauth2_provider_application.first().client_secret


class SignUpSerializer(AuthSerializerMixin, LoginSerializer):
    password = serializers.CharField(max_length=128, write_only=True, error_messages={'required': 'Password required'})
    username = serializers.CharField(
        error_messages={'required': 'Username required'},
        max_length=30,
        validators=[RegexValidator(), UniqueValidator(queryset=User.objects.all(), message="Username taken")])
    email = serializers.EmailField(
        allow_blank=True,
        allow_null=True,
        max_length=75,
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email address taken")])

    class Meta(LoginSerializer.Meta):
        fields = ('fullname', 'username', 'email', 'password', 'client_id', 'client_secret')


class UserSerializer(AuthSerializerMixin, YAKModelSerializer):

    def __new__(cls, *args, **kwargs):
        """
        Can't just inherit in the class definition due to lots of import issues
        """
        return yak_settings.USER_SERIALIZER(*args, **kwargs)


class PasswordConfirmSerializer(AuthSerializerMixin, serializers.Serializer):
    password = serializers.CharField(required=True, error_messages={'required': 'New password required'})
    confirm_password = serializers.CharField(required=True,
                                             error_messages={'required': 'New password must be confirmed'})

    def validate(self, attrs):
        # first password is decoded in the `validate_password` method
        if attrs['password'] != base64.decodestring(attrs['confirm_password']):
            raise serializers.ValidationError("Passwords did not match")
        return attrs


class PasswordChangeSerializer(PasswordConfirmSerializer):
    old_password = serializers.CharField(required=True, error_messages={'required': 'Old password required'})


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordSetSerializer(PasswordConfirmSerializer):
    uid = serializers.CharField()
    token = serializers.CharField()
