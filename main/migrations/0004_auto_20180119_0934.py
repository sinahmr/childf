# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-01-19 09:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20171215_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='child',
            name='verified',
            field=models.NullBooleanField(default=None),
        ),
    ]
