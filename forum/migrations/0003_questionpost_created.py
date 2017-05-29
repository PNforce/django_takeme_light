# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-29 08:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_remove_questionpost_pub_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionpost',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
