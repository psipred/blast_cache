# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-26 14:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blast_cache_app', '0007_cache_entry_unique_hash'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cache_entry',
            old_name='unique_hash',
            new_name='settings_hash',
        ),
    ]