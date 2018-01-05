import factory
import datetime
from test_project.test_app.models import Post
from django.utils.timezone import now
from oauth2_provider.models import AccessToken, Application
from django.contrib.auth import get_user_model
from yak.rest_social_network.models import Comment


User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'person{0}@example.com'.format(n))
    username = factory.Sequence(lambda n: 'person{0}'.format(n))

    @staticmethod
    def get_test_application():
        application, created = Application.objects.get_or_create(
            client_type=Application.CLIENT_PUBLIC,
            name="Test App",
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        return application

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = super(UserFactory, cls)._create(model_class, *args, **kwargs)
        application = cls.get_test_application()
        AccessToken.objects.create(
            user=user,
            application=application,
            token='token{}'.format(user.id),
            expires=now() + datetime.timedelta(days=1)
        )
        return user


class PostFactory(factory.DjangoModelFactory):
    class Meta:
        model = Post

    user = factory.SubFactory(UserFactory)
    title = "Factory-farmed post"
    description = "I love Yeti App Kit!"


class CommentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Comment

    user = factory.SubFactory(UserFactory)
    description = "This is not, the greatest comment in the world."
