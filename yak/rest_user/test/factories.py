from django.utils.timezone import now
import factory
import datetime
from oauth2_provider.models import AccessToken
from django.contrib.auth import get_user_model


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
        AccessToken.objects.create(user=user,
                                   application=user.application_set.first(),
                                   token='token{}'.format(user.id),
                                   expires=now() + datetime.timedelta(days=1)
        )
        return user
