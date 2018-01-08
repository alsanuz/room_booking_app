# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-07 13:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room_booking', '0003_auto_20180107_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='amount_people',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='booking',
            name='price',
            field=models.FloatField(blank=True, help_text='Total booking price'),
        ),
    ]
