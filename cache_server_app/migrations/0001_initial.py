# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cache_entry',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('uniprotID', models.CharField(unique=True, db_index=True, max_length=20)),
                ('md5', models.CharField(unique=True, db_index=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='file',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('accessed_count', models.IntegerField(default=0)),
                ('expiry_date', models.DateTimeField(auto_now_add=True)),
                ('file', models.CharField(unique=True, db_index=True, max_length=256)),
                ('file_location', models.CharField(unique=True, db_index=True, max_length=256)),
                ('file_type', models.IntegerField(default=2, choices=[(1, 'pssm'), (2, 'chk')])),
                ('file_byte_location', models.IntegerField(default=0)),
                ('hit_count', models.IntegerField(default=0)),
                ('blast_hits', models.IntegerField(default=0)),
                ('cache_entry', models.ForeignKey(to='cache_server_app.Cache_entry')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
