from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_save
from django.utils.baseconv import base62
from yak.rest_core.models import resize_model_photos
from yak.rest_notifications.models import create_notification_settings
from yak.rest_social.models import AbstractSocialYeti, FollowableModel, BaseSocialModel, Like, Flag, Share, Tag, \
    Comment, relate_tags, mentions
from yak.rest_user.utils import create_auth_client


class User(AbstractSocialYeti):

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(User, self).save(force_insert, force_update, using, update_fields)
        resize_model_photos(self, force_update)

FollowableModel.register(User)
post_save.connect(create_auth_client, sender=User)
post_save.connect(create_notification_settings, sender=User)


class Post(BaseSocialModel):
    user = models.ForeignKey(User, related_name='posts')
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    TAG_FIELD = 'description'

    likes = GenericRelation(Like)
    flags = GenericRelation(Flag)
    shares = GenericRelation(Share)
    related_tags = models.ManyToManyField(Tag, null=True, blank=True)
    comments = GenericRelation(Comment)

    def likes_count(self):
        return self.likes.count()

    def comments_count(self):
        return self.comments.count()

    def identifier(self):
        return u"%s" % self.title

    def __unicode__(self):
        return u"{}".format(self.title) if self.title else "Untitled"

    def url(self):
        current_site = Site.objects.get_current()
        return "http://{0}/{1}/{2}/".format(current_site.domain, "post", base62.encode(self.pk))

    def facebook_og_info(self):
        return {'action': 'post', 'object': 'cut', 'url': self.url()}

    def create_social_message(self, provider):
        message = "{} published by {} on Test Project".format(self.title, self.user.username)

        # TODO: Sending of messages to post on social media is broken and convoluted at this point, need to refactor
        if provider == "twitter":
            return "%s" % message.encode('utf-8')
        else:
            return "%s %s" % (message.encode('utf-8'), self.url())

post_save.connect(relate_tags, sender=Post)
post_save.connect(mentions, sender=Post)
