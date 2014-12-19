# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rest_social_network', '0002_auto_20141210_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(related_name='comments', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='flag',
            name='user',
            field=models.ForeignKey(related_name='flags', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(related_name='following', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='like',
            name='user',
            field=models.ForeignKey(related_name='likes', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='share',
            name='user',
            field=models.ForeignKey(related_name='shares', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
