# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-01 12:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20180125_1834'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ongoinguserinfo',
            options={'verbose_name': 'مشخصات در دست تأیید', 'verbose_name_plural': 'مشخصات در دست تأیید'},
        ),
        migrations.AlterField(
            model_name='activity',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
