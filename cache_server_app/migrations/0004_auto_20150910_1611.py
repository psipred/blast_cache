# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cache_server_app', '0003_auto_20150827_1707'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='file',
            options={'get_latest_by': 'created'},
        ),
        migrations.AddField(
            model_name='file',
            name='runtime',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
