# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-19 12:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0002_auto_20170619_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='logmodel',
            name='fajl_logova',
            field=models.CharField(default='Unknown', max_length=30),
        ),
    ]