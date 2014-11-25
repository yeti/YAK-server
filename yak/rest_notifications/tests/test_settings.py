from django.conf import settings
from django.core.urlresolvers import reverse
from yak.rest_core.test import SchemaTestCase
from yak.rest_user.test.factories import UserFactory


class NotificationSettingsTestCase(SchemaTestCase):
    def test_can_only_see_own_notification_settings(self):
        user = UserFactory()
        UserFactory()
        url = reverse("notification_settings-list")
        response = self.assertSchemaGet(url, None, "$notificationSettingResponse", user)
        self.assertEqual(response.data["count"], len(settings.NOTIFICATION_TYPES))

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
