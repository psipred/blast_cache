# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cache_entry',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('uniprotID', models.CharField(max_length=20, unique=True, db_index=True)),
                ('md5', models.CharField(max_length=64, unique=True, db_index=True)),
                ('track_string', models.CharField(max_length=512, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('accessed_count', models.IntegerField(default=0)),
                ('expiry_date', models.DateTimeField()),
                ('file_location', models.CharField(max_length=256, db_index=True)),
                ('file_type', models.IntegerField(default=2, choices=[(1, 'pssm'), (2, 'chk')])),
                ('file_byte_start', models.IntegerField(default=0)),
                ('file_byte_stop', models.IntegerField(default=0)),
                ('blast_hits', models.IntegerField(default=0)),
                ('runtime', models.IntegerField(null=True, default=0)),
                ('cache_entry', models.ForeignKey(to='blast_cache_app.Cache_entry')),
            ],
            options={
                'get_latest_by': 'created',
            },
        ),
    ]
