# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_social', '0006_auto_20141016_1723'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='share',
            unique_together=set([('user', 'content_type', 'object_id')]),
        ),
    ]
