# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cache_server_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='file_byte_location',
            new_name='file_byte_start',
        ),
        migrations.RemoveField(
            model_name='file',
            name='file',
        ),
        migrations.RemoveField(
            model_name='file',
            name='hit_count',
        ),
        migrations.AddField(
            model_name='file',
            name='file_byte_stop',
            field=models.IntegerField(default=0),
        ),
    ]
