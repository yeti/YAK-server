from django.db import models
from yak.rest_core.models import CoreModel


class SocialProvider(CoreModel):
    """
    Used as a relation on User model so users can pick certain default providers to share posts on
    TODO: Do we still need this? / I think FB recommends explicit sharing, not default sharing
    """
    name = models.CharField(max_length=20)
