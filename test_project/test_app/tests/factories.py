import factory
from yak.rest_social.utils import get_social_model
from yak.rest_user.test.factories import UserFactory


Post = get_social_model()


class PostFactory(factory.DjangoModelFactory):
    class Meta:
        model = Post

    user = factory.SubFactory(UserFactory)
    title = "Factory-farmed post"
    description = "I love Yeti App Kit!"