from yak.rest_social_network.views import SocialUserViewSet
from test_project.test_app.api.serializers import ProjectUserSerializer


class ProjectUserViewSet(SocialUserViewSet):
    serializer_class = ProjectUserSerializer

