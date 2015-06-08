# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_social_network', '0004_auto_20150313_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='related_tags',
            field=models.ManyToManyField(to='rest_social_network.Tag', blank=True),
        ),
    ]
