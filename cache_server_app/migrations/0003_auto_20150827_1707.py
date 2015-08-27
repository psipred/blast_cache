# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cache_server_app', '0002_auto_20150826_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='expiry_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='file',
            name='file_location',
            field=models.CharField(db_index=True, max_length=256),
        ),
    ]
