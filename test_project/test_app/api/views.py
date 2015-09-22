from rest_framework import viewsets
from test_project.test_app.models import Post, Article
from yak.rest_social_auth.views import SocialShareMixin
from yak.rest_social_network.views import SocialUserViewSet
from test_project.test_app.api.serializers import ProjectUserSerializer, PostSerializer, ArticleSerializer


class ProjectUserViewSet(SocialUserViewSet):
    serializer_class = ProjectUserSerializer


class PostViewSet(viewsets.ModelViewSet, SocialShareMixin):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
