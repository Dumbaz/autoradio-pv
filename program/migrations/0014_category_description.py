# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-12 15:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0013_category_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
    ]
