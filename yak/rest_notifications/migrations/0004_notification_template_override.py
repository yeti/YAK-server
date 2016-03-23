# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_notifications', '0003_auto_20141220_0023'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='template_override',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
