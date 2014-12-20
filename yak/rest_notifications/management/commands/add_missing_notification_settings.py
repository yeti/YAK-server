from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from yak.rest_notifications.models import NotificationSetting, NotificationType

__author__ = 'rudolphmutter'


User = get_user_model()


class Command(BaseCommand):
    args = ''
    help = 'Creates missing notification settings for existing users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            for notification_type in NotificationType.objects.all():
                NotificationSetting.objects.get_or_create(notification_type=notification_type, user=user)