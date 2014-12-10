# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_notifications', '0007_auto_20141103_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'follow.html'), (1, 'like.html'), (2, 'comment.html'), (3, 'mention.html'), (4, 'share.html')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notificationsetting',
            name='notification_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'follow.html'), (1, 'like.html'), (2, 'comment.html'), (3, 'mention.html'), (4, 'share.html')]),
            preserve_default=True,
        ),
    ]
