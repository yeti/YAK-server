from yak.rest_user.serializers import LoginSerializer


class SocialSignUpSerializer(LoginSerializer):
    class Meta(LoginSerializer.Meta):
        fields = ('email', 'username', 'client_id', 'client_secret')
        read_only_fields = ('username',)
