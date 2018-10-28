from unittest import mock
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from rest_framework.reverse import reverse
from test_project import settings
from test_project.test_app.models import Post, Article
from test_project.test_app.tests.factories import PostFactory, UserFactory
from yak.rest_core.test import SchemaTestCase
from yak.rest_notifications.models import create_notification, Notification, NotificationSetting, NotificationType
from yak.rest_notifications.utils import send_email_notification, send_push_notification
from yak.settings import yak_settings


User = get_user_model()


def mockPushNotificationHandler(receiver, message, deep_link=None):
    return {"hello": "world"}


class NotificationsTestCase(SchemaTestCase):
    def setUp(self):
        super(NotificationsTestCase, self).setUp()
        self.social_obj = PostFactory()
        self.receiver = UserFactory()
        self.reporter = UserFactory()
        self.notification_type = NotificationType.objects.get(slug="comment")
        patcher = patch('yak.rest_notifications.utils.submit_to_pushwoosh')
        self.addCleanup(patcher.stop)
        self.mock_submit_to_pushwoosh = patcher.start()
        self.mock_submit_to_pushwoosh.return_value = {"status_code": 200}

    @mock.patch('pypushwoosh.client.PushwooshClient.invoke')
    def test_create_pushwoosh_token(self, mock_pushwoosh_client):
        mock_pushwoosh_client.return_value = {"status_code": 200}

        url = reverse("pushwoosh_token")
        data = {
            "token": "ABC123",
            "language": "en",
            "hwid": "XYZ456",
            "platform": "ios"
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

    @mock.patch('yak.rest_notifications.utils.yak_settings')
    def test_push_notification_sent_custom_handler(self, mock_settings):
        mock_settings.PUSH_NOTIFICATION_HANDLER = "test_project.test_app.tests." \
                                                  "test_notifications.mockPushNotificationHandler"
        message = "<h1>You have a notification!</h1>"
        response = send_push_notification(self.receiver, message)
        self.assertEqual(response["hello"], "world")

    def test_create_notification(self):
        notification_count = Notification.objects.count()

        # If receiver is the same as the reporter, a notification is not created
        create_notification(self.receiver, self.receiver, self.social_obj, self.notification_type)
        self.assertEqual(notification_count, Notification.objects.count())

        # If the receiver and reporter are different, a notification is created
        create_notification(self.receiver, self.reporter, self.social_obj, self.notification_type)
        self.assertEqual(notification_count + 1, Notification.objects.count())

    def test_correct_notification_type_sent(self):
        setting = NotificationSetting.objects.get(notification_type=self.notification_type,
                                                  user=self.receiver)

        # An email and a push are sent if allow_email and allow_push are True
        create_notification(self.receiver, self.reporter, self.social_obj, self.notification_type)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(len(self.mock_submit_to_pushwoosh.mock_calls), 1)

        # No new email is sent if allow_email is False
        setting.allow_email = False
        setting.save()
        create_notification(self.receiver, self.reporter, self.social_obj, self.notification_type)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(len(self.mock_submit_to_pushwoosh.mock_calls), 2)

        # If allow_push is False and allow_email True, an email is sent and a push isn't
        setting.allow_email = True
        setting.allow_push = False
        setting.save()
        create_notification(self.receiver, self.reporter, self.social_obj, self.notification_type)
        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue(len(self.mock_submit_to_pushwoosh.mock_calls), 2)

    def test_can_only_see_own_notifications(self):
        create_notification(self.receiver, self.reporter, self.social_obj, self.notification_type)
        create_notification(self.reporter, self.receiver, self.social_obj, self.notification_type)

        # Notifications serialized with thumbnails
        post = PostFactory()
        post.thumbnail = settings.PROJECT_ROOT + "/test_app/tests/img/yeti.jpg"
        post.save()
        create_notification(self.receiver, self.reporter, post, self.notification_type)

        url = reverse("notifications")
        response = self.assertSchemaGet(url, None, "$notificationResponse", self.receiver)
        self.assertEqual(response.data["count"], self.receiver.notifications_received.count())

    def test_content_object_serialization(self):
        """
        Content object is serialized using the standard serialization for that object type
        The `content_objectt` key is replaced for each different type of object serialized
        """
        article = Article.objects.create(title="Cool article")
        user = UserFactory()
        create_notification(user, self.reporter, self.social_obj, self.notification_type)
        create_notification(user, self.receiver, article, self.notification_type)
        url = reverse("notifications")
        response = self.assertSchemaGet(url, None, "$notificationResponse", user)
        self.assertEqual(response.data["count"], 2)
        self.assertIn("article", response.data["results"][0])
        self.assertNotIn("post", response.data["results"][0])
        self.assertIn("post", response.data["results"][1])
        self.assertNotIn("article", response.data["results"][1])

    def test_comment_creates_notification(self):
        url = reverse("comments-list")
        content_type = ContentType.objects.get_for_model(Post)
        data = {
            "content_type": content_type.pk,
            "object_id": self.social_obj.pk,
            "description": "Yeti are cool"
        }
        self.assertSchemaPost(url, "$commentRequest", "$commentResponse", data, self.reporter)
        comment_type = NotificationType.objects.get(slug="comment")
        notification_count = Notification.objects.filter(user=self.social_obj.user,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(Post),
                                                         notification_type=comment_type).count()
        self.assertEqual(notification_count, 1)

    def test_follow_creates_notification(self):
        url = reverse("follows-list")
        content_type = ContentType.objects.get_for_model(User)
        data = {
            "content_type": content_type.pk,
            "object_id": self.receiver.pk,
        }
        self.assertSchemaPost(url, "$followRequest", "$followResponse", data, self.reporter)
        follow_type = NotificationType.objects.get(slug="follow")
        notification_count = Notification.objects.filter(user=self.receiver,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(User),
                                                         notification_type=follow_type).count()
        self.assertEqual(notification_count, 1)

    def test_share_creates_notification(self):
        url = reverse("shares-list")
        content_type = ContentType.objects.get_for_model(Post)
        data = {
            "content_type": content_type.pk,
            "object_id": self.social_obj.pk,
            "shared_with": [self.receiver.pk]
        }
        self.assertSchemaPost(url, "$shareRequest", "$shareResponse", data, self.reporter)
        share_type = NotificationType.objects.get(slug="share")
        notification_count = Notification.objects.filter(user=self.receiver,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(Post),
                                                         notification_type=share_type).count()
        self.assertEqual(notification_count, 1)

    def test_like_creates_notification(self):
        url = reverse("likes-list")
        content_type = ContentType.objects.get_for_model(Post)
        data = {
            "content_type": content_type.pk,
            "object_id": self.social_obj.pk,
        }
        self.assertSchemaPost(url, "$likeRequest", "$likeResponse", data, self.reporter)
        like_type = NotificationType.objects.get(slug="like")
        notification_count = Notification.objects.filter(user=self.social_obj.user,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(Post),
                                                         notification_type=like_type).count()
        self.assertEqual(notification_count, 1)

    def test_comment_mention_creates_notification(self):
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
        mention_type = NotificationType.objects.get(slug="mention")
        notification_count = Notification.objects.filter(user=self.social_obj.user,
                                                         reporter=self.reporter,
                                                         content_type=ContentType.objects.get_for_model(Post),
                                                         notification_type=mention_type).count()

        self.assertEqual(notification_count, 1)

    def test_serialization_when_content_object_deleted(self):
        mention_notification = NotificationType.objects.get(slug="mention")
        content_type = ContentType.objects.get_for_model(Post)
        user = UserFactory()
        post = PostFactory(user=user)
        Notification.objects.create(notification_type=mention_notification, content_type=content_type,
                                    object_id=post.pk, user=user, reporter=self.reporter)
        post.delete()
        other_post = PostFactory(user=user)
        Notification.objects.create(notification_type=mention_notification, content_type=content_type,
                                    object_id=other_post.pk, user=user, reporter=self.reporter)
        url = reverse("notifications")
        response = self.assertSchemaGet(url, None, "$notificationResponse", user)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['post']['id'], other_post.pk)


class NotificationSettingsTestCase(SchemaTestCase):
    def test_can_only_see_own_notification_settings(self):
        user = UserFactory()
        UserFactory()
        url = reverse("notification_settings-list")
        response = self.assertSchemaGet(url, None, "$notificationSettingResponse", user)
        self.assertEqual(response.data["count"], NotificationType.objects.count())

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

    def test_bulk_update_notification_settings(self):
        url = reverse("notification_settings-list")
        user = UserFactory()
        bad_user = UserFactory()
        notification_settings = user.notification_settings.all()
        data = [
            {"id": notification_settings[0].pk, "allow_email": False},
            {"id": notification_settings[1].pk, "allow_email": False}
        ]
        # Can't update another user's notification settings
        self.assertSchemaPut(url, "$notificationSettingBulkRequest", "$notificationSettingResponse", data, bad_user,
                             forbidden=True)
        self.assertTrue(NotificationSetting.objects.get(pk=notification_settings[0].pk).allow_email)

        self.assertSchemaPut(url, "$notificationSettingBulkRequest", "$notificationSettingResponse", data, user)
        self.assertFalse(NotificationSetting.objects.get(pk=notification_settings[0].pk).allow_email)
