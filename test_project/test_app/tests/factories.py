import factory
from yak.rest_user.test.factories import UserFactory
from yak.settings import yak_settings


Post = yak_settings.SOCIAL_MODEL


class PostFactory(factory.DjangoModelFactory):
    class Meta:
        model = Post

    user = factory.SubFactory(UserFactory)
    title = "Factory-farmed post"
    description = "I love Yeti App Kit!"