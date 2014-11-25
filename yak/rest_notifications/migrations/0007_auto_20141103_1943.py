# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_notifications', '0006_auto_20141027_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'follow.html'), (1, 'like.html'), (2, 'comment.html'), (3, 'mention.html'), (4, 'share.html'), (5, 'clip_used.html'), (6, 'submitted_clip.html'), (7, 'casting_call.html'), (8, 'submitted_your_clip.html')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notificationsetting',
            name='notification_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'follow.html'), (1, 'like.html'), (2, 'comment.html'), (3, 'mention.html'), (4, 'share.html'), (5, 'clip_used.html'), (6, 'submitted_clip.html'), (7, 'casting_call.html'), (8, 'submitted_your_clip.html')]),
            preserve_default=True,
        ),
    ]
