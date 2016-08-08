import rest_framework
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.decorators import detail_route, list_route
from yak.rest_core.utils import get_package_version
from yak.rest_social_network.models import Tag, Comment, Follow, Flag, Share, Like
from yak.rest_social_network.serializers import TagSerializer, CommentSerializer, FollowSerializer, FlagSerializer, \
    ShareSerializer, LikeSerializer
from yak.rest_user.serializers import UserSerializer
from yak.rest_user.views import UserViewSet
from django.contrib.auth import get_user_model


User = get_user_model()
drf_version = get_package_version(rest_framework)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_fields = ('content_type', 'object_id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @list_route(methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            # [self.perform_create(obj) for obj in serializer.validated_data]
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShareViewSet(viewsets.ModelViewSet):
    queryset = Share.objects.all()
    serializer_class = ShareSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class FlagView(generics.CreateAPIView):
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer

    def pre_save(self, obj):
        obj.user = self.request.user


class SocialUserViewSet(UserViewSet):
    serializer_class = UserSerializer

    @detail_route(methods=['get'])
    def following(self, request, pk):
        requested_user = User.objects.get(pk=pk)
        following = requested_user.user_following()

        if drf_version[0] >= 3 and drf_version[1] < 1:
            result_page = self.paginate_queryset(following)
        else:
            paginator = FollowViewSet().paginator
            result_page = paginator.paginate_queryset(following, request)

        serializer = FollowSerializer(instance=result_page, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def followers(self, request, pk):
        requested_user = User.objects.get(pk=pk)
        followers = requested_user.user_followers()

        if drf_version[0] >= 3 and drf_version[1] < 1:
            result_page = self.paginate_queryset(followers)
        else:
            paginator = FollowViewSet().paginator
            result_page = paginator.paginate_queryset(followers, request)

        serializer = FollowSerializer(instance=result_page, many=True, context={'request': request})
        return Response(serializer.data)
