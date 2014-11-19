# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('notification_type', models.PositiveSmallIntegerField(choices=[(0, 'follow.html'), (1, 'like.html'), (2, 'comment.html'), (3, 'mention.html'), (4, 'shared_session.html'), (5, 'clip_used.html'), (6, 'submitted_clip.html')])),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('reporter', models.ForeignKey(related_name=b'reporter', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name=b'receiver', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NotificationSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('notification_type', models.PositiveSmallIntegerField(choices=[(0, 'follow.html'), (1, 'like.html'), (2, 'comment.html'), (3, 'mention.html'), (4, 'shared_session.html'), (5, 'clip_used.html'), (6, 'submitted_clip.html')])),
                ('allow_push', models.BooleanField(default=True)),
                ('allow_email', models.BooleanField(default=True)),
                ('user', models.ForeignKey(related_name=b'notification_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='notificationsetting',
            unique_together=set([('notification_type', 'user')]),
        ),
    ]
