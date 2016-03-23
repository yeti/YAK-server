# -*- coding: utf-8 -*-


from django.db import models, migrations


def default_notification_types(apps, schema_editor):
    NotificationType = apps.get_model("rest_notifications", "NotificationType")
    NotificationType.objects.create(name="Comment", slug="comment", description="Someone commented on one of your posts")
    NotificationType.objects.create(name="Follow", slug="follow", description="Someone started following you")
    NotificationType.objects.create(name="Like", slug="like", description="Someone liked one of your posts")
    NotificationType.objects.create(name="Mention", slug="mention", description="Someone mentioned you")
    NotificationType.objects.create(name="Share", slug="share", description="Someone shared something with you")


class Migration(migrations.Migration):

    dependencies = [
        ('rest_notifications', '0002_auto_20141220_0018'),
    ]

    operations = [
        migrations.RunPython(default_notification_types),
    ]
