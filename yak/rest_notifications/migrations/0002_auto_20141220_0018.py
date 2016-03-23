# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
        ('rest_notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushwooshtoken',
            name='user',
            field=models.ForeignKey(related_name='pushwoosh_tokens', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationsetting',
            name='notification_type',
            field=models.ForeignKey(related_name='user_settings', to='rest_notifications.NotificationType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationsetting',
            name='user',
            field=models.ForeignKey(related_name='notification_settings', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='notificationsetting',
            unique_together=set([('notification_type', 'user')]),
        ),
        migrations.AddField(
            model_name='notification',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.ForeignKey(related_name='notifications', to='rest_notifications.NotificationType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='reporter',
            field=models.ForeignKey(related_name='notifications_sent', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(related_name='notifications_received', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
