# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rest_notifications', '0005_pushwooshtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pushwooshtoken',
            name='user',
            field=models.ForeignKey(related_name='pushwoosh_tokens', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
