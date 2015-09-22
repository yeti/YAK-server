# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_social_network', '0003_auto_20150311_0123'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='share',
            unique_together=set([]),
        ),
    ]
