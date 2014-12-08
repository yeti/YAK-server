from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.urlresolvers import reverse
from mock import MagicMock
from test_project.test_app.models import Post
from test_project.test_app.tests.factories import PostFactory, UserFactory
from yak.rest_core.test import SchemaTestCase
from yak.rest_notifications.models import create_notification, Notification, NotificationSetting
from yak.rest_notifications.utils import send_email_notification, send_push_notification, PushwooshClient
from yak.rest_social.models import Comment
from yak.settings import yak_settings


User = get_user_model()


class NotificationsTestCase(SchemaTestCase):
    def setUp(self):
        super(NotificationsTestCase, self).setUp()
        self.social_obj = PostFactory()
        self.receiver = UserFactory()
        self.reporter = UserFactory()
        PushwooshClient.invoke = MagicMock(return_value={"status_code": 200})

    def test_create_pushwoosh_token(self):
        url = reverse("pushwoosh_token")
        data = {
            "token": "ABC123",
            "language": "en",
            "hwid": "XYZ456"
        }
        self.assertSchemaPost(url, "$pushwooshTokenRequest", "$pushwooshTokenResponse", data, self.receiver)

        # Non-authenticated users can't create a token
        self.assertSchemaPost(url, "$pushwooshTokenRequest", "$pushwooshTokenResponse", data, None, unauthorized=True)

        # Can't create token if write-only language and hwid data is missing
        bad_data = {
            "token": "ABC123"
        }
        self.add_credentials(self.receiver)
        response = self.client.post(url, bad_data, format="json")
        self.assertHttpBadRequest(response)

    def test_email_notification_sent(self):
        message = "<h1>You have a notification!</h1>"
        send_email_notification(self.receiver, message)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, yak_settings.EMAIL_NOTIFICATION_SUBJECT)
        self.assertEqual(mail.outbox[0].body, "You have a notification!")
        self.assertEqual(mail.outbox[0].alternatives, [(message, "text/html")])

    def test_push_notification_sent(self):
        message = "<h1>You have a notification!</h1>"
        response = send_push_notification(self.receiver, message)
        self.assertEqual(response["status_code"], 200)

    def test_create_notification(self):
        notification_count = Notification.objects.count()

        # If receiver is the same as the reporter, a notification is not created
        create_notification(self.receiver, self.receiver, self.social_obj, yak_settings.NOTIFICATION_TYPES[0][0])
        self.assertEqual(notification_count, Notification.objects.count())

        # If the receiver and reporter are different, a notification is created
        create_notification(self.receiver, self.reporter, self.social_obj, yak_settings.NOTIFICATION_TYPES[0][0])
        self.assertEqual(notification_count + 1, Notification.objects.count())

    def test_correct_notification_type_sent(self):
        setting = NotificationSetting.objects.get(notification_type=yak_settings.NOTIFICATION_TYPES[0][0],
                                                  user=self.receiver)

        # An email and a push are sent if allow_email and allow_push are True
        create_notification(self.receiver, self.reporter, self.social_obj, yak_settings.NOTIFICATION_TYPES[0][0])
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(len(PushwooshClient.invoke.mock_calls), 1)

        # No new email is sent if allow_email is False
        setting.allow_email = False
        setting.save()
        create_notification(self.receiver, self.reporter, self.social_obj, yak_settings.NOTIFICATION_TYPES[0][0])
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(len(PushwooshClient.invoke.mock_calls), 2)

        # If allow_push is False and allow_email True, an email is sent and a push isn't
        setting.allow_email = True
        setting.allow_push = False
        setting.save()
        create_notification(self.receiver, self.reporter, self.social_obj, yak_settings.NOTIFICATION_TYPES[0][0])
        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue(len(PushwooshClient.invoke.mock_calls), 2)

    def test_can_only_see_own_notifications(self):
        create_notification(self.receiver, self.reporter, self.social_obj, yak_settings.NOTIFICATION_TYPES[0][0])
        create_notification(self.reporter, self.receiver, self.social_obj, yak_settings.NOTIFICATION_TYPES[0][0])
        url = reverse("notifications")
        response = self.assertSchemaGet(url, None, "$notificationResponse", self.receiver)
        self.assertEqual(response.data["count"], self.receiver.notifications_received.count())

    def test_comment_creates_notification(self):
        url = reverse("comments-list")
        content_type = ContentType.objects.get_for_model(Post)
        data = {
            "content_type": content_type.pk,
            "object_id": self.social_obj.pk,
            "description": "Yeti are cool"
        }
        self.assertSchemaPost(url, "$commentRequest", "$commentResponse", data, self.reporter)
        notification_count = Notification.objects.filter(user=self.social_obj.user,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(Post),
                                                         notification_type=Notification.TYPES.comment).count()
        self.assertEquals(notification_count, 1)

    def test_follow_creates_notification(self):
        url = reverse("follows-list")
        content_type = ContentType.objects.get_for_model(User)
        data = {
            "content_type": content_type.pk,
            "object_id": self.receiver.pk,
        }
        self.assertSchemaPost(url, "$followRequest", "$followResponse", data, self.reporter)
        notification_count = Notification.objects.filter(user=self.receiver,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(User),
                                                         notification_type=Notification.TYPES.follow).count()
        self.assertEquals(notification_count, 1)

    def test_share_creates_notification(self):
        url = reverse("shares-list")
        content_type = ContentType.objects.get_for_model(Post)
        data = {
            "content_type": content_type.pk,
            "object_id": self.social_obj.pk,
            "shared_with": [self.receiver.pk]
        }
        self.assertSchemaPost(url, "$shareRequest", "$shareResponse", data, self.reporter)
        notification_count = Notification.objects.filter(user=self.receiver,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(Post),
                                                         notification_type=Notification.TYPES.share).count()
        self.assertEquals(notification_count, 1)

    def test_like_creates_notification(self):
        url = reverse("likes-list")
        content_type = ContentType.objects.get_for_model(Post)
        data = {
            "content_type": content_type.pk,
            "object_id": self.social_obj.pk,
        }
        self.assertSchemaPost(url, "$likeRequest", "$likeResponse", data, self.reporter)
        notification_count = Notification.objects.filter(user=self.social_obj.user,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(Post),
                                                         notification_type=Notification.TYPES.like).count()
        self.assertEquals(notification_count, 1)

    def comment_mention_creates_notification(self):
        """
        User receives a notification when their username is @mentioned, even if they are not the owner of the post
        """
        url = reverse("comments-list")
        content_type = ContentType.objects.get_for_model(Post)
        data = {
            "content_type": content_type.pk,
            "object_id": PostFactory().pk,
            "description": "@{} look at my cool comment!".format(self.social_obj.user.username)
        }
        self.assertSchemaPost(url, "$commentRequest", "$commentResponse", data, self.reporter)
        notification_count = Notification.objects.filter(user=self.social_obj.user,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(Comment),
                                                         notification_type=Notification.TYPES.mention).count()

        self.assertEquals(notification_count, 1)


class NotificationSettingsTestCase(SchemaTestCase):
    def test_can_only_see_own_notification_settings(self):
        user = UserFactory()
        UserFactory()
        url = reverse("notification_settings-list")
        response = self.assertSchemaGet(url, None, "$notificationSettingResponse", user)
        self.assertEqual(response.data["count"], len(yak_settings.NOTIFICATION_TYPES))

    def test_can_only_update_own_settings(self):
        user = UserFactory()
        other_user = UserFactory()
        url = reverse("notification_settings-detail", args=[user.notification_settings.first().pk])
        data = {
            "allow_push": False,
            "allow_email": False
        }

        # A user can update their own settings
        response = self.assertSchemaPatch(url, "$notificationSettingRequest", "$notificationSettingResponse", data,
                                          user)
        self.assertEqual(response.data["id"], user.notification_settings.first().pk)
        self.assertFalse(response.data["allow_push"])
        self.assertFalse(response.data["allow_email"])

        # A user cannot update someone else's settings
        other_url = reverse("notification_settings-detail", args=[other_user.notification_settings.first().pk])
        self.assertSchemaPatch(other_url, "$notificationSettingRequest", "$notificationSettingResponse", data, user,
                               unauthorized=True)

    def test_settings_only_updated_or_listed(self):
        # Cannot be created or destroyed
        user = UserFactory()
        create_url = reverse("notification_settings-list")
        delete_url = reverse("notification_settings-detail", args=[user.notification_settings.first().pk])
        data = {
            "allow_push": False,
            "allow_email": False
        }
        self.assertSchemaPost(create_url, "$notificationSettingRequest", "$notificationSettingResponse", data, user,
                              unauthorized=True)
        self.assertSchemaDelete(delete_url, user, unauthorized=True)