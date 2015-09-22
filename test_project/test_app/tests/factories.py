import factory
import datetime
import oauth2_provider
from test_project.test_app.models import Post
from django.utils.timezone import now
from oauth2_provider.models import AccessToken
from django.contrib.auth import get_user_model
from yak.rest_social_network.models import Comment


User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'person{0}@example.com'.format(n))
    username = factory.Sequence(lambda n: 'person{0}'.format(n))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = super(UserFactory, cls)._create(model_class, *args, **kwargs)
        # Force save for post_save signal to create auth client
        user.save()
        oauth_toolkit_version = [int(num) for num in oauth2_provider.__version__.split('.')]
        # If we're using version 0.8.0 or higher
        if oauth_toolkit_version[0] >= 0 and oauth_toolkit_version[1] >= 8:
            AccessToken.objects.create(user=user,
                                       application=user.oauth2_provider_application.first(),
                                       token='token{}'.format(user.id),
                                       expires=now() + datetime.timedelta(days=1)
                                       )
        else:
            AccessToken.objects.create(user=user,
                                       application=user.application_set.first(),
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
