from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from rest_notifications.models import Notification, NotificationSetting

__author__ = 'rudolphmutter'


User = get_user_model()


class Command(BaseCommand):
    args = ''
    help = 'Creates missing notification settings for existing users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            for pk, name in Notification.TYPES:
                NotificationSetting.objects.get_or_create(notification_type=pk, user=user)