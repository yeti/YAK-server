import base64
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import viewsets, generics, status, views
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from yak.rest_core.permissions import IsOwnerOrReadOnly
from yak.rest_user.permissions import IsAuthenticatedOrCreate
from yak.rest_user.serializers import SignUpSerializer, LoginSerializer, PasswordChangeSerializer, UserSerializer, \
    PasswordResetSerializer, PasswordSetSerializer
from yak.rest_user.utils import reset_password

__author__ = 'baylee'


User = get_user_model()


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (IsAuthenticatedOrCreate,)


class Login(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    authentication_classes = (BasicAuthentication,)

    def get_queryset(self):
        queryset = super(Login, self).get_queryset()
        return queryset.filter(pk=self.request.user.pk)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    search_fields = ('username', 'fullname')

    @list_route(methods=["get"])
    def me(self, request):
        if request.user.is_authenticated():
            serializer = self.get_serializer(instance=request.user)
            return Response(serializer.data)
        else:
            return Response({"errors": "User is not authenticated"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        if not request.user.check_password(base64.decodestring(request.data['old_password'])):
            raise AuthenticationFailed("Old password was incorrect")
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.data['password'])
        request.user.save()
        return Response({'status': 'password set'})


class PasswordResetView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_password(request, serializer.data['email'])
        return Response({'status': 'password reset'})


class PasswordSetView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = PasswordSetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = urlsafe_base64_decode(serializer.data['uid'])
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, serializer.data['token']):
            user.set_password(serializer.data['password'])
            user.save()
            return Response(UserSerializer(instance=user, context={'request': request}).data)
        else:
            return Response({"errors": "Password reset unsuccessful"}, status=status.HTTP_400_BAD_REQUEST)
